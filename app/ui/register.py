import streamlit as st
from database.queries import get_user_by_email, create_user

@st.dialog("📋 Cadastro de Novo Usuário")
def register_user():
    st.markdown("Preencha os dados abaixo para cadastrar um novo usuário:")

    with st.form("form_cadastro", clear_on_submit=True):
        nome = st.text_input("Nome completo")
        email = st.text_input("E-mail")
        tipo = "usuário"  # fixo por enquanto
        submit = st.form_submit_button("✅ Cadastrar Usuário", use_container_width=True)

        if submit:
            if not nome or not email:
                st.error("⚠️ Preencha todos os campos.")
                return

            if get_user_by_email(email):
                st.warning("Este e-mail já está cadastrado.")
                return

            if create_user(nome, email, tipo, token=""):
                st.success("🎉 Usuário cadastrado com sucesso!")
            else:
                st.error("❌ Erro ao cadastrar usuário.")