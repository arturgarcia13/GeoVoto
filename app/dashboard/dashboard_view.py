# app/dashboard/dashboard_view.py

import streamlit as st
from .data_loader import load_data
from components.kpis import show_kpis
from components.charts import grafico_top_candidatos, grafico_partidos
from components.filters import aplicar_filtros


def build_dashboard(engine):
    """Constrói e exibe o dashboard principal."""
    df = load_data(engine)

    st.sidebar.success(f"Logado como: {st.session_state.email}")
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.title("📊 Dashboard de Análise Eleitoral")
    st.markdown("Use os filtros na barra lateral para explorar os resultados.")

    if not df.empty:
        df_filtrado = aplicar_filtros(df)

        if df_filtrado.empty:
            st.warning("Nenhum dado encontrado para os filtros selecionados.")
        else:
            show_kpis(df_filtrado)
            st.markdown("---")

            col_graf1, col_graf2 = st.columns(2)
            with col_graf1:
                grafico_top_candidatos(df_filtrado)
            with col_graf2:
                grafico_partidos(df_filtrado)

            st.markdown("---")

            with st.expander("Ver dados detalhados da seleção"):
                st.dataframe(df_filtrado, use_container_width=True)
    else:
        st.error("Não foi possível carregar os dados. Verifique a conexão e a query.")