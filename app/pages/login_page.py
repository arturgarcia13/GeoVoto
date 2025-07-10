import streamlit as st
from ui.login import login_screen, login_scam
from ui.register import register_user


def page_login():
    # Inicializa variáveis de estado, se necessário
    if "register_mode" not in st.session_state:
        st.session_state["register_mode"] = False

    # Lê o token da URL (modo compatível)
    query_params = st.query_params
    token = query_params.get("token", [None])

    # Se token válido, faz login automático
    if token and login_scam(token):
        st.session_state["logged_in"] = True
        return  # Sai da função, login bem-sucedido

    # Caso esteja no modo de cadastro
    if st.session_state["register_mode"]:
        st.title("Cadastro de Novo Usuário")
        register_user()
        if st.button("Voltar para o login"):
            st.session_state["register_mode"] = False
        return

    # Tela de login padrão
    login_screen()

    if st.button("Cadastrar Novo Usuário"):
        st.session_state["register_mode"] = True
