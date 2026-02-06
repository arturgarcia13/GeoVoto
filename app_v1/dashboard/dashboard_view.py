import streamlit as st
from .data_loader import load_data
from components.charts import *
from components.filters import filtrar_por_candidato

def build_dashboard(engine):
    """Constrói e exibe o dashboard principal."""
    if "Arquivos Carregados" not in st.session_state:
        st.session_state["Arquivos Carregados"] = load_data(engine)

    dataframes = st.session_state["Arquivos Carregados"]

    if not isinstance(dataframes, dict):
        st.error("Erro ao carregar os dados.")
        return
    if len(dataframes) == 0:
        st.error("Não foi possível carregar os dados. Verifique a conexão e a query.")
        return

    st.sidebar.header("Filtros do Dashboard")

    # FILTRO DE MUNICÍPIO
    lista_municipios = sorted(
        dataframes['municipio']['Nome_Municipio'].unique())
    municipio_selecionado = st.sidebar.selectbox(
        "Filtre por Município",
        options=["Todos os Municípios"] + lista_municipios
    )

    # FILTRO DE CANDIDATO
    lista_candidatos = dataframes['candidato'][[
        'Num_Candidato', 'Nome_Urna']].drop_duplicates()
    nome_candidato = st.sidebar.selectbox(
        "Selecione o candidato",
        lista_candidatos['Nome_Urna']
    )
    num_candidato = lista_candidatos[lista_candidatos['Nome_Urna']
                                     == nome_candidato]['Num_Candidato'].values[0]

    # FILTRO DE PARTIDO
    lista_partidos = sorted(dataframes['partido']['Sigla_Partido'].unique())
    partido_selecionado = st.sidebar.selectbox(
        "Filtre por partido",
        options=["Todos"] + lista_partidos
    )

    # FILTRO DE APOIO
    lista_apoio = ["Todos", "apoia", "nao apoia", "indeciso"]
    apoio_selecionado = st.sidebar.selectbox(
        "Filtre por status de apoio",
        options=lista_apoio
    )

    dados_candidato = filtrar_por_candidato(dataframes, num_candidato)

    if not dados_candidato or all(df.empty for df in dados_candidato.values()):
        st.warning("Nenhum dado encontrado para os filtros selecionados.")
        return

    dados_para_graficos = dados_candidato.copy()

    # FILTRO DE PARTIDo
    if partido_selecionado != "Todos":
        dados_para_graficos['votos_partido_municipio'] = dados_para_graficos['votos_partido_municipio'][
            dados_para_graficos['votos_partido_municipio']['FK_Sigla_Partido'] == partido_selecionado
        ]

    # FILTRO DE APOIO
    if apoio_selecionado != "Todos":
        dados_para_graficos['apoio_prefeito_candidato'] = dados_para_graficos['apoio_prefeito_candidato'][
            dados_para_graficos['apoio_prefeito_candidato']['Status_Apoio'] == apoio_selecionado
        ]
        municipios_filtrados_pelo_apoio = dados_para_graficos['apoio_prefeito_candidato']['FK_Cod_Municipio'].unique(
        )
        dados_para_graficos['votacao_candidato_municipio_zona'] = dados_para_graficos['votacao_candidato_municipio_zona'][
            dados_para_graficos['votacao_candidato_municipio_zona']['FK_Cod_Municipio'].isin(
                municipios_filtrados_pelo_apoio)
        ]

    if not dados_para_graficos or all(df.empty for df in dados_para_graficos.values()):
        st.warning(
            "Nenhum dado encontrado para a combinação de filtros selecionada.")
        return

    with st.container():
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header(" Desempenho do Candidato")
            grafico_votos_por_municipio(
                dados_para_graficos['votacao_candidato_municipio_zona'], dataframes['municipio'])

        with col2:
            st.header(" Apoio Político")
            grafico_apoio_prefeito(
                dados_para_graficos['votacao_candidato_municipio_zona'], dados_para_graficos['apoio_prefeito_candidato'])

        with col3:
            st.header(" Comparecimento")
            grafico_comparecimento(
                dataframes['manifestacao_eleitorado_municipio'], dataframes['municipio'])

        with col4:
            grafico_composicao_votos(
                df_manifestacao=dataframes['manifestacao_eleitorado_municipio'],
                dataframes=dataframes,
                municipio_selecionado=municipio_selecionado
            )

    # Visualização dos dados detalhados
    st.markdown("---")
    with st.expander("Ver dados detalhados da seleção"):
        for nome_tabela, df in dados_candidato.items():
            st.subheader(f"Tabela: {nome_tabela}")
            st.dataframe(df, use_container_width=True)