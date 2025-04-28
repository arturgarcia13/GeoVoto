import streamlit as st
import os
import pandas
from IPython.display import display
from pathlib import Path
#import gdown
import geopandas as gpd
import pydeck as pdk
import time

caminho_shp = "/workspaces/GeoVoto/bairros_fortaleza/vw_Fortaleza_Bairros.shp"
gdf_bairros = gpd.read_file(caminho_shp)

col1,col2 = st.columns([9,2])
with col1:
    if st.button("🏠 Home"):
        with st.spinner("Redirecionando", show_time=False):
            st.switch_page("pages/home.py")
with col2:
    if st.button("🚪 Sair"):
        st.success("Bye 👋")
        #st.logout()

tab1 = st.tabs(["🌎 Mapa dos bairros"])


st.title("Mapa dos Bairros de Fortaleza")

if gdf_bairros.crs.to_epsg() != 4326:
    st.warning("CRS inadequado. Conversão em andamento...")
    gdf_bairros = gdf_bairros.to_crs(epsg=4326)
    st.write(f"CRS convertido para: {gdf_bairros.crs}")


# Criar uma nova coluna com as coordenadas das bordas
gdf_bairros["coordinates"] = gdf_bairros["geometry"].apply(lambda x: list(x.exterior.coords))

# Transformar para dataframe puro para o pydeck
df_plot = gdf_bairros[["coordinates", "Nome", "Área (ha)"]].copy()

#Calculo dos centroides para correção do mapa (apagar no proximo commit)
#gdf_temp = gdf_bairros.to_crs(epsg=3857)
#centroids = gdf_temp.geometry.centroid
#centroids = centroids.to_crs(epsg=4326)
#st.write(f"lat média: {centroids.geometry.centroid.y.mean()}")
#st.write(f"lon média: {centroids.geometry.centroid.x.mean()}")

st.pydeck_chart(
    pdk.Deck(
         map_style="mapbox://styles/mapbox/light-v9",
         initial_view_state =pdk.ViewState(
                latitude= -3.79,  # Centro aproximado
                longitude= -38.526,
                zoom=10.6,
                pitch=0
            ),
        layers =[
            pdk.Layer(
                "PolygonLayer",
                data=df_plot,
                get_polygon = "coordinates",
                get_fill_color=[71, 176, 250, 60],
                get_line_color=[0, 0, 250],
                get_line_width=2,
                line_width_min_pixels=1,
                pickable = True,
                stroked = True,
                extruded = False,
            ),
        ],
        tooltip={
            "html": "<b>Bairro:</b> {Nome} <br/> <b>Área (ha):</b> {Área (ha)}",
            "style": {
                "backgroundColor": "steelblue",
                "color": "white",
                "fontSize": "12px",
                "padding": "10px"
            }
        }
    ),
)