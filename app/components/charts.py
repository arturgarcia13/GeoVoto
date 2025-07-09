import streamlit as st
import plotly.express as px
import pandas as pd

def grafico_votos_por_municipio(votacao, municipios):
    df = votacao.merge(municipios, left_on='FK_Cod_Municipio', right_on='Cod_IBGE')
    fig = px.bar(df, x='Nome_Municipio', y='Votos_Validos_Candidato',
                 title='Votos Válidos por Município', text='Votos_Validos_Candidato')
    st.plotly_chart(fig, use_container_width=True)

def grafico_votos_por_municipio(votacao, municipios):
    df = votacao.merge(municipios, left_on='FK_Cod_Municipio', right_on='Cod_IBGE')
    fig = px.bar(df, x='Nome_Municipio', y='Votos_Validos_Candidato',
                 title='Votos Válidos por Município', text='Votos_Validos_Candidato')
    st.plotly_chart(fig, use_container_width=True)

def grafico_apoio_prefeito(votacao, apoio):
    df = votacao.merge(apoio, on=['FK_Cod_Municipio', 'FK_Num_Candidato'])
    fig = px.box(df, x='Status_Apoio', y='Votos_Validos_Candidato',
                 title='Votos por Apoio do Prefeito')
    st.plotly_chart(fig, use_container_width=True)

def grafico_faixa_etaria(perfil):
    fig = px.bar(perfil.groupby('Faixa_Etaria')['Qtd_Eleitores_Perfil'].sum().reset_index(),
                 x='Faixa_Etaria', y='Qtd_Eleitores_Perfil', title='Distribuição por Faixa Etária')
    st.plotly_chart(fig, use_container_width=True)

def grafico_votos_partido(votos_partido):
    fig = px.pie(votos_partido, values='Votos_Validos_Partido_Municipio',
                 names='FK_Sigla_Partido', title='Distribuição de Votos por Partido')
    st.plotly_chart(fig, use_container_width=True)

def grafico_comparecimento(manifestacao, municipios):
    df = manifestacao.merge(municipios, left_on='FK_Cod_Municipio', right_on='Cod_IBGE')
    fig = px.bar(df, x='FK_Cod_Municipio', y='Percentual_Comparecimento',
                 title='Comparecimento por Município')
    st.plotly_chart(fig, use_container_width=True)
