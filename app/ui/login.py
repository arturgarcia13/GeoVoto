import streamlit as st
import uuid
import smtplib
from email.message import EmailMessage
from streamlit_extras.switch_page_button import switch_page
from database.queries import get_user_by_email, update_user_token, validate_token


def enviar_link_por_email(remetente_email, remetente_nome, senha_app, destinatario, token) -> bool:
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


def login_scam(token: str) -> bool:
    if token:
        if not token or len(token) < 20:
            st.error("Token ausente ou malformado.")
            return False
        user = validate_token(token)
        print(user)
        if user:
            st.session_state["logged_in"] = True
            st.session_state["user_type"] = user["tipo"]
            st.session_state["user_email"] = user["email"]
            st.session_state["nome"] = user["nome"]
            st.success(f"✅ Bem-vindo, {user['nome']}")
            st.rerun()
            return True
        else:
            st.error("Token inválido ou expirado.")
            return False
    return False


def login_screen():
    st.title("🔐 Login GeoVoto")

    # Inicializa estados
    for key in ["logged_in", "user_type", "user_email"]:
        if key not in st.session_state:
            st.session_state[key] = None if key != "logged_in" else False

    st.subheader("📧 Enviar link mágico de autenticação")

    email = st.text_input("E-mail do usuário para login")

    # Idealmente, use st.secrets (recomendo configurar)
    remetente_nome = "Administracao GeoVoto"
    remetente_email = "leticiafrotamesquita@gmail.com"
    remetente_senha = "tqrq qslz piko zhyu"

    if st.button("📨 Enviar link", use_container_width=True):
        if not email:
            st.warning("Digite um e-mail válido.")
            return

        user = get_user_by_email(email)
        if not user:
            st.error("Usuário não encontrado.")
            return

        token = str(uuid.uuid4())
        update_user_token(email, token)

        if enviar_link_por_email(remetente_email, remetente_nome, remetente_senha, email, token):
            st.success("✅ Link mágico enviado com sucesso! Verifique seu e-mail.")
        else:
            st.error("❌ Não foi possível enviar o e-mail.")
