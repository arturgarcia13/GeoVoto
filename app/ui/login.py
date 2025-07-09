# app/ui/login.py

import streamlit as st
import uuid
import smtplib
from email.message import EmailMessage
from database.json_user_store import (
    get_user_by_email,
    update_user_token,
    validate_token,
)
from streamlit_extras.switch_page_button import switch_page


def enviar_link_por_email(remetente_email, remetente_nome, senha_app, destinatario, token):
    link = f"http://localhost:8501/?token={token}"
    
    msg = EmailMessage()
    msg["Subject"] = "Seu link mágico de acesso"
    msg["From"] = f"{remetente_nome} <{remetente_email}>"
    msg["To"] = destinatario
    msg.set_content(
        f"Olá,\n\nClique no link abaixo para acessar o sistema:\n\n{link}\n\n"
        f"Abraços,\n{remetente_nome}"
    )

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(remetente_email, senha_app)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Erro ao enviar e-mail: {e}")
        return False


def login_screen():
    st.title("🔐 Login via Link Mágico")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_type = None
        st.session_state.user_email = None

    # Verifica se existe token na URL
    query_params = st.query_params
    token = query_params["token"] if "token" in query_params else None

    if token:
        if not token or len(token) < 20:
            st.error("Token ausente ou malformado.")
            return
        user = validate_token(token)
        if user:
            st.session_state.logged_in = True
            st.session_state.user_type = user["tipo"]
            st.session_state.user_email = user["email"]
            st.success(f"✅ Bem-vindo, {user['nome']} ({user['tipo']})")
        else:
            st.error("Token inválido ou expirado.")
        return

    # Formulário para enviar o link mágico
    st.subheader("📧 Enviar link mágico para um usuário")

    # Dados do remetente
    remetente_nome = "Administracao GeoVoto"
    remetente_email = "leticiafrotamesquita@gmail.com"
    remetente_senha = "tqrq qslz piko zhyu"

    # E-mail do usuário que vai receber o link
    email = st.text_input("E-mail do usuário para login")

    if st.button("📨 Enviar link"):
        user = get_user_by_email(email)
        if user:
            token = str(uuid.uuid4())
            update_user_token(email, token)

            if not remetente_email or not remetente_senha or not remetente_nome:
                st.error("⚠️ Preencha as credenciais do remetente.")
            elif enviar_link_por_email(
                remetente_email, remetente_nome, remetente_senha, email, token
            ):
                st.success("✅ Link mágico enviado com sucesso!")
            else:
                st.error("❌ Não foi possível enviar o e-mail.")
        else:
            st.error("Usuário não encontrado.")
