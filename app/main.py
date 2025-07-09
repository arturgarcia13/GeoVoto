import streamlit as st
from utils.ui import configurar_interface
from app.login import login_screen
from dashboard.db_connection import get_engine
from dashboard.dashboard_view import build_dashboard

# Conexão com o banco
engine = get_engine()

# Configurações de layout, título, etc.
configurar_interface()

# --- Controle de fluxo do app ---
if st.session_state.get("logged_in", False):
    if st.session_state["user_type"] == "admin":
        st.sidebar.success("Administrador")
    else:
        st.sidebar.info("Usuário")
    build_dashboard(engine)  # Só chama aqui, dentro do if
else:
    login_screen()