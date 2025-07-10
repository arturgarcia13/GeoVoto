import streamlit as st

from ui.interface import configurar_interface
from pages.dashboard import page_dashboard
from database.connection import get_engine
from pages.login_page import page_login

# Configuração da página
st.set_page_config(page_title="GeoVoto", page_icon="🗳️")

# Inicializa estado de login se necessário
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Barra lateral
st.sidebar.title("🧭 Navegação")

# Verifica se o usuário está logado
if not st.session_state["logged_in"]:
    page_login()
else:
    engine = get_engine()

    # Mostra o dashboard
    page_dashboard(engine)
