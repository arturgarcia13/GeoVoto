# ui/pages/base_page.py
import streamlit as st
from abc import ABC, abstractmethod
from typing import Optional
from database.connection import get_engine
from utils.error_handler import handle_page_errors

class BasePage(ABC):
    """Classe base para todas as páginas da aplicação"""
    
    def __init__(self, title: str):
        self.title = title
        self.engine = get_engine()
    
    @handle_page_errors
    def render(self):
        """Método principal para renderizar a página"""
        if self.title:
            st.title(self.title)
        
        # Verificação de conexão com banco
        if not self.engine:
            st.error("❌ Erro de conexão com banco de dados")
            st.stop()
        
        # Renderiza conteúdo específico da página
        self._render_content()
    
    @abstractmethod
    def _render_content(self):
        """Método abstrato para conteúdo específico da página"""
        pass
    
    def show_loading(self, message: str = "Carregando..."):
        """Helper para mostrar loading"""
        return st.spinner(message)
    
    def show_error(self, message: str, exception: Optional[Exception] = None):
        """Helper para mostrar erros de forma consistente"""
        st.error(f"❌ {message}")
        if exception and st.secrets.get("DEBUG", False):
            st.exception(exception)
    
    def show_success(self, message: str):
        """Helper para mostrar mensagens de sucesso"""
        st.success(f"✅ {message}")
    
    def show_info(self, message: str):
        """Helper para mostrar informações"""
        st.info(f"ℹ️ {message}")