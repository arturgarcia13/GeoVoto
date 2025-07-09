import streamlit as st
from ui.interface import configurar_interface
from ui.login import login_screen
from dashboard.dashboard_view import build_dashboard
from database.connection import get_engine

# Conexão com o banco
engine = get_engine()

# Configurações de layout, título, etc.
# configurar_interface()
def configurar_interface():
    st.set_page_config(
        page_title="Dashboard de Análise Eleitoral",
        page_icon="📊",
        layout="wide"
    )

# --- Controle de fluxo do app ---
if st.session_state.get("logged_in", False):
    if st.session_state["user_type"] == "admin":
        st.sidebar.success("Administrador")
    else:
        st.sidebar.info("Usuário")
    build_dashboard(engine)  # Só chama aqui, dentro do if
else:
    login_screen()