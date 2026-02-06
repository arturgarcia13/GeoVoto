import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from plotly.figure_factory import create_distplot


def grafico_votos_por_municipio(votacao, municipios):
    df = votacao.merge(
        municipios, left_on='FK_Cod_Municipio', right_on='Cod_IBGE')
    fig = px.bar(df, x='Nome_Municipio', y='Votos_Validos_Candidato',
                 title='Votos Válidos por Município', text='Votos_Validos_Candidato')
    st.plotly_chart(fig, use_container_width=True)


def grafico_votos_por_municipio(votacao, municipios):
    df = votacao.merge(
        municipios, left_on='FK_Cod_Municipio', right_on='Cod_IBGE')

    # Evita log de zero
    df = df[df['Votos_Validos_Candidato'] > 0].copy()
    votos_agrupados = df.groupby('Nome_Municipio')[
        'Votos_Validos_Candidato'].sum().reset_index()
    votos_agrupados = votos_agrupados.sort_values(
        by='Votos_Validos_Candidato', ascending=False)

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
    # soma dos municipios que apoia, nao apoia ou indeciso
    votos_por_apoio = df.groupby('Status_Apoio')[
        'Votos_Validos_Candidato'].sum().reset_index()

    fig = px.bar(votos_por_apoio, x='Status_Apoio',
                 y='Votos_Validos_Candidato')
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
    try:
        df_combinado = pd.merge(manifestacao, municipios,
                                left_on='FK_Cod_Municipio', right_on='Cod_IBGE')
        media_geral = df_combinado['Percentual_Comparecimento'].mean()
        df_grafico = df_combinado.sort_values(
            by='Percentual_Comparecimento', ascending=False).head(30)

        fig = px.bar(
            df_grafico, x='Nome_Municipio', y='Percentual_Comparecimento',
            title='Top 30 Municípios por Taxa de Comparecimento',
            labels={"Nome_Municipio": "Município",
                    "Percentual_Comparecimento": "Comparecimento (%)"},
            text='Percentual_Comparecimento'
        )
        fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        fig.update_yaxes(range=[78, 91])

        # Anotação da média dentro do gráfico
        fig.add_annotation(
            x=0.98, y=0.98, xref="paper", yref="paper",
            text=f"<b>Média Geral</b><br>{media_geral:.2f}%",
            showarrow=False, font=dict(size=14, color="white"), align="right",
            bgcolor="rgba(0, 0, 0, 0.7)", bordercolor="rgba(255, 255, 255, 0.5)",
            borderwidth=1, borderpad=10
        )
        # Expessura
        fig.add_hline(
            y=media_geral,
            line=dict(color="red", width=3, dash="solid")
        )

        # exibindo
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Ocorreu um erro ao gerar o gráfico de comparecimento: {e}")


def grafico_composicao_votos(df_manifestacao, dataframes, municipio_selecionado="Todos os Municípios"):
    try:
        if municipio_selecionado == "Todos os Municípios":
            st.header("Composição Geral dos Votos")
            df_filtrado = df_manifestacao
        else:
            st.header(f"Composição dos Votos em {municipio_selecionado}")
            cod_municipio = dataframes['municipio'][dataframes['municipio']
                                                    ['Nome_Municipio'] == municipio_selecionado]['Cod_IBGE'].values[0]
            df_filtrado = df_manifestacao[df_manifestacao['FK_Cod_Municipio']
                                          == cod_municipio]

        if df_filtrado.empty:
            st.info(f"Não há dados de votação para {municipio_selecionado}.")
            return

        total_brancos = df_filtrado['Votos_Brancos'].sum()
        total_nulos = df_filtrado['Votos_Nulos_Urna'].sum()
        total_anulados = df_filtrado['Votos_Anulados'].sum()
        total_comparecimento = df_filtrado['Comparecimento'].sum()
        if total_comparecimento == 0:
            st.info(f"Não houve comparecimento para {municipio_selecionado}.")
            return
        total_validos = total_comparecimento - \
            (total_brancos + total_nulos + total_anulados)

        dados_grafico = pd.DataFrame({
            'Tipo de Voto': ['Votos Válidos', 'Votos Brancos', 'Votos Nulos', 'Votos Anulados'],
            'Total': [total_validos, total_brancos, total_nulos, total_anulados]
        })

        ordem_fixa = ['Votos Válidos', 'Votos Brancos',
                      'Votos Nulos', 'Votos Anulados']
        mapa_de_cores = {
            'Votos Válidos': 'royalblue',
            'Votos Brancos': 'lightskyblue',
            'Votos Nulos': 'lightcoral',
            'Votos Anulados': 'crimson'
        }

        fig = px.pie(
            dados_grafico,
            names='Tipo de Voto',
            values='Total',
            hole=0.4,
            color='Tipo de Voto',  # cor = categoria
            color_discrete_map=mapa_de_cores,
            category_orders={"Tipo de Voto": ordem_fixa}
        )

        fig.update_traces(textinfo='percent+label',
                          textfont_size=12, pull=[0.05, 0, 0, 0])
        fig.update_layout(title_text='', legend_title_text='Categorias')

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(
            f"Ocorreu um erro ao gerar o gráfico de composição de votos: {e}")