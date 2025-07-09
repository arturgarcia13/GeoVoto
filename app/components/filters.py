import streamlit as st

def aplicar_filtros(df):
    st.sidebar.header("Filtros")

    municipios = sorted(df['nome_municipio'].unique())
    municipio_selecionado = st.sidebar.selectbox("Município", ["Todos os Municípios"] + municipios)

    partidos = sorted(df['sigla_partido'].unique())
    partido_selecionado = st.sidebar.selectbox("Partido", ["Todos os Partidos"] + partidos)

    df_filtrado = df.copy()
    if municipio_selecionado != "Todos os Municípios":
        df_filtrado = df_filtrado[df_filtrado['nome_municipio'] == municipio_selecionado]
    if partido_selecionado != "Todos os Partidos":
        df_filtrado = df_filtrado[df_filtrado['sigla_partido'] == partido_selecionado]

    return df_filtrado