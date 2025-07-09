import streamlit as st
from ui.login import login_screen
from ui.register import register_user
from ui.interface import configurar_interface
from dashboard.dashboard_view import build_dashboard
from database.connection import get_engine

st.set_page_config(page_title="GeoVoto", page_icon="🗳️")

# --- Barra lateral de navegação ---
st.sidebar.title("🧭 Navegação")

if not st.session_state.get("logged_in", False):
    pagina = st.sidebar.selectbox("Ir para", ["Login", "Cadastro"])
    
    if pagina == "Login":
        login_screen()
    elif pagina == "Cadastro":
        register_user()
else:
    engine = get_engine()

    if st.session_state["user_type"] == "admin":
        st.sidebar.success("Administrador")
    else:
        st.sidebar.info("Usuário")

    build_dashboard(engine)
