# ui/pages/strategic_page.py
import streamlit as st
import pandas as pd
from dataclasses import dataclass
from typing import Dict, Any
from ui.pages.base_page import BasePage
from services.data_service import DataService
from services.strategic_service import StrategicService
from ui.components.analysis_tables import AnalysisTables
from config.config_manager import data_config

@dataclass
class StrategicWeights:
    """Classe para pesos da análise estratégica"""
    electorate: int = 30
    penetration: int = 25
    potential: int = 25
    efficiency: int = 20
    
    def validate(self) -> bool:
        """Valida se os pesos somam 100%"""
        return sum([self.electorate, self.penetration, self.potential, self.efficiency]) == 100
    
    def to_dict(self) -> Dict[str, int]:
        """Converte para dicionário"""
        return {
            "electorate": self.electorate,
            "penetration": self.penetration, 
            "potential": self.potential,
            "efficiency": self.efficiency
        }

class StrategicPage(BasePage):
    """Página de análise estratégica"""
    
    def __init__(self):
        super().__init__("📊 Análise Estratégica")
        self.data_service = DataService()
        self.strategic_service = StrategicService()
        self.analysis_tables = AnalysisTables()
    
    def _render_content(self):
        """Renderiza conteúdo da análise estratégica"""
        
        # Renderiza controles de peso na sidebar
        weights = self._render_weights_controls()
        if not weights.validate():
            st.warning("⚠️ A soma dos pesos deve ser 100%. Ajuste para continuar.")
            return
        
        # Carrega dados necessários
        with self.show_loading("Carregando dados estratégicos..."):
            data = self._load_strategic_data()
            if not data:
                return
        
        # Processa análise estratégica
        strategic_data = self._calculate_strategic_analysis(data, weights)
        
        # Renderiza resultados
        self._render_strategic_results(strategic_data)
    
    def _render_weights_controls(self) -> StrategicWeights:
        """Renderiza controles de peso na sidebar"""
        with st.sidebar:
            st.markdown("### ⚙️ Ajuste de Pesos Estratégicos")
            
            peso_eleitorado = st.slider(
                "Peso – Tamanho do Eleitorado", 
                0, 100, 30,
                help="Importância do tamanho do eleitorado municipal"
            )
            peso_penetracao = st.slider(
                "Peso – Espaço para Crescimento", 
                0, 100, 25,
                help="Importância do potencial de crescimento da penetração"
            )
            peso_potencial = st.slider(
                "Peso – Potencial Absoluto", 
                0, 100, 25,
                help="Importância do potencial absoluto de votos"
            )
            peso_eficiencia = st.slider(
                "Peso – Eficiência da Campanha", 
                0, 100, 20,
                help="Importância da eficiência da campanha local"
            )
            
            return StrategicWeights(
                electorate=peso_eleitorado,
                penetration=peso_penetracao,
                potential=peso_potencial,
                efficiency=peso_eficiencia
            )
    
    def _load_strategic_data(self) -> Dict[str, pd.DataFrame]:
        """Carrega dados necessários para análise estratégica"""
        try:
            # Dados eleitorais básicos
            electoral_data = self.data_service.get_electoral_data()
            
            # Dados de apoio político
            support_query = "SELECT * FROM apoio_prefeito_candidato"
            support_data = pd.read_sql(support_query, con=self.engine)
            
            return {
                **electoral_data,
                "support": support_data
            }
            
        except Exception as e:
            self.show_error("Erro ao carregar dados estratégicos", e)
            return {}
    
    def _calculate_strategic_analysis(
        self, 
        data: Dict[str, pd.DataFrame], 
        weights: StrategicWeights
    ) -> pd.DataFrame:
        """Calcula análise estratégica completa"""
        
        try:
            # Usa candidato configurável ou padrão
            candidate_id = data_config.default_candidate_id
            
            # Processa dados estratégicos
            strategic_df = self.strategic_service.calculate_strategic_data(
                votes_df=data["votes"],
                voters_df=data["voters"],
                support_df=data["support"],
                candidate_id=candidate_id
            )
            
            # Calcula score estratégico
            strategic_df = self.strategic_service.calculate_strategic_score(
                strategic_df, 
                weights
            )
            
            return strategic_df
            
        except Exception as e:
            self.show_error("Erro ao calcular análise estratégica", e)
            return pd.DataFrame()
    
    def _render_strategic_results(self, strategic_data: pd.DataFrame):
        """Renderiza resultados da análise estratégica"""
        
        if strategic_data.empty:
            st.warning("Nenhum dado estratégico disponível")
            return
        
        # Métricas resumidas
        self._render_strategic_metrics(strategic_data)
        
        # Tabelas de top municípios
        self._render_top_strategic_municipalities(strategic_data)
        
        # Análise detalhada
        self._render_detailed_analysis(strategic_data)
        
        # Placeholder para mapa futuro
        st.info("🗺️ Mapa estratégico será implementado na próxima fase")
    
    def _render_strategic_metrics(self, data: pd.DataFrame):
        """Renderiza métricas estratégicas resumidas"""
        st.markdown("### 📊 Métricas Estratégicas Gerais")
        
        metrics = {
            "municipalities": {
                "label": "🏛️ Municípios Analisados",
                "value": f"{len(data):,}",
                "delta": None
            },
            "total_votes": {
                "label": "🗳️ Total de Votos",
                "value": f"{data['Votos_Validos_Candidato'].sum():,}",
                "delta": None
            },
            "avg_penetration": {
                "label": "📈 Penetração Média",
                "value": f"{data['Penetracao_Atual'].mean():.2f}%",
                "delta": None
            },
            "top_efficiency": {
                "label": "⚡ Melhor Eficiência",
                "value": f"{data['Eficiencia_Campanha'].max():.2f}%",
                "delta": None
            }
        }
        
        self.analysis_tables.render_metric_cards(metrics, columns=4)
    
    def _render_top_strategic_municipalities(self, data: pd.DataFrame):
        """Renderiza tabelas de top municípios estratégicos"""
        
        columns_config = {
            "Cod_IBGE": "Código IBGE",
            "Votos_Validos_Candidato": "Votos do Candidato",
            "Penetracao_Atual": "Penetração Atual (%)",
            "Potencial_Crescimento": "Potencial de Crescimento",
            "Eficiencia_Campanha": "Eficiência da Campanha (%)",
            "Score_Estrategico": "Score Estratégico",
            "Posicao_Ranking": "Posição no Ranking"
        }
        
        # Top municípios estratégicos
        st.markdown("### 🥇 Top Municípios Estratégicos")
        with st.expander("Ver detalhes dos top 10"):
            top_strategic = data.sort_values("Score_Estrategico", ascending=False).head(10)
            st.dataframe(
                top_strategic.rename(columns=columns_config),
                use_container_width=True,
                height=300,
                hide_index=True
            )
        
        # Municípios com menor prioridade
        st.markdown("### 📉 Municípios com Menor Prioridade Estratégica") 
        with st.expander("Ver detalhes dos 10 com menor prioridade"):
            bottom_strategic = data.sort_values("Score_Estrategico", ascending=True).head(10)
            st.dataframe(
                bottom_strategic.rename(columns=columns_config),
                use_container_width=True,
                height=300,
                hide_index=True
            )
    
    def _render_detailed_analysis(self, data: pd.DataFrame):
        """Renderiza análise detalhada com filtros interativos"""
        
        st.markdown("### 🔍 Análise Detalhada por Município")
        
        # Filtros interativos
        filter_columns = ["Status_Apoio"] if "Status_Apoio" in data.columns else []
        display_columns = [
            "Cod_IBGE", "Votos_Validos_Candidato", "Penetracao_Atual", 
            "Potencial_Crescimento", "Eficiencia_Campanha", "Score_Estrategico"
        ]
        
        # Filtra colunas que existem nos dados
        available_display_columns = [col for col in display_columns if col in data.columns]
        
        if filter_columns and available_display_columns:
            self.analysis_tables.render_interactive_filter_table(
                data,
                filter_columns=filter_columns,
                display_columns=available_display_columns,
                title="Análise por Filtros"
            )
        
        # Estatísticas descritivas
        numeric_columns = [
            "Votos_Validos_Candidato", "Penetracao_Atual", 
            "Potencial_Crescimento", "Eficiencia_Campanha", "Score_Estrategico"
        ]
        available_numeric_columns = [col for col in numeric_columns if col in data.columns]
        
        if available_numeric_columns:
            self.analysis_tables.render_summary_statistics(
                data,
                available_numeric_columns,
                "📊 Estatísticas da Análise Estratégica"
            )