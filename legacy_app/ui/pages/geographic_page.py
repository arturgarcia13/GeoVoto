# ui/pages/geographic_page.py
import streamlit as st
import pandas as pd
import geopandas as gpd
from ui.pages.base_page import BasePage
from services.optimized_data_service import optimized_data_service
from services.map_service import MapService
from ui.components.analysis_tables import AnalysisTables
from ui.map_utils import gerar_mapa
from config.config_manager import data_config

class GeographicPage(BasePage):
    """Página de análise geográfica"""
    
    def __init__(self):
        super().__init__("🗺️ Análise Geográfica")
        self.data_service = DataService()
        self.map_service = MapService()
        self.analysis_tables = AnalysisTables()
        self.map_component = MapComponent()
    
    def _render_content(self):
        """Renderiza conteúdo da página geográfica"""
        # Seletor de tipo de visualização
        visualization_type = self._render_visualization_selector()
        
        # Carrega dados necessários
        with self.show_loading("Carregando dados..."):
            data = self._load_required_data()
            if not data:
                return
        
        # Renderiza análise baseada no tipo selecionado
        if visualization_type == "Votos por Candidato":
            self._render_candidate_analysis(data)
        else:
            self._render_party_analysis(data)
    
    def _render_visualization_selector(self) -> str:
        """Renderiza seletor de tipo de visualização"""
        return st.radio(
            "Selecione o tipo de visualização",
            ["Votos por Candidato", "Votos por Partido"],
            index=0,
            horizontal=True
        )
    
    def _load_required_data(self) -> dict:
        """Carrega todos os dados necessários"""
        try:
            # Dados eleitorais
            electoral_data = self.data_service.get_electoral_data()
            
            # Dados geográficos
            geographic_data = self.data_service.get_geographic_data()
            
            return {
                **electoral_data,
                "geographic": geographic_data
            }
        except Exception as e:
            self.show_error("Erro ao carregar dados", e)
            return {}
    
    def _render_candidate_analysis(self, data: dict):
        """Renderiza análise por candidato"""
        # Seletor de candidato
        candidate_info = self._render_candidate_selector(data["candidates"])
        if not candidate_info:
            return
        
        candidate_name, candidate_id = candidate_info
        
        # Processa dados do candidato
        with self.show_loading(f"Processando dados de {candidate_name}..."):
            processed_data = self.map_service.process_candidate_data(
                data["votes"], 
                data["voters"], 
                candidate_id
            )
            
            # Merge com dados geográficos
            geo_data = self.map_service.merge_with_geographic_data(
                data["geographic"], 
                processed_data
            )
        
        # Renderiza análises
        self._render_municipality_highlights(
            processed_data, 
            "candidato",
            candidate_name
        )
        
        # Renderiza mapa usando função existente
        st.subheader(f"🗺️ Distribuição Geográfica - {candidate_name}")
        gerar_mapa(geo_data, tipo="candidato")
    
    def _render_party_analysis(self, data: dict):
        """Renderiza análise por partido"""
        # Seletor de partido
        party = self._render_party_selector(data["party_votes"])
        if not party:
            return
        
        # Processa dados do partido
        with self.show_loading(f"Processando dados do {party}..."):
            processed_data = self.map_service.process_party_data(
                data["party_votes"],
                data["voters"],
                party
            )
            
            # Merge com dados geográficos
            geo_data = self.map_service.merge_with_geographic_data(
                data["geographic"],
                processed_data
            )
        
        # Renderiza análises
        self._render_municipality_highlights(
            processed_data,
            "partido", 
            party
        )
        
        # Renderiza mapa usando função existente
        st.subheader(f"🗺️ Distribuição Geográfica - {party}")
        gerar_mapa(geo_data, tipo="partido", sigla=party)
    
    def _render_candidate_selector(self, candidates_df: pd.DataFrame) -> tuple:
        """Renderiza seletor de candidato"""
        candidate_name = st.selectbox(
            "🧑‍💼 Selecione um candidato",
            candidates_df["Nome_Urna"].tolist()
        )
        
        candidate_id = candidates_df[
            candidates_df["Nome_Urna"] == candidate_name
        ]["Num_Candidato"].values[0]
        
        return candidate_name, candidate_id
    
    def _render_party_selector(self, party_votes_df: pd.DataFrame) -> str:
        """Renderiza seletor de partido"""
        available_parties = sorted(
            party_votes_df["FK_Sigla_Partido"].dropna().unique().tolist()
        )
        
        return st.selectbox(
            "🏛️ Selecione um partido",
            available_parties
        )
    
    def _render_municipality_highlights(self, data: pd.DataFrame, analysis_type: str, entity_name: str):
        """Renderiza destaques por município"""
        st.markdown("### 📊 Destaques por Município")
        
        # Configurações baseadas no tipo
        config = self._get_analysis_config(analysis_type)
        
        col_higher, col_lower = st.columns(2)
        
        with col_higher:
            self.analysis_tables.render_top_municipalities(
                data,
                title=f"🔺 Municípios com Maior % - {entity_name}",
                config=config,
                ascending=False
            )
        
        with col_lower:
            self.analysis_tables.render_top_municipalities(
                data,
                title=f"🔻 Municípios com Menor % - {entity_name}",
                config=config,
                ascending=True
            )
    
    def _render_map_section(self, geo_data: gpd.GeoDataFrame, map_type: str, entity_name: str):
        """Renderiza seção do mapa"""
        st.subheader(f"🗺️ Distribuição Geográfica - {entity_name}")
        
        self.map_component.render_choropleth_map(
            geo_data,
            map_type=map_type,
            entity_name=entity_name
        )
    
    def _get_analysis_config(self, analysis_type: str) -> dict:
        """Retorna configuração de análise baseada no tipo"""
        configs = {
            "candidato": {
                "columns": ["Municipio", "Votos_Candidato", "Votos_Validos_Municipio", "Percentual_Municipio_Total"],
                "labels": {
                    "Municipio": "Município",
                    "Votos_Candidato": "Votos no Candidato", 
                    "Votos_Validos_Municipio": "Votos Válidos do Município",
                    "Percentual_Municipio_Total": "% do Candidato no Município"
                },
                "sort_column": "Percentual_Municipio_Total"
            },
            "partido": {
                "columns": ["Municipio", "Votos_Partido", "Votos_Validos_Municipio", "Percentual_Municipio_Total"],
                "labels": {
                    "Municipio": "Município",
                    "Votos_Partido": "Votos no Partido",
                    "Votos_Validos_Municipio": "Votos Válidos do Município", 
                    "Percentual_Municipio_Total": "% do Partido no Município"
                },
                "sort_column": "Percentual_Municipio_Total"
            }
        }
        return configs.get(analysis_type, configs["candidato"])