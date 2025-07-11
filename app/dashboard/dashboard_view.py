# app/dashboard/dashboard_view.py

import streamlit as st
from .data_loader import load_data
from components.charts import *
from components.filters import filtrar_por_candidato

@st.cache_data(show_spinner=False)
def build_dashboard(_engine):
    """Constrói e exibe o dashboard principal."""
    with st.spinner("Carregando dados..."):
        if "Arquivos Carregados" not in st.session_state:
            st.session_state["Arquivos Carregados"] = load_data(_engine)

        dataframes = st.session_state["Arquivos Carregados"]

    
    if not isinstance(dataframes, dict):
        st.error("Erro ao carregar os dados.")
        return
    if len(dataframes) == 0:
        st.error("Não foi possível carregar os dados. Verifique a conexão e a query.")
        return

    # Selecionar candidato
    lista_candidatos = dataframes['candidato'][['Num_Candidato', 'Nome_Urna']].drop_duplicates()
    nome = lista_candidatos['Nome_Urna']# st.sidebar.selectbox("Selecione o candidato", lista_candidatos['Nome_Urna'])
    num_candidato = lista_candidatos[lista_candidatos['Nome_Urna'] == nome]['Num_Candidato'].values[0]

    # Filtrar dados por candidato selecionado
    dados_candidato = st.session_state.get(
        "Filtro Carregado",
        filtrar_por_candidato(dataframes, num_candidato)
    )

    if not dados_candidato or all(df.empty for df in dados_candidato.values()):
        st.warning("Nenhum dado encontrado para os filtros selecionados.")
        return
    
    with st.container():
        # Layout em colunas
        st.metric("Total de Municípios", dados_candidato['votacao_candidato_municipio_zona']['FK_Cod_Municipio'].nunique())
        
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("📊 Desempenho do Candidato")
            grafico_votos_por_municipio(dados_candidato['votacao_candidato_municipio_zona'], dataframes['municipio'])
        
        with col2:
            st.header("🤝 Apoio Político")
            grafico_apoio_prefeito(dados_candidato['votacao_candidato_municipio_zona'], dados_candidato['apoio_prefeito_candidato'])

        with col3:
            st.header("🏛️ Votos por Partido")
            grafico_votos_partido(dataframes['votos_partido_municipio'])

        with col4:
            st.header("📈 Comparecimento")
            grafico_comparecimento(dataframes['manifestacao_eleitorado_municipio'], dataframes['municipio'])

    # Visualização dos dados detalhados
    st.markdown("---")
    with st.expander("Ver dados detalhados da seleção"):
        for nome_tabela, df in dados_candidato.items():
            st.subheader(f"Tabela: {nome_tabela}")
            st.dataframe(df, use_container_width=True)