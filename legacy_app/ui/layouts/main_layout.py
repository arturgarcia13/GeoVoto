# ui/layouts/main_layout.py
import streamlit as st
from typing import List
from core.auth_manager import AuthManager
from ui.pages.dashboard_page import DashboardPage
from ui.pages.geographic_page import GeographicPage
from ui.pages.strategic_page import StrategicPage
from ui.pages.users_page import UsersPage

class MainLayout:
    """Layout principal da aplicação para usuários autenticados"""
    
    def __init__(self):
        self.auth_manager = AuthManager()
        self.pages = {
            "Dashboard": DashboardPage(),
            "Análise Geográfica": GeographicPage(), 
            "Análise Estratégica": StrategicPage(),
            "Usuários": UsersPage()
        }
    
    def render(self):
        """Renderiza layout principal"""
        self._render_sidebar()
        self._render_main_content()
    
    def _render_sidebar(self):
        """Renderiza barra lateral com info do usuário"""
        with st.sidebar:
            user_info = self.auth_manager.get_current_user()
            st.success(f"Logado como: {user_info['name']}")
            st.title("Navegação")
            
            if st.button("Logout", type="secondary"):
                self.auth_manager.logout()
    
    def _render_main_content(self):
        """Renderiza conteúdo principal com tabs"""
        available_tabs = self._get_available_tabs()
        
        # Cria tabs baseado no tipo de usuário
        tabs = st.tabs(available_tabs)
        
        # Renderiza cada página em sua respectiva tab
        for i, tab_name in enumerate(available_tabs):
            with tabs[i]:
                page = self.pages.get(tab_name)
                if page:
                    page.render()
                else:
                    st.error(f"Página '{tab_name}' não encontrada")
    
    def _get_available_tabs(self) -> List[str]:
        """Retorna tabs disponíveis baseado no tipo de usuário"""
        base_tabs = ["Dashboard", "Análise Geográfica", "Análise Estratégica"]
        
        if self.auth_manager.is_admin():
            return base_tabs + ["Usuários"]
        
        return base_tabs

class TabRenderer:
    """Classe auxiliar para renderização consistente de tabs"""
    
    @staticmethod
    def render_with_error_handling(page_func, page_name: str):
        """Renderiza página com tratamento de erro consistente"""
        try:
            page_func()
        except Exception as e:
            st.error(f"Erro ao carregar {page_name}: {str(e)}")
            st.exception(e)  # Para debug - remover em produção