import streamlit as st
from ui.interface import configurar_interface
from app.ui.login import login_screen
from dashboard.dashboard_view import build_dashboard
from database.connection import get_engine

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