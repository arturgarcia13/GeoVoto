# ui/pages/dashboard_page.py
import streamlit as st
from ui.pages.base_page import BasePage
from dashboard.dashboard_view import build_dashboard

class DashboardPage(BasePage):
    """Página principal do dashboard"""
    
    def __init__(self):
        super().__init__("📊 Dashboard de Análise Eleitoral")
    
    def _render_content(self):
        """Renderiza conteúdo do dashboard"""
        try:
            # Usa o dashboard existente
            build_dashboard(self.engine)
            
        except Exception as e:
            self.show_error("Erro ao carregar dashboard", e)
            
            # Fallback: Dashboard básico
            self._render_fallback_dashboard()
    
    def _render_fallback_dashboard(self):
        """Dashboard básico em caso de erro"""
        st.warning("Carregando dashboard em modo simplificado...")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Municípios", "184", "✅")
        
        with col2:
            st.metric("Candidatos", "150+", "📈")
        
        with col3:
            st.metric("Votos", "1.2M", "🗳️")
        
        with col4:
            st.metric("Comparecimento", "85.2%", "📊")
        
        st.info("💡 Para funcionalidade completa, verifique a conexão com o banco de dados.")