# core/session_manager.py
import streamlit as st
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class SessionKeys:
    """Constantes para chaves de sessão"""
    LOGGED_IN: str = "logged_in"
    TOKEN_PROCESSED: str = "token_processed"
    REGISTER_MODE: str = "register_mode"
    USER_TYPE: str = "user_type"
    USER_EMAIL: str = "user_email"
    USER_NAME: str = "nome"

class SessionManager:
    """Gerenciador centralizado de estado da sessão"""
    
    def __init__(self):
        self.default_states = {
            SessionKeys.LOGGED_IN: False,
            SessionKeys.TOKEN_PROCESSED: False,
            SessionKeys.REGISTER_MODE: False,
            SessionKeys.USER_TYPE: None,
            SessionKeys.USER_EMAIL: None,
            SessionKeys.USER_NAME: None,
        }
    
    def initialize(self):
        """Inicializa todas as variáveis de estado necessárias"""
        for key, default_value in self.default_states.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém valor da sessão de forma segura"""
        return st.session_state.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Define valor na sessão"""
        st.session_state[key] = value
    
    def clear_session(self) -> None:
        """Limpa completamente a sessão atual"""
        # Limpa parâmetros da URL
        st.query_params.clear()
        
        # Limpa session_state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        # Reinicializa estados padrão
        self.initialize()
    
    def is_logged_in(self) -> bool:
        """Verifica se usuário está logado"""
        return self.get(SessionKeys.LOGGED_IN, False)
    
    def get_user_type(self) -> Optional[str]:
        """Retorna tipo do usuário logado"""
        return self.get(SessionKeys.USER_TYPE)
    
    def get_user_info(self) -> Dict[str, Any]:
        """Retorna informações do usuário logado"""
        return {
            "name": self.get(SessionKeys.USER_NAME),
            "email": self.get(SessionKeys.USER_EMAIL),
            "type": self.get(SessionKeys.USER_TYPE)
        }
    
    def set_user_data(self, user_data: Dict[str, Any]) -> None:
        """Define dados do usuário na sessão"""
        self.set(SessionKeys.LOGGED_IN, True)
        self.set(SessionKeys.USER_TYPE, user_data.get("tipo"))
        self.set(SessionKeys.USER_EMAIL, user_data.get("email"))
        self.set(SessionKeys.USER_NAME, user_data.get("nome"))