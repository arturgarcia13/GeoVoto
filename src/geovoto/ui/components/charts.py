import streamlit as st
import plotly.express as px
import pandas as pd
from typing import Optional

def chart_votes_by_municipality(votacao: pd.DataFrame, municipios: pd.DataFrame):
    """Generates a bar chart of top 10 municipalities by valid votes."""
    df = votacao.merge(
        municipios, left_on='FK_Cod_Municipio', right_on='Cod_IBGE'
    )

    # Filter out zero votes
    df = df[df['Votos_Validos_Candidato'] > 0].copy()
    
    votes_grouped = df.groupby('Nome_Municipio')[
        'Votos_Validos_Candidato'
    ].sum().reset_index()
    
    votes_grouped = votes_grouped.sort_values(
        by='Votos_Validos_Candidato', ascending=False
    )

    df_top10 = votes_grouped.head(10)

    fig = px.bar(
        df_top10,
        x='Nome_Municipio',
        y='Votos_Validos_Candidato',
        title='Top 10 Municípios (Votos Válidos)',
        text='Votos_Validos_Candidato',
        labels={'Nome_Municipio': 'Município', 'Votos_Validos_Candidato': 'Votos'}
    )

    fig.update_layout(yaxis_type="log", xaxis_tickangle=45)
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)


def chart_political_support(votacao: pd.DataFrame, support: pd.DataFrame):
    """Generates a chart showing votes by mayor support status."""
    df = votacao.merge(support, on=['FK_Cod_Municipio', 'FK_Num_Candidato'])
    
    votes_by_support = df.groupby('Status_Apoio')[
        'Votos_Validos_Candidato'
    ].sum().reset_index()

    fig = px.bar(
        votes_by_support, 
        x='Status_Apoio',
        y='Votos_Validos_Candidato',
        title='Votos por Status de Apoio',
        color='Status_Apoio'
    )
    st.plotly_chart(fig, use_container_width=True)


def chart_turnout(manifestacao: pd.DataFrame, municipios: pd.DataFrame):
    """Generates a chart of top municipalities by turnout."""
    try:
        df_combined = pd.merge(
            manifestacao, municipios,
            left_on='FK_Cod_Municipio', right_on='Cod_IBGE'
        )
        
        avg_turnout = df_combined['Percentual_Comparecimento'].mean()
        
        df_chart = df_combined.sort_values(
            by='Percentual_Comparecimento', ascending=False
        ).head(30)

        fig = px.bar(
            df_chart, 
            x='Nome_Municipio', 
            y='Percentual_Comparecimento',
            title='Top 30 Municípios por Comparecimento',
            labels={
                "Nome_Municipio": "Município",
                "Percentual_Comparecimento": "Comparecimento (%)"
            },
            text='Percentual_Comparecimento'
        )
        
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_yaxes(range=[50, 100]) # Adaptive range would be better but keeping simple
        
        # Add average line
        fig.add_hline(
            y=avg_turnout,
            line=dict(color="red", width=2, dash="dash"),
            annotation_text=f"Média: {avg_turnout:.1f}%",
            annotation_position="bottom right"
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error generating turnout chart: {e}")


def chart_vote_composition(manifestacao: pd.DataFrame, municipios: pd.DataFrame, municipality_name="Todos os Municípios"):
    """Generates a pie chart of vote composition (valid, null, blank)."""
    try:
        if municipality_name == "Todos os Municípios":
            st.subheader("Composição Geral dos Votos")
            df_filtered = manifestacao
        else:
            st.subheader(f"Composição dos Votos em {municipality_name}")
            # Find municipality code
            muni_row = municipios[municipios['Nome_Municipio'] == municipality_name]
            if muni_row.empty:
                st.warning(f"Município {municipality_name} não encontrado.")
                return
            
            cod_municipio = muni_row['Cod_IBGE'].values[0]
            df_filtered = manifestacao[manifestacao['FK_Cod_Municipio'] == cod_municipio]

        if df_filtered.empty:
            st.info("Sem dados para a seleção.")
            return

        total_blanks = df_filtered['Votos_Brancos'].sum()
        total_nulls = df_filtered['Votos_Nulos_Urna'].sum()
        total_annulled = df_filtered['Votos_Anulados'].sum()
        total_turnout = df_filtered['Votos_Validos_Municipio'].sum() + total_blanks + total_nulls + total_annulled 
        # Note: Logic slightly adjusted, checking original code calculation:
        # total_comparecimento = df_filtered['Comparecimento'].sum() (Usually Abstencao + Comparecimento = Aptos)
        
        # Recalculating totals based on available columns in `manifestacao_eleitorado_municipio`
        # Assuming DataService returns these columns.
        
        # Simply using sums for the chart
        total_valid = df_filtered['Votos_Validos_Municipio'].sum()

        data_chart = pd.DataFrame({
            'Tipo': ['Votos Válidos', 'Votos Brancos', 'Votos Nulos', 'Votos Anulados'],
            'Total': [total_valid, total_blanks, total_nulls, total_annulled]
        })

        colors = {
            'Votos Válidos': 'royalblue',
            'Votos Brancos': 'lightskyblue',
            'Votos Nulos': 'lightcoral',
            'Votos Anulados': 'crimson'
        }

        fig = px.pie(
            data_chart,
            names='Tipo',
            values='Total',
            hole=0.4,
            color='Tipo',
            color_discrete_map=colors
        )
        
        fig.update_traces(textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error generating composition chart: {e}")
