# app/ui/login.py

import streamlit as st
import uuid
from app.database.json_user_store import get_user_by_email, update_user_token, validate_token

def login_screen():
    st.title("Login via Magic Link")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_type = None
        st.session_state.user_email = None

    token = st.query_params.get("token", [None])[0]

    if token:
        user = validate_token(token)
        if user:
            st.session_state.logged_in = True
            st.session_state.user_type = user["tipo"]
            st.session_state.user_email = user["email"]
            st.success(f"Bem-vindo, {user['nome']} ({user['tipo']})")
        else:
            st.error("Token inválido ou expirado.")
        return

    email = st.text_input("Digite seu e-mail para receber o link mágico")

    if st.button("Enviar link"):
        user = get_user_by_email(email)
        if user:
            token = str(uuid.uuid4())
            update_user_token(email, token)
            magic_link = f"/?token={token}"
            st.success("Link gerado com sucesso!")
            st.markdown(f"[Clique aqui para logar]({magic_link})")
        else:
            st.error("Usuário não encontrado")