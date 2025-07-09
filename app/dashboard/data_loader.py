# app/dashboard/data_loader.py

import pandas as pd
import streamlit as st
from sqlalchemy import text
from database.queries import read_sql_file


@st.cache_data(ttl=600)
def load_data(engine):
    if engine is None:
        return pd.DataFrame()

    query = text(read_sql_file("load_dashboard_data.sql"))

    try:
        with engine.connect() as conn:
            return pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Erro ao carregar os dados do dashboard: {e}")
        return pd.DataFrame()

