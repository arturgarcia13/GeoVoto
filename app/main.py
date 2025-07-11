import streamlit as st

from ui.dashboard import page_dashboard
from ui.login_page import page_login
from ui.app_page import page_app
from config.settings import AppConfig

# Configuração da página
st.set_page_config(
    page_title=AppConfig.app_name, 
    page_icon=AppConfig.app_icon, 
    initial_sidebar_state=AppConfig.initial_sidebar_state, 
    layout= AppConfig.page_layout
    )

# Inicializa estado de login se necessário
def initialize_session_state():
    """Inicializa todas as variáveis de estado necessárias"""
    default_states = {
        "logged_in": False,
        "token_processed": False,
        "register_mode": False
    }
        
    for key, default_value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def do_logout():
    st.query_params.clear()  # limpa os parâmetros da URL

    
    # Limpa o session_state
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    # Reinsere os padrões
    initialize_session_state()

    st.rerun()

initialize_session_state()
# Verifica se o usuário está logado
if not st.session_state["logged_in"]:
    col1 , col2, col3 = st.columns([0.5, 1, 0.5])
    with col2:
        tab1, tab2 = st.tabs(["Intro", "Login"])
        with tab1:
            page_app()
        
        with tab2:
            page_login()

else:

    with st.sidebar:
        st.sidebar.success(f"Logado como: {st.session_state["nome"]}")
        st.sidebar.title("Navegação")
        if st.button("Logout"):
            do_logout()
    
    tab1, tab2 = st.tabs(["Dashboard", "Análise Geográfica"])
    
    with tab1:
        # Mostra o dashboard
        page_dashboard()
    with tab2:
        # Mostra o Mapa Político
        pass
