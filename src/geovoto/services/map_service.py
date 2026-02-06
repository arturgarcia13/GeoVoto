from typing import Dict, Any, List
import pandas as pd
import geopandas as gpd
import numpy as np

from geovoto.core.exceptions import ValidationError

class MapService:
    """Service for processing geographic data and maps."""

    def process_candidate_data(
        self,
        votes_df: pd.DataFrame,
        voters_df: pd.DataFrame,
        candidate_id: int
    ) -> pd.DataFrame:
        """Processes voting data for a specific candidate."""
        candidate_votes = (
            votes_df[votes_df["FK_Num_Candidato"] == candidate_id]
            .groupby("FK_Cod_Municipio", as_index=False)
            .agg({"Votos_Nominais_Candidato": "sum"})
            .rename(columns={
                "FK_Cod_Municipio": "Cod_IBGE",
                "Votos_Nominais_Candidato": "Votos_Candidato"
            })
        )
        
        voters_renamed = voters_df.rename(columns={"FK_Cod_Municipio": "Cod_IBGE"})
        merged_data = pd.merge(candidate_votes, voters_renamed, on="Cod_IBGE", how="left")
        return self._calculate_candidate_metrics(merged_data)

    def process_party_data(
        self,
        party_votes_df: pd.DataFrame,
        voters_df: pd.DataFrame,
        party_code: str
    ) -> pd.DataFrame:
        """Processes voting data for a specific party."""
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
        
        voters_renamed = voters_df.rename(columns={"FK_Cod_Municipio": "Cod_IBGE"})
        merged_data = pd.merge(party_votes, voters_renamed, on="Cod_IBGE", how="left")
        return self._calculate_party_metrics(merged_data)

    def merge_with_geographic_data(
        self,
        gdf_municipalities: gpd.GeoDataFrame,
        electoral_data: pd.DataFrame
    ) -> gpd.GeoDataFrame:
        """Merges electoral data with geographic shapefile data."""
        geo_columns = ["Cod_IBGE", "Municipio", "geometry"]
        available_columns = [col for col in geo_columns if col in gdf_municipalities.columns]
        
        if "geometry" not in available_columns:
            raise ValidationError("Column 'geometry' not found in shapefile")
        
        gdf_final = gdf_municipalities[available_columns].merge(
            electoral_data, 
            on="Cod_IBGE", 
            how="right"
        )
        
        return gpd.GeoDataFrame(gdf_final, geometry="geometry", crs=gdf_municipalities.crs)

    def _calculate_candidate_metrics(self, data: pd.DataFrame) -> pd.DataFrame:
        data["Votos_Validos_Municipio"] = data["Votos_Validos_Municipio"].fillna(1)
        data["Votos_Candidato"] = data["Votos_Candidato"].fillna(0)
        
        data["Percentual_Votos_Validos"] = (
            100 * data["Votos_Candidato"] / data["Votos_Validos_Municipio"]
        ).round(2)
        
        data["Percentual_Municipio_Total"] = data["Percentual_Votos_Validos"]
        return data

    def _calculate_party_metrics(self, data: pd.DataFrame) -> pd.DataFrame:
        data["Votos_Validos_Municipio"] = data["Votos_Validos_Municipio"].fillna(1)
        data["Votos_Partido"] = data["Votos_Partido"].fillna(0)
        
        data["Percentual_Votos_Validos"] = (
            100 * data["Votos_Partido"] / data["Votos_Validos_Municipio"]
        ).round(2)
        
        data["Percentual_Municipio_Total"] = data["Percentual_Votos_Validos"]
        return data

    def create_choropleth_data(
        self,
        gdf: gpd.GeoDataFrame,
        value_column: str,
        bins: int = 5
    ) -> Dict[str, Any]:
        """Prepares data for choropleth map."""
        data_values = gdf[value_column].dropna()
        
        if len(data_values) == 0:
            return {"error": "No valid data for map"}
            
        quantiles = np.linspace(0, 1, bins + 1)
        breaks = data_values.quantile(quantiles).tolist()
        breaks = sorted(list(set(breaks)))
        
        return {
            "breaks": breaks,
            "min_value": float(data_values.min()),
            "max_value": float(data_values.max()),
            "mean_value": float(data_values.mean()),
            "color_column": value_column,
            "data_count": len(data_values)
        }
