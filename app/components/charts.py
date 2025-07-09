import streamlit as st

def grafico_top_candidatos(df):
    st.subheader("Top 10 Candidatos Mais Votados")
    votos = df.groupby('nome_urna_candidato')['votos_candidato'].sum().sort_values(ascending=False).head(10)
    st.bar_chart(votos)

def grafico_partidos(df):
    st.subheader("Distribuição de Votos por Partido")
    votos = df.groupby('sigla_partido')['votos_candidato'].sum().sort_values(ascending=False)
    st.bar_chart(votos)