# services/optimized_data_service.py
import pandas as pd
import geopandas as gpd
import streamlit as st
from typing import Dict, Optional, List, Any
from database.connection import get_engine
from utils.cache_imports_fix import (
    cache_electoral_data, cache_geographic_data, 
    cache_analytics_data, cache_user_data, get_cache_stats
)
from config.config_manager import config_manager
import logging

logger = logging.getLogger(__name__)

class OptimizedDataService:
    """Serviço de dados otimizado com cache estratificado"""
    
    def __init__(self):
        self.engine = get_engine()
        self._validate_connection()
    
    def _validate_connection(self):
        """Valida conexão com banco"""
        if not self.engine:
            raise ConnectionError("Falha na conexão com banco de dados")
    
    # DADOS ESTÁTICOS (raramente mudam) - Cache 1 dia
    @cache_electoral_data
    def get_municipalities_data(self) -> pd.DataFrame:
        """Carrega dados de municípios (estáticos)"""
        query = """
        SELECT DISTINCT m."Cod_IBGE", m."Nome_Municipio", m."Unidade_Geografica"
        FROM public.municipio m
        ORDER BY m."Nome_Municipio"
        """
        
        try:
            df = pd.read_sql(query, con=self.engine)
            return self._optimize_dataframe(df)
        except Exception as e:
            logger.error(f"Erro ao carregar municípios: {e}")
            raise
    
    @cache_electoral_data  
    def get_candidates_data(self) -> pd.DataFrame:
        """Carrega dados de candidatos (estáticos)"""
        query = """
        SELECT DISTINCT c."Num_Candidato", c."Nome_Urna", c."FK_Sigla_Partido"
        FROM public.candidato c
        WHERE c."Nome_Urna" IS NOT NULL
        ORDER BY c."Nome_Urna"
        """
        
        try:
            df = pd.read_sql(query, con=self.engine)
            return self._optimize_dataframe(df)
        except Exception as e:
            logger.error(f"Erro ao carregar candidatos: {e}")
            raise
    
    @cache_electoral_data
    def get_parties_data(self) -> pd.DataFrame:
        """Carrega dados de partidos (estáticos)"""
        query = """
        SELECT DISTINCT p."Sigla_Partido", p."Nome_Partido"
        FROM public.partido p
        WHERE p."Sigla_Partido" IS NOT NULL
        ORDER BY p."Sigla_Partido"
        """
        
        try:
            df = pd.read_sql(query, con=self.engine)
            return self._optimize_dataframe(df)
        except Exception as e:
            logger.error(f"Erro ao carregar partidos: {e}")
            raise
    
    # DADOS SEMI-ESTÁTICOS (mudam ocasionalmente) - Cache 1 hora
    @cache_electoral_data
    def get_voters_data(self) -> pd.DataFrame:
        """Carrega dados de eleitorado (semi-estáticos)"""
        query = """
        SELECT 
            v."FK_Cod_Municipio",
            v."Eleitores_Aptos",
            v."Votos_Validos_Municipio",
            v."Votos_Brancos",
            v."Votos_Nulos_Urna",
            v."Votos_Anulados",
            v."Abstencao",
            ROUND(
                (v."Votos_Validos_Municipio"::float / NULLIF(v."Eleitores_Aptos", 0)) * 100, 
                2
            ) as "Percentual_Comparecimento"
        FROM public.manifestacao_eleitorado_municipio v
        WHERE v."Eleitores_Aptos" > 0
        """
        
        try:
            df = pd.read_sql(query, con=self.engine)
            return self._optimize_dataframe(df)
        except Exception as e:
            logger.error(f"Erro ao carregar dados de eleitores: {e}")
            raise
    
    @cache_electoral_data
    def get_support_data(self) -> pd.DataFrame:
        """Carrega dados de apoio político (semi-estáticos)"""
        query = """
        SELECT 
            a."FK_Cod_Municipio",
            a."FK_Num_Candidato", 
            a."Status_Apoio"
        FROM public.apoio_prefeito_candidato a
        WHERE a."Status_Apoio" IS NOT NULL
        """
        
        try:
            df = pd.read_sql(query, con=self.engine)
            return self._optimize_dataframe(df)
        except Exception as e:
            logger.error(f"Erro ao carregar dados de apoio: {e}")
            raise
    
    # DADOS DINÂMICOS (mudam com frequência) - Cache 15 min
    @cache_analytics_data
    def get_votes_summary(self) -> pd.DataFrame:
        """Carrega resumo de votos (dinâmico)"""
        query = """
        SELECT 
            v."FK_Cod_Municipio",
            v."FK_Num_Candidato",
            SUM(v."Votos_Nominais_Candidato") as "Total_Votos",
            COUNT(DISTINCT v."Zona") as "Zonas_Eleitorais"
        FROM public.votacao_candidato_municipio_zona v
        WHERE v."Votos_Nominais_Candidato" > 0
        GROUP BY v."FK_Cod_Municipio", v."FK_Num_Candidato"
        ORDER BY "Total_Votos" DESC
        """
        
        try:
            df = pd.read_sql(query, con=self.engine)
            return self._optimize_dataframe(df)
        except Exception as e:
            logger.error(f"Erro ao carregar resumo de votos: {e}")
            raise
    
    @cache_analytics_data
    def get_party_votes_summary(self) -> pd.DataFrame:
        """Carrega resumo de votos por partido (dinâmico)"""
        query = """
        SELECT 
            p."FK_Cod_Municipio",
            p."FK_Sigla_Partido",
            SUM(p."Votos_Nominais_Partido") as "Total_Votos_Partido"
        FROM public.votos_partido_municipio p
        WHERE p."Votos_Nominais_Partido" > 0
        GROUP BY p."FK_Cod_Municipio", p."FK_Sigla_Partido"
        ORDER BY "Total_Votos_Partido" DESC
        """
        
        try:
            df = pd.read_sql(query, con=self.engine)
            return self._optimize_dataframe(df)
        except Exception as e:
            logger.error(f"Erro ao carregar votos por partido: {e}")
            raise
    
    # QUERIES ESPECÍFICAS OTIMIZADAS
    def get_candidate_performance(self, candidate_id: int) -> pd.DataFrame:
        """Performance otimizada para candidato específico"""
        query = """
        WITH candidate_votes AS (
            SELECT 
                v."FK_Cod_Municipio",
                SUM(v."Votos_Nominais_Candidato") as "Votos_Candidato"
            FROM public.votacao_candidato_municipio_zona v
            WHERE v."FK_Num_Candidato" = %(candidate_id)s
            GROUP BY v."FK_Cod_Municipio"
        ),
        municipality_totals AS (
            SELECT 
                e."FK_Cod_Municipio",
                e."Votos_Validos_Municipio",
                e."Eleitores_Aptos"
            FROM public.manifestacao_eleitorado_municipio e
        )
        SELECT 
            cv."FK_Cod_Municipio" as "Cod_IBGE",
            cv."Votos_Candidato",
            mt."Votos_Validos_Municipio",
            mt."Eleitores_Aptos",
            ROUND(
                (cv."Votos_Candidato"::float / NULLIF(mt."Votos_Validos_Municipio", 0)) * 100, 
                2
            ) as "Percentual_Votos_Validos"
        FROM candidate_votes cv
        JOIN municipality_totals mt ON cv."FK_Cod_Municipio" = mt."FK_Cod_Municipio"
        ORDER BY "Percentual_Votos_Validos" DESC
        """
        
        try:
            df = pd.read_sql(query, con=self.engine, params={"candidate_id": candidate_id})
            result = self._optimize_dataframe(df)
            return result
        except Exception as e:
            logger.error(f"Erro ao carregar performance do candidato {candidate_id}: {e}")
            raise
    
    def get_party_performance(self, party_code: str) -> pd.DataFrame:
        """Performance otimizada para partido específico"""
        cache_key = f"party_performance_{party_code}"
        
        query = """
        WITH party_votes AS (
            SELECT 
                p."FK_Cod_Municipio",
                SUM(p."Votos_Nominais_Partido") as "Votos_Partido"
            FROM public.votos_partido_municipio p
            WHERE p."FK_Sigla_Partido" = %(party_code)s
            GROUP BY p."FK_Cod_Municipio"
        ),
        municipality_totals AS (
            SELECT 
                e."FK_Cod_Municipio",
                e."Votos_Validos_Municipio",
                e."Eleitores_Aptos"
            FROM public.manifestacao_eleitorado_municipio e
        )
        SELECT 
            pv."FK_Cod_Municipio" as "Cod_IBGE",
            pv."Votos_Partido",
            mt."Votos_Validos_Municipio", 
            mt."Eleitores_Aptos",
            %(party_code)s as "Sigla_Partido",
            ROUND(
                (pv."Votos_Partido"::float / NULLIF(mt."Votos_Validos_Municipio", 0)) * 100,
                2
            ) as "Percentual_Votos_Validos"
        FROM party_votes pv
        JOIN municipality_totals mt ON pv."FK_Cod_Municipio" = mt."FK_Cod_Municipio"
        ORDER BY "Percentual_Votos_Validos" DESC
        """
        
        try:
            df = pd.read_sql(query, con=self.engine, params={"party_code": party_code})
            return self._optimize_dataframe(df)
        except Exception as e:
            logger.error(f"Erro ao carregar performance do partido {party_code}: {e}")
            raise
    
    # DADOS GEOGRÁFICOS (cache de longa duração)
    @cache_geographic_data
    def get_geographic_data(self, shapefile_path: str = None) -> gpd.GeoDataFrame:
        """Carrega dados geográficos com cache otimizado"""
        if shapefile_path is None:
            shapefile_path = config_manager.data.shapefile_path
        
        try:
            gdf = gpd.read_file(shapefile_path)
            
            # Padronizações
            if "codigo_ibg" in gdf.columns:
                gdf = gdf.rename(columns={"codigo_ibg": "Cod_IBGE"})
            
            # Otimiza projeção
            if gdf.crs is None or gdf.crs.to_epsg() != 4326:
                gdf = gdf.to_crs(epsg=4326)
            
            # Simplifica geometrias para melhor performance
            gdf["geometry"] = gdf["geometry"].simplify(0.001)
            
            return gdf
            
        except Exception as e:
            logger.error(f"Erro ao carregar shapefile: {e}")
            raise
    
    # MÉTODOS DE AGREGAÇÃO EFICIENTES
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Resumo otimizado para dashboard"""
        try:
            # Usa dados já em cache quando possível
            voters_df = self.get_voters_data()
            candidates_df = self.get_candidates_data()
            votes_summary = self.get_votes_summary()
            
            summary = {
                "total_municipalities": len(voters_df),
                "total_candidates": len(candidates_df),
                "total_votes": votes_summary["Total_Votos"].sum(),
                "total_eligible_voters": voters_df["Eleitores_Aptos"].sum(),
                "average_turnout": voters_df["Percentual_Comparecimento"].mean().round(2),
                "municipalities_with_data": len(votes_summary["FK_Cod_Municipio"].unique())
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Erro ao calcular resumo do dashboard: {e}")
            return {}
    
    def get_electoral_data_bundle(self) -> Dict[str, pd.DataFrame]:
        """Bundle otimizado de todos os dados eleitorais"""
        return {
            "municipalities": self.get_municipalities_data(),
            "candidates": self.get_candidates_data(),
            "parties": self.get_parties_data(),
            "voters": self.get_voters_data(),
            "support": self.get_support_data(),
            "votes_summary": self.get_votes_summary(),
            "party_votes_summary": self.get_party_votes_summary()
        }
    
    # OTIMIZAÇÕES DE DATAFRAME
    def _optimize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Otimizações avançadas de memória"""
        original_size = df.memory_usage(deep=True).sum()
        
        # Converte strings repetitivas para category
        for col in df.select_dtypes(include=['object']):
            unique_ratio = df[col].nunique() / len(df)
            if unique_ratio < 0.5:  # Menos de 50% de valores únicos
                df[col] = df[col].astype('category')
        
        # Otimiza tipos numéricos
        for col in df.select_dtypes(include=['int64']):
            col_min, col_max = df[col].min(), df[col].max()
            if col_min >= -128 and col_max <= 127:
                df[col] = df[col].astype('int8')
            elif col_min >= -32768 and col_max <= 32767:
                df[col] = df[col].astype('int16')
            elif col_min >= -2147483648 and col_max <= 2147483647:
                df[col] = df[col].astype('int32')
        
        # Otimiza floats
        for col in df.select_dtypes(include=['float64']):
            df[col] = pd.to_numeric(df[col], downcast='float')
        
        # Log da otimização
        optimized_size = df.memory_usage(deep=True).sum()
        reduction = (1 - optimized_size/original_size) * 100
        logger.info(f"DataFrame otimizado: {reduction:.1f}% redução de memória")
        
        return df
    
    # MÉTODOS DE CONTROLE DE CACHE
    def clear_all_cache(self):
        """Limpa todo o cache"""
        from utils.cache import clear_all_cache
        clear_all_cache()
        logger.info("Cache completamente limpo")
    
    def clear_dynamic_cache(self):
        """Limpa apenas cache dinâmico"""
        from utils.cache import clear_cache_by_pattern
        clear_cache_by_pattern("analytics")
        logger.info("Cache dinâmico limpo")
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas detalhadas do cache"""
        return get_cache_stats()

# Instância global otimizada
optimized_data_service = OptimizedDataService()