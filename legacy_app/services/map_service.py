# services/map_service.py
import pandas as pd
import geopandas as gpd
from typing import Optional, Dict, Any
import streamlit as st

class MapService:
    """Serviço para processamento de dados geográficos e mapas"""
    
    def process_candidate_data(
        self,
        votes_df: pd.DataFrame,
        voters_df: pd.DataFrame,
        candidate_id: int
    ) -> pd.DataFrame:
        """Processa dados de votação para um candidato específico"""
        
        # Agrupa votos do candidato por município
        candidate_votes = (
            votes_df[votes_df["FK_Num_Candidato"] == candidate_id]
            .groupby("FK_Cod_Municipio", as_index=False)
            .agg({"Votos_Nominais_Candidato": "sum"})
            .rename(columns={
                "FK_Cod_Municipio": "Cod_IBGE",
                "Votos_Nominais_Candidato": "Votos_Candidato"
            })
        )
        
        # Merge com dados de eleitorado
        voters_renamed = voters_df.rename(columns={"FK_Cod_Municipio": "Cod_IBGE"})
        merged_data = pd.merge(candidate_votes, voters_renamed, on="Cod_IBGE", how="left")
        
        # Calcula métricas derivadas
        merged_data = self._calculate_candidate_metrics(merged_data)
        
        return merged_data
    
    def process_party_data(
        self,
        party_votes_df: pd.DataFrame,
        voters_df: pd.DataFrame,
        party_code: str
    ) -> pd.DataFrame:
        """Processa dados de votação para um partido específico"""
        
        # Filtra votos do partido
        party_votes = (
            party_votes_df[party_votes_df["FK_Sigla_Partido"] == party_code]
            .groupby("FK_Cod_Municipio", as_index=False)
            .agg({"Votos_Nominais_Partido": "sum"})
            .rename(columns={
                "FK_Cod_Municipio": "Cod_IBGE",
                "Votos_Nominais_Partido": "Votos_Partido"
            })
        )
        party_votes["Sigla_Partido"] = party_code
        
        # Merge com dados de eleitorado
        voters_renamed = voters_df.rename(columns={"FK_Cod_Municipio": "Cod_IBGE"})
        merged_data = pd.merge(party_votes, voters_renamed, on="Cod_IBGE", how="left")
        
        # Calcula métricas derivadas
        merged_data = self._calculate_party_metrics(merged_data)
        
        return merged_data
    
    def merge_with_geographic_data(
        self,
        gdf_municipalities: gpd.GeoDataFrame,
        electoral_data: pd.DataFrame
    ) -> gpd.GeoDataFrame:
        """Combina dados eleitorais com dados geográficos"""
        
        # Seleciona colunas necessárias do shapefile
        geo_columns = ["Cod_IBGE", "Municipio", "geometry"]
        available_columns = [col for col in geo_columns if col in gdf_municipalities.columns]
        
        if "geometry" not in available_columns:
            raise ValueError("Coluna 'geometry' não encontrada no shapefile")
        
        # Merge dos dados
        gdf_final = gdf_municipalities[available_columns].merge(
            electoral_data, 
            on="Cod_IBGE", 
            how="right"
        )
        
        # Garante que é um GeoDataFrame
        gdf_final = gpd.GeoDataFrame(gdf_final, geometry="geometry", crs=gdf_municipalities.crs)
        
        return gdf_final
    
    def _calculate_candidate_metrics(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calcula métricas específicas para candidatos"""
        
        # Evita divisão por zero
        data["Votos_Validos_Municipio"] = data["Votos_Validos_Municipio"].fillna(1)
        data["Votos_Candidato"] = data["Votos_Candidato"].fillna(0)
        
        # Percentual de votos válidos
        data["Percentual_Votos_Validos"] = (
            100 * data["Votos_Candidato"] / data["Votos_Validos_Municipio"]
        ).round(2)
        
        # Percentual total do município (mesma métrica neste contexto)
        data["Percentual_Municipio_Total"] = data["Percentual_Votos_Validos"]
        
        return data
    
    def _calculate_party_metrics(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calcula métricas específicas para partidos"""
        
        # Evita divisão por zero
        data["Votos_Validos_Municipio"] = data["Votos_Validos_Municipio"].fillna(1)
        data["Votos_Partido"] = data["Votos_Partido"].fillna(0)
        
        # Percentual de votos válidos
        data["Percentual_Votos_Validos"] = (
            100 * data["Votos_Partido"] / data["Votos_Validos_Municipio"]
        ).round(2)
        
        # Percentual total do município  
        data["Percentual_Municipio_Total"] = data["Percentual_Votos_Validos"]
        
        return data
    
    def calculate_geographic_statistics(
        self,
        gdf: gpd.GeoDataFrame,
        value_column: str
    ) -> Dict[str, Any]:
        """Calcula estatísticas geográficas básicas"""
        
        if value_column not in gdf.columns:
            return {}
        
        # Remove valores nulos para cálculos precisos
        valid_data = gdf[value_column].dropna()
        
        if len(valid_data) == 0:
            return {"error": "Nenhum dado válido encontrado"}
        
        stats = {
            "total_value": valid_data.sum(),
            "mean_value": valid_data.mean(),
            "median_value": valid_data.median(),
            "std_value": valid_data.std(),
            "min_value": valid_data.min(),
            "max_value": valid_data.max(),
            "municipalities_count": len(gdf),
            "municipalities_with_data": len(valid_data),
            "municipalities_without_data": len(gdf) - len(valid_data),
            "data_coverage_percent": (len(valid_data) / len(gdf) * 100) if len(gdf) > 0 else 0
        }
        
        return {k: round(v, 2) if isinstance(v, float) else v for k, v in stats.items()}
    
    def get_top_performing_regions(
        self,
        gdf: gpd.GeoDataFrame,
        value_column: str,
        top_n: int = 10
    ) -> gpd.GeoDataFrame:
        """Retorna top N regiões por performance"""
        
        if value_column not in gdf.columns:
            return gpd.GeoDataFrame()
        
        return gdf.nlargest(top_n, value_column)
    
    def create_choropleth_data(
        self,
        gdf: gpd.GeoDataFrame,
        value_column: str,
        bins: int = 5
    ) -> Dict[str, Any]:
        """Prepara dados para mapa coroplético"""
        
        # Calcula quebras naturais ou quantis
        try:
            import numpy as np
            data_values = gdf[value_column].dropna()
            
            if len(data_values) == 0:
                return {"error": "Sem dados válidos para o mapa"}
            
            # Usa quantis para divisão mais equilibrada
            quantiles = np.linspace(0, 1, bins + 1)
            breaks = data_values.quantile(quantiles).tolist()
            
            # Remove duplicatas mantendo ordem
            breaks = sorted(list(set(breaks)))
            
            choropleth_data = {
                "breaks": breaks,
                "min_value": float(data_values.min()),
                "max_value": float(data_values.max()),
                "mean_value": float(data_values.mean()),
                "color_column": value_column,
                "data_count": len(data_values)
            }
            
            return choropleth_data
            
        except Exception as e:
            st.error(f"Erro ao preparar dados do mapa: {e}")
            return {"error": str(e)}