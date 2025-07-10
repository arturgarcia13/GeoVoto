# app/dashboard/dashboard_view.py

import streamlit as st
from dashboard.dashboard_view import build_dashboard

def page_dashboard(engine):
    st.sidebar.success(f"Logado como: {st.session_state["nome"]}")

    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

    st.title("📊 Dashboard de Análise Eleitoral")
    st.markdown("Use os filtros na barra lateral para explorar os resultados.")

    build_dashboard(engine)