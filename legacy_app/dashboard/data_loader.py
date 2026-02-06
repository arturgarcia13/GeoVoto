# app/dashboard/data_loader.py - Atualizado para novo sistema de cache

import pandas as pd
import streamlit as st
from sqlalchemy import inspect
from utils.cache import cached_dashboard_data
from config.config_manager import config_manager

@cached_dashboard_data(show_spinner="📊 Carregando dados do dashboard...")
def load_data(_engine):
    """Carrega dados para o dashboard com cache otimizado"""
    if _engine is None:
        return pd.DataFrame()

    try:
        with _engine.connect() as conn:
            insp = inspect(_engine)
            # Pega todos os nomes de tabelas
            tabelas = insp.get_table_names()
            
            dfs = {}
            # Loop para criar DataFrames com nomes iguais ao das tabelas
            for tabela in tabelas:
                if tabela == "perfil_eleitorado_local":
                    continue
                # Carregar uma tabela do banco local
                dfs[tabela] = pd.read_sql(f'SELECT * FROM {tabela}', con=conn)
                
                # Otimiza DataFrame se configurado
                if config_manager.data.auto_optimize_dtypes:
                    dfs[tabela] = _optimize_dataframe(dfs[tabela])
                    
            return dfs
    except Exception as e:
        st.error(f"Erro ao carregar os dados do dashboard")
        st.error(str(e))
        return {}

def _optimize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Otimiza DataFrame para reduzir uso de memória"""
    try:
        original_size = df.memory_usage(deep=True).sum()
        
        # Converte object para category quando apropriado
        for col in df.select_dtypes(include=['object']):
            if df[col].nunique() / len(df) < 0.5:  # Menos que 50% de valores únicos
                df[col] = df[col].astype('category')
        
        # Converte int64 para int32 quando possível
        for col in df.select_dtypes(include=['int64']):
            col_min, col_max = df[col].min(), df[col].max()
            if col_min >= -2147483648 and col_max <= 2147483647:
                df[col] = df[col].astype('int32')
        
        # Converte float64 para float32 quando possível  
        for col in df.select_dtypes(include=['float64']):
            df[col] = pd.to_numeric(df[col], downcast='float')
        
        # Log da otimização se em debug
        if config_manager.is_debug_enabled():
            optimized_size = df.memory_usage(deep=True).sum()
            reduction = (1 - optimized_size/original_size) * 100
            print(f"DataFrame otimizado: {reduction:.1f}% redução de memória")
        
        return df
    except Exception as e:
        if config_manager.is_debug_enabled():
            print(f"Erro na otimização do DataFrame: {e}")
        return df

def get_cache_info():
    """Retorna informações sobre o cache do dashboard"""
    from utils.cache import get_cache_stats
    
    stats = get_cache_stats()
    return {
        "dashboard_cache_active": True,
        "ttl_seconds": config_manager.cache.semi_static_ttl,
        "total_cache_items": stats.get("total_cached_items", 0),
        "cache_size_mb": stats.get("cache_size_mb", 0),
        "auto_optimization": config_manager.data.auto_optimize_dtypes
    }

def clear_dashboard_cache():
    """Limpa cache específico do dashboard"""
    from utils.cache import clear_cache_by_pattern
    clear_cache_by_pattern("dashboard")
    st.success("Cache do dashboard limpo!")

def validate_data_integrity(dfs: dict) -> dict:
    """Valida integridade dos dados carregados"""
    validation_report = {
        "tables_loaded": len(dfs),
        "total_rows": sum(len(df) for df in dfs.values()),
        "issues": []
    }
    
    # Verifica tabelas essenciais
    essential_tables = [
        "votacao_candidato_municipio_zona",
        "manifestacao_eleitorado_municipio", 
        "candidato",
        "municipio"
    ]
    
    for table in essential_tables:
        if table not in dfs:
            validation_report["issues"].append(f"Tabela essencial '{table}' não encontrada")
        elif dfs[table].empty:
            validation_report["issues"].append(f"Tabela '{table}' está vazia")
    
    # Verifica consistência de dados
    if "candidato" in dfs and "votacao_candidato_municipio_zona" in dfs:
        candidates_in_votes = set(dfs["votacao_candidato_municipio_zona"]["FK_Num_Candidato"].unique())
        candidates_in_table = set(dfs["candidato"]["Num_Candidato"].unique())
        
        missing_candidates = candidates_in_votes - candidates_in_table
        if missing_candidates:
            validation_report["issues"].append(
                f"Candidatos em votos mas não na tabela candidato: {len(missing_candidates)}"
            )
    
    validation_report["data_quality"] = "good" if len(validation_report["issues"]) == 0 else "issues_found"
    
    return validation_report