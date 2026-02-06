# services/data_service.py
import pandas as pd
import geopandas as gpd
import streamlit as st
from typing import Dict, Optional
from database.connection import get_engine
from config.settings import app_config
from utils.cache import cached_query, cached_geodata

class DataService:
    """Serviço centralizado para carregamento e cache de dados"""
    
    def __init__(self):
        self.engine = get_engine()
    
    @cached_query
    def get_electoral_data(self, _engine=None) -> Dict[str, pd.DataFrame]:
        """Carrega todos os dados eleitorais com cache otimizado"""
        if _engine is None:
            _engine = self.engine
            
        queries = {
            "votes": "SELECT * FROM votacao_candidato_municipio_zona",
            "voters": "SELECT * FROM manifestacao_eleitorado_municipio", 
            "candidates": 'SELECT DISTINCT "Num_Candidato", "Nome_Urna" FROM candidato ORDER BY "Nome_Urna"',
            "party_votes": "SELECT * FROM votos_partido_municipio",
            "support": "SELECT * FROM apoio_prefeito_candidato"
        }
        
        data = {}
        for key, query in queries.items():
            try:
                df = pd.read_sql(query, con=_engine)
                # Otimizações básicas de memória
                data[key] = self._optimize_dataframe(df)
            except Exception as e:
                st.error(f"Erro ao carregar {key}: {e}")
                raise
        
        return data
    
    @cached_geodata  
    def get_geographic_data(self, shapefile_path: str = None) -> gpd.GeoDataFrame:
        """Carrega dados geográficos com cache de longa duração"""
        if shapefile_path is None:
            shapefile_path = app_config.shapefile_path
            
        try:
            gdf = gpd.read_file(shapefile_path)
            # Padroniza nome da coluna
            if "codigo_ibg" in gdf.columns:
                gdf = gdf.rename(columns={"codigo_ibg": "Cod_IBGE"})
            
            # Garante projeção correta para mapas web
            if gdf.crs is None or gdf.crs.to_epsg() != 4326:
                gdf = gdf.to_crs(epsg=4326)
                
            return gdf
            
        except Exception as e:
            st.error(f"Erro ao carregar shapefile: {e}")
            raise
    
    @cached_query
    def get_candidate_votes(self, _engine, candidate_id: int) -> pd.DataFrame:
        """Carrega votos específicos de um candidato"""
        query = """
        SELECT FK_Cod_Municipio, SUM(Votos_Nominais_Candidato) as Votos_Candidato
        FROM votacao_candidato_municipio_zona 
        WHERE FK_Num_Candidato = %s
        GROUP BY FK_Cod_Municipio
        """
        
        try:
            df = pd.read_sql(query, con=_engine, params=[candidate_id])
            return df.rename(columns={"FK_Cod_Municipio": "Cod_IBGE"})
        except Exception as e:
            st.error(f"Erro ao carregar votos do candidato {candidate_id}: {e}")
            raise
    
    @cached_query  
    def get_party_votes(self, _engine, party_code: str) -> pd.DataFrame:
        """Carrega votos específicos de um partido"""
        query = """
        SELECT FK_Cod_Municipio, SUM(Votos_Nominais_Partido) as Votos_Partido
        FROM votos_partido_municipio
        WHERE FK_Sigla_Partido = %s
        GROUP BY FK_Cod_Municipio
        """
        
        try:
            df = pd.read_sql(query, con=_engine, params=[party_code])
            df["Sigla_Partido"] = party_code
            return df.rename(columns={"FK_Cod_Municipio": "Cod_IBGE"})
        except Exception as e:
            st.error(f"Erro ao carregar votos do partido {party_code}: {e}")
            raise
    
    def _optimize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Otimiza DataFrame para reduzir uso de memória"""
        # Converte object para category quando apropriado
        for col in df.select_dtypes(include=['object']):
            if df[col].nunique() / len(df) < 0.5:  # Menos que 50% de valores únicos
                df[col] = df[col].astype('category')
        
        # Converte int64 para int32 quando possível
        for col in df.select_dtypes(include=['int64']):
            if df[col].min() > -2147483648 and df[col].max() < 2147483647:
                df[col] = df[col].astype('int32')
        
        # Converte float64 para float32 quando possível  
        for col in df.select_dtypes(include=['float64']):
            df[col] = pd.to_numeric(df[col], downcast='float')
            
        return df
    
    def get_dashboard_summary(self) -> Dict[str, any]:
        """Retorna dados resumidos para dashboard"""
        try:
            data = self.get_electoral_data()
            
            summary = {
                "total_municipalities": len(data["voters"]),
                "total_candidates": len(data["candidates"]),
                "total_votes": data["votes"]["Votos_Nominais_Candidato"].sum(),
                "total_eligible_voters": data["voters"]["Eleitores_Aptos"].sum(),
                "turnout_rate": (
                    data["voters"]["Votos_Validos_Municipio"].sum() / 
                    data["voters"]["Eleitores_Aptos"].sum() * 100
                ).round(2)
            }
            
            return summary
            
        except Exception as e:
            st.error(f"Erro ao calcular resumo: {e}")
            return {}

# Instância global do serviço
data_service = DataService()