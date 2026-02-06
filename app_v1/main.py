import streamlit as st

from ui.dashboard import page_dashboard
from ui.login_page import page_login
from ui.app_page import page_app
import pandas as pd
import geopandas as gpd

from ui.map_utils import gerar_mapa
from database.connection import get_engine
from config.settings import app_config
from ui.manager_user import user_manager

# Configuração da página
st.set_page_config(
    page_title=app_config.app_name, 
    page_icon=app_config.app_icon, 
    initial_sidebar_state=app_config.initial_sidebar_state, 
    layout= app_config.page_layout)

@st.cache_data
def carregar_shapefile(path):
    return gpd.read_file(path)

@st.cache_data
def carregar_dados_principais(_engine):
    df_votos = pd.read_sql("SELECT * FROM votacao_candidato_municipio_zona", con=_engine)
    df_eleitores = pd.read_sql("SELECT * FROM manifestacao_eleitorado_municipio", con=_engine)
    df_candidatos = pd.read_sql(
        'SELECT DISTINCT "Num_Candidato", "Nome_Urna" FROM candidato ORDER BY "Nome_Urna"',
        con=_engine
    )
    df_partido_municipio = pd.read_sql("SELECT * FROM votos_partido_municipio", con=_engine)
    return df_votos, df_eleitores, df_candidatos, df_partido_municipio

def carregar_apoio_municipio(_engine):
    return pd.read_sql("SELECT * FROM apoio_prefeito_candidato", con=_engine)

def calcular_dados_estrategicos(df_votos, df_eleitores, df_apoio):
    df_base = df_votos[df_votos["FK_Num_Candidato"] == 1221].groupby("FK_Cod_Municipio", as_index=False).agg({
        "Votos_Nominais_Candidato": "sum"
    }).rename(columns={
        "FK_Cod_Municipio": "Cod_IBGE",
        "Votos_Nominais_Candidato": "Votos_Validos_Candidato"
    })

    df_base = pd.merge(df_base, df_eleitores.rename(columns={"FK_Cod_Municipio": "Cod_IBGE"}), on="Cod_IBGE", how="left")
    df_base = pd.merge(df_base, df_apoio.rename(columns={"FK_Cod_Municipio": "Cod_IBGE"}), on="Cod_IBGE", how="left")

    df_base["Votos_Com_Impacto"] = df_base.apply(
        lambda row: row["Votos_Validos_Candidato"] *
        (1.12 if row["Status_Apoio"] == "apoia" else 1.03 if row["Status_Apoio"] == "indeciso" else 0.95),
        axis=1
    )

    df_base["Ganho_Votos"] = df_base["Votos_Com_Impacto"] - df_base["Votos_Validos_Candidato"]
    df_base["Penetracao_Atual"] = 100 * df_base["Votos_Validos_Candidato"] / df_base["Votos_Validos_Municipio"]
    df_base["Potencial_Crescimento"] = df_base["Eleitores_Aptos"] - df_base["Votos_Validos_Candidato"]
    df_base["Eficiencia_Campanha"] = 100 * df_base["Ganho_Votos"] / df_base["Eleitores_Aptos"]

    return df_base

# Inicializa estado de login se necessário
def initialize_session_state():
    """Inicializa todas as variáveis de estado necessárias"""
    default_states = {
        "logged_in": False,
        "token_processed": False,
        "register_mode": False
    }

    for key, default_value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def do_logout():
    st.query_params.clear()  # limpa os parâmetros da URL


    # Limpa o session_state
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    # Reinsere os padrões
    initialize_session_state()

    st.rerun()

initialize_session_state()
# Verifica se o usuário está logado
if not st.session_state["logged_in"]:
    col1 , col2, col3 = st.columns([0.5, 1, 0.5])
    with col2:
        tab1, tab2 = st.tabs(["Intro", "Login"])
        with tab1:
            page_app()

        with tab2:
            page_login()

