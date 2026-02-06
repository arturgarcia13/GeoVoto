import streamlit as st
from typing import List

from geovoto.ui.session import SessionManager
from geovoto.services.auth_service import AuthService
from geovoto.ui.pages.dashboard import DashboardPage
# Add other pages as they are implemented
# from geovoto.ui.pages.geographic import GeographicPage
# from geovoto.ui.pages.strategic import StrategicPage
# from geovoto.ui.pages.users import UsersPage

class MainLayout:
    """Main application layout for authenticated users."""
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.auth_service = AuthService()
        self.pages = {
            "Dashboard": DashboardPage(),
            # "Análise Geográfica": GeographicPage(),
            # "Análise Estratégica": StrategicPage(),
        }
        
    def render(self):
        self._render_sidebar()
        self._render_main_content()
    
    def _render_sidebar(self):
        with st.sidebar:
            user_info = self.session_manager.get_current_user_info()
            st.success(f"Logged in: {user_info.get('name')}")
            
            st.title("Navigation")
            
            # Additional admin options could go here
            if self.session_manager.get("user_type") == "admin":
                 st.info("Admin Mode")
            
            if st.button("Logout", type="secondary"):
                self.session_manager.clear()
                st.rerun()

    def _render_main_content(self):
        tabs_names = list(self.pages.keys())
        tabs = st.tabs(tabs_names)
        
        for i, name in enumerate(tabs_names):
            with tabs[i]:
                try:
                    self.pages[name].render()
                except Exception as e:
                    st.error(f"Error loading {name}: {e}")
