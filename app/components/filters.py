import streamlit as st

def filtrar_por_candidato(dados, num_candidato):
    dados_filtrados = {}
    for chave, df in dados.items():
        if 'FK_Num_Candidato' in df.columns:
            dados_filtrados[chave] = df[df['FK_Num_Candidato'] == num_candidato]
        else:
            dados_filtrados[chave] = df
    return dados_filtrados