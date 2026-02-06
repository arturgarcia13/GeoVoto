import sys
from pathlib import Path

# Add src to path to allow absolute imports of geovoto package
src_path = Path(__file__).parent.parent
sys.path.append(str(src_path))

import streamlit as st
from geovoto.config.settings import settings
from geovoto.core.logging import setup_logging
from geovoto.ui.session import SessionManager
from geovoto.services.auth_service import AuthService
from geovoto.ui.layouts.login import LoginLayout
from geovoto.ui.layouts.main_layout_view import MainLayout

# Setup logging
logger = setup_logging()

def main():
    """Main entrypoint for the GeoVoto application."""
    st.set_page_config(
        page_title=settings.ui.page_title,
        page_icon=settings.ui.page_icon,
        layout=settings.ui.layout,
        initial_sidebar_state=settings.ui.initial_sidebar_state
    )
    
    # Initialize session
    session_manager = SessionManager()
    session_manager.initialize()
    
    # Check authentication
    if not session_manager.is_logged_in():
        # Check if there is a token in URL
        query_params = st.query_params
        token = query_params.get("token")
        
        if token:
            _handle_token_login(token, session_manager)
        else:
            LoginLayout().render()
    else:
        MainLayout().render()

def _handle_token_login(token: str, session_manager: SessionManager):
    """Handles auto-login via URL token."""
    auth_service = AuthService()
    user = auth_service.validate_token(token)
    
    if user:
        session_manager.login_user(user)
        st.success(f"Welcome back, {user.get('nome')}!")
        st.rerun()
    else:
        st.error("Invalid or expired token.")
        LoginLayout().render()

if __name__ == "__main__":
    main()
