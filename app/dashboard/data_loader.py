# app/dashboard/data_loader.py

import pandas as pd
import streamlit as st
from sqlalchemy import inspect


@st.cache_data(ttl=600)
def load_data(_engine):
    if _engine is None:
        return pd.DataFrame()

    try:
        with _engine.connect() as conn:
            insp = inspect(_engine)
            # Pega todos os nomes de tabelas
            tabelas = insp.get_table_names()
            dfs = {}
            # Loop para criar DataFrames com nomes iguais ao das tabelas
            for tabela in tabelas:
                if tabela == "perfil_eleitorado_local":
                    continue
                # Carregar uma tabela do banco local
                dfs[tabela] = pd.read_sql(f'SELECT * FROM {tabela}', con=conn)
                # print(f"\nTabela carregada como DataFrame: {tabela}")       
            return dfs
    except Exception as e:
        st.error(f"Erro ao carregar os dados do dashboard")
        return pd.DataFrame()

