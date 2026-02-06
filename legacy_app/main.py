# main.py - Versão Refatorada (Fase 1)
import streamlit as st
from config.settings import app_config
from core.session_manager import SessionManager
from core.auth_manager import AuthManager
from ui.layouts.main_layout import MainLayout
from ui.layouts.login_layout import LoginLayout

def main():
    """Ponto de entrada principal da aplicação"""
    # Configuração da página
    st.set_page_config(
        page_title=app_config.app_name,
        page_icon=app_config.app_icon,
        initial_sidebar_state=app_config.initial_sidebar_state,
        layout=app_config.page_layout
    )
    
    # Inicialização dos gerenciadores
    session_manager = SessionManager()
    auth_manager = AuthManager()
    
    # Inicializar estado da sessão
    session_manager.initialize()
    
    # Verificar autenticação
    if not auth_manager.is_authenticated():
        LoginLayout().render()
    else:
        MainLayout().render()

if __name__ == "__main__":
    main()