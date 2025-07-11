import streamlit as st
import uuid
from database.queries import get_user_by_email, update_user_token, validate_token

def login_scan(token: str) -> bool:
    if len(token) < 20:
        st.error("Token malformado.")
        return False
    user = validate_token(token)
    if user:
        st.session_state["logged_in"] = True
        st.session_state["user_type"] = user["tipo"]
        st.session_state["user_email"] = user["email"]
        st.session_state["nome"] = user["nome"]
        st.success(f"✅ Bem-vindo, {user['nome']}")
        st.rerun()
        return True
    else:
        return False

def login_screen():

    st.title("Login na Plataforma GeoVoto")
    # Inicializa estados
    for key in ["logged_in", "user_type", "user_email"]:
        if key not in st.session_state:
            st.session_state[key] = None if key != "logged_in" else False

    st.subheader("Criar token de autenticação")

    email = st.text_input("E-mail do usuário para login")

    if st.button("Criar token", use_container_width=True):
        if not email:
            st.warning("Digite um e-mail válido.")
            return

        user = get_user_by_email(email)
        st.write(user)
        if not user:
            st.error("Usuário não encontrado.")
            return

        token = str(uuid.uuid4())
        update_user_token(email, token)

        success_login(token)

@st.dialog("Aqui está seu token")
def success_login(token):
    st.success("✅ Token criado com sucesso!")
    st.write(f'/?token={token}')
    st.balloons()
