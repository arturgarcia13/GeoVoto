# core/auth_manager.py
import streamlit as st
from typing import Optional, Dict, Any
from database.queries import validate_token
from core.session_manager import SessionManager, SessionKeys

class AuthManager:
    """Gerenciador de autenticação centralizado"""
    
    def __init__(self):
        self.session_manager = SessionManager()
    
    def is_authenticated(self) -> bool:
        """Verifica se usuário está autenticado"""
        # Primeiro verifica token da URL se ainda não processado
        if not self.session_manager.get(SessionKeys.TOKEN_PROCESSED):
            self._process_url_token()
        
        return self.session_manager.is_logged_in()
    
    def _process_url_token(self) -> None:
        """Processa token da URL"""
        query_params = st.query_params
        token = query_params.get("token")
        
        if token:
            self.session_manager.set(SessionKeys.TOKEN_PROCESSED, True)
            self._authenticate_with_token(token)
    
    def _authenticate_with_token(self, token: str) -> bool:
        """Autentica usuário com token"""
        if len(token) < 20:
            st.error("Token malformado.")
            return False
        
        with st.spinner("Processando login..."):
            user = validate_token(token)
            
            if user:
                self.session_manager.set_user_data(user)
                st.success(f"✅ Bem-vindo, {user['nome']}!")
                st.rerun()
                return True
            else:
                st.error("❌ Token inválido")
                return False
    
    def logout(self) -> None:
        """Realiza logout do usuário"""
        self.session_manager.clear_session()
        st.rerun()
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Retorna dados do usuário atual"""
        if self.is_authenticated():
            return self.session_manager.get_user_info()
        return None
    
    def is_admin(self) -> bool:
        """Verifica se usuário atual é admin"""
        user_type = self.session_manager.get_user_type()
        return user_type == "admin"
    
    def require_auth(self) -> bool:
        """Força autenticação - retorna True se autenticado"""
        if not self.is_authenticated():
            st.error("🔒 Acesso negado. Faça login para continuar.")
            st.stop()
        return True
    
    def require_admin(self) -> bool:
        """Força autenticação de admin"""
        self.require_auth()
        if not self.is_admin():
            st.error("🚫 Acesso restrito a administradores.")
            st.stop()
        return True