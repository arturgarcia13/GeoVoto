import streamlit as st

def show_kpis(df):
    total_votos = int(df['votos_candidato'].sum())
    num_candidatos = df['nome_urna_candidato'].nunique()
    num_partidos = df['sigla_partido'].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Votos Válidos", f"{total_votos:,}".replace(",", "."))
    col2.metric("Nº de Candidatos", num_candidatos)
    col3.metric("Nº de Partidos", num_partidos)