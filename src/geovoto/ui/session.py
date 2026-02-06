from dataclasses import dataclass
from typing import Any, Dict, Optional
import streamlit as st

@dataclass
class SessionKeys:
    """Keys used in Streamlit session state."""
    LOGGED_IN: str = "logged_in"
    TOKEN_PROCESSED: str = "token_processed"
    REGISTER_MODE: str = "register_mode"
    USER_TYPE: str = "user_type"
    USER_EMAIL: str = "user_email"
    USER_NAME: str = "nome"


class SessionManager:
    """Manages Streamlit session state."""
    
    def __init__(self):
        self._defaults = {
            SessionKeys.LOGGED_IN: False,
            SessionKeys.TOKEN_PROCESSED: False,
            SessionKeys.REGISTER_MODE: False,
            SessionKeys.USER_TYPE: None,
            SessionKeys.USER_EMAIL: None,
            SessionKeys.USER_NAME: None,
        }

    def initialize(self) -> None:
        """Initializes session state with default values if not present."""
        for key, value in self._defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return st.session_state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        st.session_state[key] = value

    def clear(self) -> None:
        """Clears all session state and resets to defaults."""
        st.query_params.clear()
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        self.initialize()

    def login_user(self, user_data: Dict[str, Any]) -> None:
        """Sets user data in session upon login."""
        self.set(SessionKeys.LOGGED_IN, True)
        self.set(SessionKeys.USER_TYPE, user_data.get("tipo"))
        self.set(SessionKeys.USER_EMAIL, user_data.get("email"))
        self.set(SessionKeys.USER_NAME, user_data.get("nome"))

    def get_current_user_info(self) -> Dict[str, Any]:
        return {
            "name": self.get(SessionKeys.USER_NAME),
            "email": self.get(SessionKeys.USER_EMAIL),
            "type": self.get(SessionKeys.USER_TYPE)
        }

    def is_logged_in(self) -> bool:
        return self.get(SessionKeys.LOGGED_IN, False)