else:

    with st.sidebar:
        st.sidebar.success(f"Logado como: {st.session_state['nome']}")
        st.sidebar.title("Navegação")
        if st.button("Logout"):
            do_logout()

    tabs_admin = ["Dashboard", "Análise Geográfica", "Análise Estratégica", "Usuários"]
    tabs_user = ["Dashboard", "Análise Geográfica", "Análise Estratégica"]
    # Verifica o tipo de usuário
    if st.session_state.get("user_type") == "usuário":
        tab1, tab2, tab3 = st.tabs(tabs_user)

        with tab1:
            # Mostra o dashboard
            page_dashboard()
        with tab2:
            tipo_mapa = st.radio(
                "🗺️ Selecione o tipo de visualização",
                ["Votos por Candidato", "Votos por Partido"],
                index=0,
                horizontal=True
            )

            try:
                # Carregamento dos dados se ainda não estiverem carregados
                engine = get_engine()
                df_votos, df_eleitores, df_candidatos, df_partido_municipio = carregar_dados_principais(engine)

                shapefile_path = "app/data/Limites_municipais_Ceara_2025/Limites_municipais_IPECE_2025_utm_sirgas_2000.shp"
                gdf_municipios = carregar_shapefile(shapefile_path)
                gdf_municipios = gdf_municipios.rename(columns={"codigo_ibg": "Cod_IBGE"})

                if tipo_mapa == "Votos por Candidato":
                    nome_candidato = st.selectbox("🧑‍💼 Selecione um candidato", df_candidatos["Nome_Urna"].tolist())
                    num_candidato = df_candidatos[df_candidatos["Nome_Urna"] == nome_candidato]["Num_Candidato"].values[0]

                    df_votos_candidato = (
                        df_votos[df_votos["FK_Num_Candidato"] == num_candidato]
                        .groupby("FK_Cod_Municipio", as_index=False)
                        .agg({"Votos_Nominais_Candidato": "sum"})
                        .rename(columns={
                            "FK_Cod_Municipio": "Cod_IBGE",
                            "Votos_Nominais_Candidato": "Votos_Candidato"
                        })
                    )

                    df_eleitores_renomeado = df_eleitores.rename(columns={"FK_Cod_Municipio": "Cod_IBGE"})
                    df_merged = pd.merge(df_votos_candidato, df_eleitores_renomeado, on="Cod_IBGE", how="left")
                    df_merged["Percentual_Votos_Validos"] = (
                        100 * df_merged["Votos_Candidato"] / df_merged["Votos_Validos_Municipio"]
                    ).round(2)
                    df_merged["Percentual_Municipio_Total"] = (
                        100 * df_merged["Votos_Candidato"] / df_merged["Votos_Validos_Municipio"]
                    ).round(2)

                    gdf_final = gdf_municipios[["Cod_IBGE", "Municipio", "geometry"]].merge(df_merged, on="Cod_IBGE", how="right")
                    gdf_final = gpd.GeoDataFrame(gdf_final, geometry="geometry", crs=gdf_municipios.crs)
                    df_merged = gdf_final.drop(columns=gdf_final.select_dtypes("geometry").columns)

                    # Análise dos Top 5 Municípios com mais e menos votos
                    st.markdown("### 📊 Destaques por Município")
                    col_maiores, col_menores = st.columns(2)

                    df_top_maiores = (
                        df_merged[["Municipio", "Votos_Candidato", "Votos_Validos_Municipio", "Percentual_Municipio_Total"]]
                        .sort_values("Percentual_Municipio_Total", ascending=False)
                        .head(5)
                    )
                    df_top_menores = (
                        df_merged[["Municipio", "Votos_Candidato", "Votos_Validos_Municipio", "Percentual_Municipio_Total"]]
                        .sort_values("Percentual_Municipio_Total", ascending=True)
                        .head(5)
                    )

                    with col_maiores:
                        st.subheader("🔺 Município com Maior % de Votos")
                        st.dataframe(
                            df_top_maiores.rename(columns={
                                "Municipio": "Município",
                                "Votos_Candidato": "Votos no Candidato",
                                "Votos_Validos_Municipio": "Votos Válidos do Município",
                                "Percentual_Municipio_Total": "% do Candidato no Município"
                            }),
                            use_container_width=True
                        )

                    with col_menores:
                        st.subheader("🔻 Município com os Menores % de Votos")
                        st.dataframe(
                            df_top_menores.rename(columns={
                                "Municipio": "Município",
                                "Votos_Candidato": "Votos no Candidato",
                                "Votos_Validos_Municipio": "Votos Válidos do Município",
                                "Percentual_Municipio_Total": "% do Candidato no Município"
                            }),
                            use_container_width=True
                        )

                    st.subheader("🗺️Número de Votos em Cada Município")
                    gerar_mapa(gdf_final, tipo="candidato")

                elif tipo_mapa == "Votos por Partido":
                    partidos_disponiveis = sorted(df_partido_municipio["FK_Sigla_Partido"].dropna().unique().tolist())
                    sigla_partido = st.selectbox("🏛️ Selecione um partido", partidos_disponiveis)

                    df_votos_partido = (
                        df_partido_municipio[df_partido_municipio["FK_Sigla_Partido"] == sigla_partido]
                        .groupby("FK_Cod_Municipio", as_index=False)
                        .agg({"Votos_Nominais_Partido": "sum"})
                        .rename(columns={
                            "FK_Cod_Municipio": "Cod_IBGE",
                            "Votos_Nominais_Partido": "Votos_Partido"
                        })
                    )
                    df_votos_partido["Sigla_Partido"] = sigla_partido

                    df_eleitores_renomeado = df_eleitores.rename(columns={"FK_Cod_Municipio": "Cod_IBGE"})
                    df_merged_partido = pd.merge(df_votos_partido, df_eleitores_renomeado, on="Cod_IBGE", how="left")
                    df_merged_partido["Percentual_Votos_Validos"] = (
                        100 * df_merged_partido["Votos_Partido"] / df_merged_partido["Votos_Validos_Municipio"]
                    ).round(2)

                    df_merged_partido["Percentual_Municipio_Total"] = (
                        100 * df_merged_partido["Votos_Partido"] / df_merged_partido["Votos_Validos_Municipio"]
                    ).round(2)

                    gdf_final_partido = gdf_municipios[["Cod_IBGE", "Municipio", "geometry"]].merge(df_merged_partido, on="Cod_IBGE", how="right")
                    gdf_final_partido = gpd.GeoDataFrame(gdf_final_partido, geometry="geometry", crs=gdf_municipios.crs)
                    df_merged_partido = gdf_final_partido.drop(columns=gdf_final_partido.select_dtypes("geometry").columns)

                    st.markdown("### 📊 Destaques por Município")
                    col_maiores, col_menores = st.columns(2)

                    df_top_maiores = (
                        df_merged_partido[["Municipio", "Votos_Partido", "Votos_Validos_Municipio", "Percentual_Municipio_Total"]]
                        .sort_values("Percentual_Municipio_Total", ascending=False)
                        .head(5)
                    )
                    df_top_menores = (
                        df_merged_partido[["Municipio", "Votos_Partido", "Votos_Validos_Municipio", "Percentual_Municipio_Total"]]
                        .sort_values("Percentual_Municipio_Total", ascending=True)
                        .head(5)
                    )

                    with col_maiores:
                        st.subheader("🔺 Municípios com Maior % de Voto no Partido")
                        st.dataframe(
                            df_top_maiores.rename(columns={
                                "Municipio": "Município",
                                "Votos_Partido": "Votos no Partido",
                                "Votos_Validos_Municipio": "Votos Válidos do Município",
                                "Percentual_Municipio_Total": "% do Partido no Município"
                            }),
                            use_container_width=True
                        )

                    with col_menores:
                        st.subheader("🔻 Municípios com Menor % de Voto no Partido")
                        st.dataframe(
                            df_top_menores.rename(columns={
                                "Municipio": "Município",
                                "Votos_Partido": "Votos no Partido",
                                "Votos_Validos_Municipio": "Votos Válidos do Município",
                                "Percentual_Municipio_Total": "% do Partido no Município"
                            }),
                            use_container_width=True
                        )

                    st.subheader("🗺️ Número de Votos em Cada Município")
                    gerar_mapa(gdf_final_partido, tipo="partido", sigla=sigla_partido)

            except Exception as e:
                st.error(f"Erro ao carregar dados ou gerar mapa: {e}")
        with tab3:
            try:
                engine = get_engine()
                df_votos, df_eleitores, df_candidatos, df_partido_municipio = carregar_dados_principais(engine)
                df_apoio = carregar_apoio_municipio(engine)

                # Criação de colunas auxiliares a partir de df_eleitores
                df_extra = df_eleitores.rename(columns={"FK_Cod_Municipio": "Cod_IBGE"}).copy()
                df_extra["Comparecimento"] = df_extra["Votos_Validos_Municipio"]
                df_extra["Percentual_Comparecimento"] = (
                        100 * df_extra["Votos_Validos_Municipio"] / df_extra["Eleitores_Aptos"]
                ).round(2)
                df_extra["Brancos_Nulos"] = df_extra["Votos_Nulos_Urna"] + df_extra["Votos_Brancos"]

            except Exception as e:
                st.error(f"Erro ao carregar dados estratégicos: {e}")
                st.stop()

            with st.sidebar:
                st.markdown("### ⚙️ Ajuste de Pesos Estratégicos")
                peso_eleitorado = st.slider("Peso – Tamanho do Eleitorado", 0, 100, 30)
                peso_penetracao = st.slider("Peso – Espaço para Crescimento", 0, 100, 25)
                peso_potencial = st.slider("Peso – Potencial Absoluto", 0, 100, 25)
                peso_eficiencia = st.slider("Peso – Eficiência da Campanha", 0, 100, 20)

            soma_pesos = peso_eleitorado + peso_penetracao + peso_potencial + peso_eficiencia
            if soma_pesos != 100:
                st.warning("A soma dos pesos deve ser 100%. Ajuste para continuar.")
                st.stop()

            # Calcula df_estrategia
            df_estrategia = calcular_dados_estrategicos(df_votos, df_eleitores, df_apoio)


            # Score estratégico
            df_estrategia["Score_Estrategico"] = (
                                                        peso_eleitorado * df_estrategia["Eleitores_Aptos"].rank(
                                                    ascending=False, pct=True) +
                                                        peso_penetracao * (100 - df_estrategia["Penetracao_Atual"]).rank(
                                                    ascending=False, pct=True) +
                                                        peso_potencial * df_estrategia["Potencial_Crescimento"].rank(
                                                    ascending=False, pct=True) +
                                                        peso_eficiencia * df_estrategia["Eficiencia_Campanha"].rank(
                                                    ascending=False, pct=True)
                                                ) / 100

            df_estrategia["Posicao_Ranking"] = df_estrategia["Score_Estrategico"].rank(ascending=False).astype(int)

            st.markdown("### 🥇 Top Municípios Estratégicos")
            with st.expander("Ver detalhes"):
                st.dataframe(df_estrategia.sort_values("Score_Estrategico", ascending=False).head(10),
                            use_container_width=True, height=300, hide_index=True)
            
            st.markdown("### 🥄 Municípios com Menor Prioridade Estratégica")
            with st.expander("Ver detalhes"):
                st.dataframe(df_estrategia.sort_values("Score_Estrategico", ascending=True).head(10),
                            use_container_width=True, height=300, hide_index=True)

            # Mapa (ainda não implementado aqui)
            st.info("🗺️ Mapa de ranking será adicionado na próxima etapa.")
    
    else:
        tab1, tab2, tab3, tab4 = st.tabs(tabs_admin) 

        with tab1:
            # Mostra o dashboard
            page_dashboard()
        with tab2:
            tipo_mapa = st.radio(
                "🗺️ Selecione o tipo de visualização",
                ["Votos por Candidato", "Votos por Partido"],
                index=0,
                horizontal=True
            )

            try:
                # Carregamento dos dados se ainda não estiverem carregados
                engine = get_engine()
                df_votos, df_eleitores, df_candidatos, df_partido_municipio = carregar_dados_principais(engine)

                shapefile_path = "app/data/Limites_municipais_Ceara_2025/Limites_municipais_IPECE_2025_utm_sirgas_2000.shp"
                gdf_municipios = carregar_shapefile(shapefile_path)
                gdf_municipios = gdf_municipios.rename(columns={"codigo_ibg": "Cod_IBGE"})

                if tipo_mapa == "Votos por Candidato":
                    nome_candidato = st.selectbox("🧑‍💼 Selecione um candidato", df_candidatos["Nome_Urna"].tolist())
                    num_candidato = df_candidatos[df_candidatos["Nome_Urna"] == nome_candidato]["Num_Candidato"].values[0]

                    df_votos_candidato = (
                        df_votos[df_votos["FK_Num_Candidato"] == num_candidato]
                        .groupby("FK_Cod_Municipio", as_index=False)
                        .agg({"Votos_Nominais_Candidato": "sum"})
                        .rename(columns={
                            "FK_Cod_Municipio": "Cod_IBGE",
                            "Votos_Nominais_Candidato": "Votos_Candidato"
                        })
                    )

                    df_eleitores_renomeado = df_eleitores.rename(columns={"FK_Cod_Municipio": "Cod_IBGE"})
                    df_merged = pd.merge(df_votos_candidato, df_eleitores_renomeado, on="Cod_IBGE", how="left")
                    df_merged["Percentual_Votos_Validos"] = (
                        100 * df_merged["Votos_Candidato"] / df_merged["Votos_Validos_Municipio"]
                    ).round(2)
                    df_merged["Percentual_Municipio_Total"] = (
                        100 * df_merged["Votos_Candidato"] / df_merged["Votos_Validos_Municipio"]
                    ).round(2)

                    gdf_final = gdf_municipios[["Cod_IBGE", "Municipio", "geometry"]].merge(df_merged, on="Cod_IBGE", how="right")
                    gdf_final = gpd.GeoDataFrame(gdf_final, geometry="geometry", crs=gdf_municipios.crs)
                    df_merged = gdf_final.drop(columns=gdf_final.select_dtypes("geometry").columns)

                    # Análise dos Top 5 Municípios com mais e menos votos
                    st.markdown("### 📊 Destaques por Município")
                    col_maiores, col_menores = st.columns(2)

                    df_top_maiores = (
                        df_merged[["Municipio", "Votos_Candidato", "Votos_Validos_Municipio", "Percentual_Municipio_Total"]]
                        .sort_values("Percentual_Municipio_Total", ascending=False)
                        .head(5)
                    )
                    df_top_menores = (
                        df_merged[["Municipio", "Votos_Candidato", "Votos_Validos_Municipio", "Percentual_Municipio_Total"]]
                        .sort_values("Percentual_Municipio_Total", ascending=True)
                        .head(5)
                    )

                    with col_maiores:
                        st.subheader("🔺 Município com Maior % de Votos")
                        st.dataframe(
                            df_top_maiores.rename(columns={
                                "Municipio": "Município",
                                "Votos_Candidato": "Votos no Candidato",
                                "Votos_Validos_Municipio": "Votos Válidos do Município",
                                "Percentual_Municipio_Total": "% do Candidato no Município"
                            }),
                            use_container_width=True
                        )

                    with col_menores:
                        st.subheader("🔻 Município com os Menores % de Votos")
                        st.dataframe(
                            df_top_menores.rename(columns={
                                "Municipio": "Município",
                                "Votos_Candidato": "Votos no Candidato",
                                "Votos_Validos_Municipio": "Votos Válidos do Município",
                                "Percentual_Municipio_Total": "% do Candidato no Município"
                            }),
                            use_container_width=True
                        )

                    st.subheader("🗺️Número de Votos em Cada Município")
                    gerar_mapa(gdf_final, tipo="candidato")

                elif tipo_mapa == "Votos por Partido":
                    partidos_disponiveis = sorted(df_partido_municipio["FK_Sigla_Partido"].dropna().unique().tolist())
                    sigla_partido = st.selectbox("🏛️ Selecione um partido", partidos_disponiveis)

                    df_votos_partido = (
                        df_partido_municipio[df_partido_municipio["FK_Sigla_Partido"] == sigla_partido]
                        .groupby("FK_Cod_Municipio", as_index=False)
                        .agg({"Votos_Nominais_Partido": "sum"})
                        .rename(columns={
                            "FK_Cod_Municipio": "Cod_IBGE",
                            "Votos_Nominais_Partido": "Votos_Partido"
                        })
                    )
                    df_votos_partido["Sigla_Partido"] = sigla_partido

                    df_eleitores_renomeado = df_eleitores.rename(columns={"FK_Cod_Municipio": "Cod_IBGE"})
                    df_merged_partido = pd.merge(df_votos_partido, df_eleitores_renomeado, on="Cod_IBGE", how="left")
                    df_merged_partido["Percentual_Votos_Validos"] = (
                        100 * df_merged_partido["Votos_Partido"] / df_merged_partido["Votos_Validos_Municipio"]
                    ).round(2)

                    df_merged_partido["Percentual_Municipio_Total"] = (
                        100 * df_merged_partido["Votos_Partido"] / df_merged_partido["Votos_Validos_Municipio"]
                    ).round(2)

                    gdf_final_partido = gdf_municipios[["Cod_IBGE", "Municipio", "geometry"]].merge(df_merged_partido, on="Cod_IBGE", how="right")
                    gdf_final_partido = gpd.GeoDataFrame(gdf_final_partido, geometry="geometry", crs=gdf_municipios.crs)
                    df_merged_partido = gdf_final_partido.drop(columns=gdf_final_partido.select_dtypes("geometry").columns)

                    st.markdown("### 📊 Destaques por Município")
                    col_maiores, col_menores = st.columns(2)

                    df_top_maiores = (
                        df_merged_partido[["Municipio", "Votos_Partido", "Votos_Validos_Municipio", "Percentual_Municipio_Total"]]
                        .sort_values("Percentual_Municipio_Total", ascending=False)
                        .head(5)
                    )
                    df_top_menores = (
                        df_merged_partido[["Municipio", "Votos_Partido", "Votos_Validos_Municipio", "Percentual_Municipio_Total"]]
                        .sort_values("Percentual_Municipio_Total", ascending=True)
                        .head(5)
                    )

                    with col_maiores:
                        st.subheader("🔺 Municípios com Maior % de Voto no Partido")
                        st.dataframe(
                            df_top_maiores.rename(columns={
                                "Municipio": "Município",
                                "Votos_Partido": "Votos no Partido",
                                "Votos_Validos_Municipio": "Votos Válidos do Município",
                                "Percentual_Municipio_Total": "% do Partido no Município"
                            }),
                            use_container_width=True
                        )

                    with col_menores:
                        st.subheader("🔻 Municípios com Menor % de Voto no Partido")
                        st.dataframe(
                            df_top_menores.rename(columns={
                                "Municipio": "Município",
                                "Votos_Partido": "Votos no Partido",
                                "Votos_Validos_Municipio": "Votos Válidos do Município",
                                "Percentual_Municipio_Total": "% do Partido no Município"
                            }),
                            use_container_width=True
                        )

                    st.subheader("🗺️ Número de Votos em Cada Município")
                    gerar_mapa(gdf_final_partido, tipo="partido", sigla=sigla_partido)

            except Exception as e:
                st.error(f"Erro ao carregar dados ou gerar mapa: {e}")
        with tab3:
            try:
                engine = get_engine()
                df_votos, df_eleitores, df_candidatos, df_partido_municipio = carregar_dados_principais(engine)
                df_apoio = carregar_apoio_municipio(engine)

                # Criação de colunas auxiliares a partir de df_eleitores
                df_extra = df_eleitores.rename(columns={"FK_Cod_Municipio": "Cod_IBGE"}).copy()
                df_extra["Comparecimento"] = df_extra["Votos_Validos_Municipio"]
                df_extra["Percentual_Comparecimento"] = (
                        100 * df_extra["Votos_Validos_Municipio"] / df_extra["Eleitores_Aptos"]
                ).round(2)
                df_extra["Brancos_Nulos"] = df_extra["Votos_Nulos_Urna"] + df_extra["Votos_Brancos"]

            except Exception as e:
                st.error(f"Erro ao carregar dados estratégicos: {e}")
                st.stop()

            with st.sidebar:
                st.markdown("### ⚙️ Ajuste de Pesos Estratégicos")
                peso_eleitorado = st.slider("Peso – Tamanho do Eleitorado", 0, 100, 30)
                peso_penetracao = st.slider("Peso – Espaço para Crescimento", 0, 100, 25)
                peso_potencial = st.slider("Peso – Potencial Absoluto", 0, 100, 25)
                peso_eficiencia = st.slider("Peso – Eficiência da Campanha", 0, 100, 20)

            soma_pesos = peso_eleitorado + peso_penetracao + peso_potencial + peso_eficiencia
            if soma_pesos != 100:
                st.warning("A soma dos pesos deve ser 100%. Ajuste para continuar.")
                st.stop()

            # Calcula df_estrategia
            df_estrategia = calcular_dados_estrategicos(df_votos, df_eleitores, df_apoio)


            # Score estratégico
            df_estrategia["Score_Estrategico"] = (
                                                        peso_eleitorado * df_estrategia["Eleitores_Aptos"].rank(
                                                    ascending=False, pct=True) +
                                                        peso_penetracao * (100 - df_estrategia["Penetracao_Atual"]).rank(
                                                    ascending=False, pct=True) +
                                                        peso_potencial * df_estrategia["Potencial_Crescimento"].rank(
                                                    ascending=False, pct=True) +
                                                        peso_eficiencia * df_estrategia["Eficiencia_Campanha"].rank(
                                                    ascending=False, pct=True)
                                                ) / 100

            df_estrategia["Posicao_Ranking"] = df_estrategia["Score_Estrategico"].rank(ascending=False).astype(int)

            st.markdown("### 🥇 Top Municípios Estratégicos")
            with st.expander("Ver detalhes"):
                st.dataframe(df_estrategia.sort_values("Score_Estrategico", ascending=False).head(10),
                            use_container_width=True, height=300, hide_index=True)
            
            st.markdown("### 🥄 Municípios com Menor Prioridade Estratégica")
            with st.expander("Ver detalhes"):
                st.dataframe(df_estrategia.sort_values("Score_Estrategico", ascending=True).head(10),
                            use_container_width=True, height=300, hide_index=True)

            # Mapa (ainda não implementado aqui)
            st.info("🗺️ Mapa de ranking será adicionado na próxima etapa.")
        with tab4:
            user_manager()