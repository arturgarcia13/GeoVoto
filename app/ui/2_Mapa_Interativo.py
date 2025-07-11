import streamlit as st
import geopandas as gpd
import pandas as pd
import pydeck as pdk
from database.connection import get_engine
import folium
from folium.plugins import Fullscreen
from streamlit_folium import st_folium
from ui.map_utils import gerar_mapa

st.title("🗺️ Mapa Interativo – Diagnóstico Inicial")

@st.cache_data()
def carregar_shapefile(path):
    return gpd.read_file(path)

# --- 1. Carregar shapefile dos municípios ---
shapefile_path = "app/data/Limites_municipais_Ceara_2025/Limites_municipais_IPECE_2025_utm_sirgas_2000.shp"

try:
    gdf_municipios = carregar_shapefile(shapefile_path)
    st.success("✅ Shapefile carregado com sucesso")
except Exception as e:
    st.error(f"Erro ao carregar shapefile: {e}")
    st.stop()

# Verifica CRS original
st.write("📌 CRS original do shapefile:", gdf_municipios.crs)
if gdf_municipios.crs is None or gdf_municipios.crs.to_epsg() != 4326:
    gdf_municipios = gdf_municipios.to_crs(epsg=4326)
    st.success("✅ Reprojetado para EPSG:4326")

# Exibir colunas e amostra
st.write("🧩 Colunas do shapefile:", gdf_municipios.columns.tolist())
st.dataframe(gdf_municipios.head())

# --- 2. Conectar ao PostgreSQL e importar dados ---
engine = get_engine()
if engine is None:
    st.error("❌ Falha ao conectar ao banco de dados")
    st.stop()

@st.cache_data
def carregar_dados_postgres(_engine):
    df_votos = pd.read_sql("SELECT * FROM votacao_candidato_municipio_zona", con=_engine)
    df_eleitores = pd.read_sql("SELECT * FROM manifestacao_eleitorado_municipio", con=_engine)
    df_candidatos = pd.read_sql(
        'SELECT DISTINCT "Num_Candidato", "Nome_Urna" FROM candidato ORDER BY "Nome_Urna"',
        con=_engine
    )
    return df_votos, df_eleitores, df_candidatos

try:
    df_votos, df_eleitores, df_candidatos = carregar_dados_postgres(_engine=engine)
    st.success("✅ Dados do PostgreSQL carregados com sucesso")
    # --- 2.1 Dropdown para seleção de candidato ---

    tipo_mapa = st.radio(
        "🗺️ Selecione o tipo de visualização",
        ["Votos por Candidato", "Votos por Partido"],
        index=0,
        horizontal=True
    )

    if tipo_mapa == "Votos por Candidato":
        # Dropdown para seleção
        nome_candidato = st.selectbox("🧑‍💼 Selecione um candidato", df_candidatos["Nome_Urna"].tolist())

        # Recupera o número do candidato selecionado
        num_candidato = df_candidatos[df_candidatos["Nome_Urna"] == nome_candidato]["Num_Candidato"].values[0]

        # Exibe como debug
        st.write(f"🎯 Candidato selecionado: {nome_candidato} ({num_candidato})")
        # --- 2.2 Agrupar votos por município para o candidato selecionado ---
        df_votos_candidato = (
            df_votos[df_votos["FK_Num_Candidato"] == num_candidato]
            .groupby("FK_Cod_Municipio", as_index=False)
            .agg({"Votos_Nominais_Candidato": "sum"})
            .rename(columns={
                "FK_Cod_Municipio": "Cod_IBGE",
                "Votos_Nominais_Candidato": "Votos_Candidato"
            })
        )
        # --- 2.3 Merge com dados de eleitorado ---
        df_eleitores_renomeado = df_eleitores.rename(columns={"FK_Cod_Municipio": "Cod_IBGE"})

        df_merged = pd.merge(df_votos_candidato, df_eleitores_renomeado, on="Cod_IBGE", how="left")
        df_merged["Percentual_Votos_Validos"] = (
                100 * df_merged["Votos_Candidato"] / df_merged["Votos_Validos_Municipio"]
        ).round(2)
        df_merged["Percentual_Municipio_Total"] = (
            100 * df_merged["Votos_Candidato"] / df_merged["Votos_Validos_Municipio"]
        ).round(2)

        # Debug do merge
        st.write("📌 df_merged – Votos + eleitorado")
        st.dataframe(df_merged.head())

        # --- 2.4 Merge com shapefile (GeoDataFrame) ---
        gdf_municipios = gdf_municipios.rename(columns={"codigo_ibg": "Cod_IBGE"})  # se ainda não tiver renomeado
        gdf_final = gdf_municipios[["Cod_IBGE", "Municipio", "geometry"]].merge(df_merged, on="Cod_IBGE", how="right")
        gdf_final = gpd.GeoDataFrame(gdf_final, geometry="geometry", crs=gdf_municipios.crs)

        # Análise dos Top 5 Municípios com mais e menos votos
        st.markdown("### 📊 Destaques por Município")
        col_maiores, col_menores = st.columns(2)

        df_top_maiores = (
            df_merged[["Cod_IBGE", "Municipio", "Votos_Candidato", "Votos_Validos_Municipio", "Percentual_Municipio_Total"]]
            .sort_values("Percentual_Municipio_Total", ascending=False)
            .head(5)
        )
        df_top_menores = (
            df_merged[["Cod_IBGE", "Municipio", "Votos_Candidato", "Votos_Validos_Municipio", "Percentual_Municipio_Total"]]
            .sort_values("Percentual_Municipio_Total", ascending=True)
            .head(5)
        )

        with col_maiores:
            st.subheader("🔝 Município com os Maiores % de Votos")
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

        st.subheader("🗺️ Votos por Candidato em Cada Município")
        st_data = gerar_mapa(gdf_final, tipo="candidato")
        df_merged = gdf_final.drop(columns=gdf_final.select_dtypes("geometry").columns)

        # Debug visual
        st.write("🗺️ gdf_final – GeoDataFrame com dados de votos")
        st.dataframe(
            gdf_final[["Municipio", "Votos_Candidato", "Percentual_Votos_Validos", "Eleitores_Aptos", "Abstencao"]].head())
        # Debug: mostrar amostra dos votos agregados
        st.write("📊 Votos do candidato por município")
        st.dataframe(df_votos_candidato.head())

    elif tipo_mapa == "Votos por Partido":
        sigla_partido = st.selectbox("🧾 Selecione o partido", df_votos["Sigla_Partido"].unique())
        df_votos_partido = (
            df_votos[df_votos["Sigla_Partido"] == sigla_partido]
            .groupby("FK_Cod_Municipio", as_index=False)
            .agg({"Votos_Nominais_Candidato": "sum"})
            .rename(columns={
                "FK_Cod_Municipio": "Cod_IBGE",
                "Votos_Nominais_Candidato": "Votos_Partido"
            })
        )
        df_votos_partido["Sigla_Partido"] = sigla_partido

        df_eleitores_renomeado = df_eleitores.rename(columns={"FK_Cod_Municipio": "Cod_IBGE"})
        df_merged_partido = pd.merge(df_votos_partido, df_eleitores_renomeado, on="Cod_IBGE", how="left")
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
    st.error(f"Erro ao carregar dados do PostgreSQL: {e}")
    st.stop()

# Debug: mostrar info dos DataFrames
st.write("📊 df_votos – Votação por candidato por município")
st.dataframe(df_votos.head())

st.write("🧾 df_eleitores – Eleitorado e abstenções")
st.dataframe(df_eleitores.head())