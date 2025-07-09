import streamlit as st
from app.ui.login import login_screen
from app.ui.register import register_user

st.set_page_config(page_title="GeoVoto", page_icon="🗳️")

st.sidebar.title("🧭 Navegação")
pagina = st.sidebar.selectbox("Ir para", ["Login", "Cadastro"])

if pagina == "Login":
    login_screen()
elif pagina == "Cadastro":
    register_user()
