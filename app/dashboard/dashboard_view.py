# app/dashboard/dashboard_view.py

import streamlit as st
from .data_loader import load_data
from components.charts import *
from components.filters import filtrar_por_candidato


def build_dashboard(engine):
    """Constrói e exibe o dashboard principal."""
    dataframes = st.session_state.get("Arquivos Carregados", load_data(engine))


    st.sidebar.success(f"Logado como: Artur") #{st.session_state.email}
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.title("📊 Dashboard de Análise Eleitoral")
    st.markdown("Use os filtros na barra lateral para explorar os resultados.")

    if len(dataframes) != 0:
        # Selecionar candidato
        lista_candidatos = dataframes['candidato'][['Num_Candidato', 'Nome_Urna']].drop_duplicates()
        nome = st.sidebar.selectbox("Selecione o candidato", lista_candidatos['Nome_Urna'])
        num_candidato = lista_candidatos[lista_candidatos['Nome_Urna'] == nome]['Num_Candidato'].values[0]

        # Filtrar dados por candidato selecionado
        dados_candidato = st.session_state.get(
            "Filtro Carregado",
            filtrar_por_candidato(dataframes, num_candidato)
        )

        if len(dados_candidato) == 0:
            st.warning("Nenhum dado encontrado para os filtros selecionados.")
        else:
            st.header("📊 Desempenho do Candidato")
            grafico_votos_por_municipio(dados_candidato['votacao_candidato_municipio_zona'], dataframes['municipio'])

            st.header("🤝 Apoio Político")
            grafico_apoio_prefeito(dados_candidato['votacao_candidato_municipio_zona'], dados_candidato['apoio_prefeito_candidato'])

            # st.header("👥 Perfil do Eleitorado")
            # grafico_faixa_etaria(dataframes['perfil_eleitorado'])

            st.header("🏛️ Votos por Partido")
            grafico_votos_partido(dataframes['votos_partido_municipio'])

            st.header("📈 Comparecimento")
            grafico_comparecimento(dataframes['manifestacao_eleitorado_municipio'], dataframes['municipio'])

            st.markdown("---")
            with st.expander("Ver dados detalhados da seleção"):
                for nome_tabela, df in dados_candidato.items():
                    st.subheader(f"Tabela: {nome_tabela}")
                    st.dataframe(df, use_container_width=True)

    else:
        st.error("Não foi possível carregar os dados. Verifique a conexão e a query.")