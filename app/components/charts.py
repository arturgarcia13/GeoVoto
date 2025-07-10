import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from plotly.figure_factory import create_distplot

def grafico_votos_por_municipio(votacao, municipios):
    df = votacao.merge(municipios, left_on='FK_Cod_Municipio', right_on='Cod_IBGE')
    fig = px.bar(df, x='Nome_Municipio', y='Votos_Validos_Candidato',
                 title='Votos Válidos por Município', text='Votos_Validos_Candidato')
    st.plotly_chart(fig, use_container_width=True)

def grafico_votos_por_municipio(votacao, municipios):
    df = votacao.merge(municipios, left_on='FK_Cod_Municipio', right_on='Cod_IBGE')

    # Evita log de zero
    df = df[df['Votos_Validos_Candidato'] > 0].copy()
    votos_agrupados = df.groupby('Nome_Municipio')['Votos_Validos_Candidato'].sum().reset_index()
    votos_agrupados = votos_agrupados.sort_values(by='Votos_Validos_Candidato', ascending=False)
    
    df_top10 = votos_agrupados.head(10)

    fig = px.bar(
        df_top10,
        x='Nome_Municipio',
        y='Votos_Validos_Candidato',
        title='Top 10',
        text='Votos_Validos_Candidato'
    )
    
    fig.update_layout(yaxis_type="log", xaxis_tickangle=45)
    fig.update_traces(texttemplate='%{text}', textposition='outside')

    st.plotly_chart(fig, use_container_width=True)



def grafico_apoio_prefeito(votacao, apoio):
    df = votacao.merge(apoio, on=['FK_Cod_Municipio', 'FK_Num_Candidato'])
    #soma dos municipios que apoia, nao apoia ou indeciso
    votos_por_apoio = df.groupby('Status_Apoio')['Votos_Validos_Candidato'].sum().reset_index()

    fig = px.bar(votos_por_apoio, x='Status_Apoio', y='Votos_Validos_Candidato')
    st.plotly_chart(fig, use_container_width=True)

def grafico_faixa_etaria(perfil):
    fig = px.bar(perfil.groupby('Faixa_Etaria')['Qtd_Eleitores_Perfil'].sum().reset_index(),
                 x='Faixa_Etaria', y='Qtd_Eleitores_Perfil', title='Distribuição por Faixa Etária')
    st.plotly_chart(fig, use_container_width=True)

def grafico_votos_partido(votos_partido):
    fig = px.pie(votos_partido, values='Votos_Validos_Partido_Municipio',
                 names='FK_Sigla_Partido', )
    st.plotly_chart(fig, use_container_width=True)

def grafico_comparecimento(manifestacao, municipios): 
    df = manifestacao.merge(municipios, left_on='FK_Cod_Municipio', right_on='Cod_IBGE')

    fig = px.histogram(
        df,
        x='Percentual_Comparecimento',
        nbins=40,
        histnorm='density',  # transforma o eixo y para densidade
        marginal='rug',      # adiciona marquinhas abaixo da curva
        title='Distribuição da Taxa de Comparecimento por Município'
    )

    fig.update_layout(xaxis_title='% Comparecimento', yaxis_title='Densidade')
    st.plotly_chart(fig, use_container_width=True)