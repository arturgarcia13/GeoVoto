import streamlit as st
import uuid
import time
from typing import Optional

from geovoto.services.auth_service import AuthService
from geovoto.ui.session import SessionManager
from geovoto.config.settings import settings

class LoginLayout:
    """Handles the login and registration UI flow."""
    
    def __init__(self):
        self.auth_service = AuthService()
        self.session_manager = SessionManager()

    def render(self):
        """Renders the main login interface."""
        self._render_header()
        
        tab_intro, tab_login = st.tabs(["🏠 Apresentação", "🔐 Acesso"])
        
        with tab_intro:
            self._render_intro_page()
        
        with tab_login:
            if st.session_state.get("register_mode", False):
                self._render_registration_form()
            else:
                self._render_login_form()

    def _render_header(self):
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem 0;">
            <h1>{settings.ui.page_icon} {settings.ui.page_title}</h1>
            <h3>Sistema de Análise Eleitoral</h3>
        </div>
        """, unsafe_allow_html=True)

    def _render_intro_page(self):
        st.markdown("""
        ### 📊 Bem-vindo ao GeoVoto
        
        Plataforma profissional para análise e visualização de dados eleitorais.
        
        **Funcionalidades:**
        - 📈 Dashboard Interativo
        - 🗺️ Mapas de Calor e Coropléticos
        - ⚡ Performance Otimizada
        
        Clique na aba **Acesso** para entrar.
        """)

    def _render_login_form(self):
        st.subheader("🔐 Acesso ao Sistema")
        
        with st.form("login_form"):
            email = st.text_input("📧 Email", placeholder="seu.email@exemplo.com")
            
            col_submit, col_register = st.columns(2)
            with col_submit:
                submit = st.form_submit_button("🔑 Acessar", type="primary", use_container_width=True)
            with col_register:
                register = st.form_submit_button("📝 Cadastrar", use_container_width=True)

        if submit:
            self._handle_login(email)
        
        if register:
            st.session_state["register_mode"] = True
            st.rerun()

    def _handle_login(self, email: str):
        if not email:
            st.warning("Informe seu email.")
            return

        user = self.auth_service.get_user_by_email(email)
        if not user:
            st.error("Usuário não encontrado.")
            return

        # Generate token
        token = str(uuid.uuid4())
        # In a real app we might send email, here we show link
        self.auth_service.user_repository.update_token(email, token) # Accessing repo directly for now or add method to service
        
        link = f"/?token={token}"
        st.success("Link de acesso gerado!")
        st.code(link, language=None)
        st.info(f"Link expira em {settings.security.token_expiry_hours} horas.")

    def _render_registration_form(self):
        st.subheader("📝 Cadastro")
        
        if st.button("← Voltar"):
            st.session_state["register_mode"] = False
            st.rerun()
            
        with st.form("reg_form"):
            name = st.text_input("Nome")
            email = st.text_input("Email")
            if st.form_submit_button("Criar Conta", type="primary"):
                self._handle_registration(name, email)

    def _handle_registration(self, name: str, email: str):
        if self.auth_service.get_user_by_email(email):
            st.error("Email já cadastrado.")
            return
            
        if self.auth_service.user_repository.create(name, email, "user", ""):
            st.success("Conta criada! Volte para fazer login.")
        else:
            st.error("Erro ao criar conta.")
