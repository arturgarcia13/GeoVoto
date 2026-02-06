from typing import Dict, Any
import pandas as pd
import geopandas as gpd
import logging

from geovoto.infrastructure.database.connection import get_engine
from geovoto.infrastructure.caching import cache_static, cache_semi_static, cache_dynamic
from geovoto.config.settings import settings
from geovoto.utils.dataframe import optimize_dataframe

logger = logging.getLogger(__name__)

class DataService:
    """Service for loading and caching electoral data."""
    
    def __init__(self):
        # Engine is retrieved lazily or via dependency injection if needed
        pass

    @property
    def engine(self):
        return get_engine()

    @cache_static
    def get_municipalities_data(self) -> pd.DataFrame:
        query = """
        SELECT DISTINCT m."Cod_IBGE", m."Nome_Municipio", m."Unidade_Geografica"
        FROM public.municipio m
        ORDER BY m."Nome_Municipio"
        """
        return optimize_dataframe(pd.read_sql(query, con=self.engine))

    @cache_static
    def get_candidates_data(self) -> pd.DataFrame:
        query = """
        SELECT DISTINCT c."Num_Candidato", c."Nome_Urna", c."FK_Sigla_Partido"
        FROM public.candidato c
        WHERE c."Nome_Urna" IS NOT NULL
        ORDER BY c."Nome_Urna"
        """
        return optimize_dataframe(pd.read_sql(query, con=self.engine))

    @cache_static
    def get_parties_data(self) -> pd.DataFrame:
        query = """
        SELECT DISTINCT p."Sigla_Partido", p."Nome_Partido"
        FROM public.partido p
        WHERE p."Sigla_Partido" IS NOT NULL
        ORDER BY p."Sigla_Partido"
        """
        return optimize_dataframe(pd.read_sql(query, con=self.engine))

    @cache_semi_static
    def get_voters_data(self) -> pd.DataFrame:
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
        return optimize_dataframe(pd.read_sql(query, con=self.engine))

    @cache_dynamic
    def get_votes_summary(self) -> pd.DataFrame:
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
        return optimize_dataframe(pd.read_sql(query, con=self.engine))

    @cache_dynamic
    def get_party_votes_summary(self) -> pd.DataFrame:
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
        return optimize_dataframe(pd.read_sql(query, con=self.engine))

    def get_candidate_performance(self, candidate_id: int) -> pd.DataFrame:
        # Not cached as params vary widely, or could use dynamic cache with key builder
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
        return optimize_dataframe(pd.read_sql(query, con=self.engine, params={"candidate_id": candidate_id}))

    @cache_static
    def get_geographic_data(self, shapefile_path: str = None) -> gpd.GeoDataFrame:
        path = shapefile_path or settings.data.shapefile_path
        gdf = gpd.read_file(path)
        
        if "codigo_ibg" in gdf.columns:
            gdf = gdf.rename(columns={"codigo_ibg": "Cod_IBGE"})
        
        if gdf.crs is None or gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs(epsg=4326)
            
        gdf["geometry"] = gdf["geometry"].simplify(0.001)
        return gdf

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Calculates dashboard summary metrics efficiently."""
        try:
            voters_df = self.get_voters_data()
            candidates_df = self.get_candidates_data()
            votes_summary = self.get_votes_summary()
            
            return {
                "total_municipalities": len(voters_df),
                "total_candidates": len(candidates_df),
                "total_votes": votes_summary["Total_Votos"].sum(),
                "total_eligible_voters": voters_df["Eleitores_Aptos"].sum(),
                "average_turnout": voters_df["Percentual_Comparecimento"].mean().round(2),
                "municipalities_with_data": len(votes_summary["FK_Cod_Municipio"].unique())
            }
        except Exception as e:
            logger.error(f"Error calculating dashboard summary: {e}")
            return {}
