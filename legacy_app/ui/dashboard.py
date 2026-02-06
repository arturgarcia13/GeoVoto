import streamlit as st
from dashboard.dashboard_view import build_dashboard
from database.connection import get_engine


def page_dashboard():
    
    engine = get_engine()
    
    st.title("Dashboard de Análise Eleitoral")
    
    build_dashboard(engine)