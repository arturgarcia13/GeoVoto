# app/ui/register.py
import streamlit as st
import json
from pathlib import Path

USERS_PATH = Path("app/data/usuarios.json")

def load_users():
    if USERS_PATH.exists():
        with open(USERS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_users(users):
    with open(USERS_PATH, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def user_exists(email):
    users = load_users()
    return any(user["email"] == email for user in users)

def register_user():
    st.title("📋 Cadastro de Novo Usuário")

    nome = st.text_input("Nome completo")
    email = st.text_input("E-mail")
    tipo = st.selectbox("Tipo de usuário", ["user", "admin"])

    if st.button("Cadastrar"):
        if not nome or not email:
            st.error("Preencha todos os campos.")
            return

        if user_exists(email):
            st.warning("Este e-mail já está cadastrado.")
            return

        novo_usuario = {
            "nome": nome,
            "email": email,
            "tipo": tipo,
            "token": ""
        }

        users = load_users()
        users.append(novo_usuario)
        save_users(users)
        st.success("Usuário cadastrado com sucesso!")
