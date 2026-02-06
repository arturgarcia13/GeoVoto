# connection.py
import streamlit as st
from sqlalchemy import create_engine

@st.cache_resource
def get_engine():
    try:
        database_url = st.secrets["POSTGRES_URL"]
        return create_engine(database_url, connect_args={"sslmode": "require"}, pool_timeout=60)
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None