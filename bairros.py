import streamlit as st
import os
import pandas
from IPython.display import display
from pathlib import Path
import gdown
import geopandas as gpd
import pydeck as pdk


caminho_shp = "/workspaces/GeoVoto/bairros_fortaleza/vw_Fortaleza_Bairros.shp"
gdf_bairros = gpd.read_file(caminho_shp)

st.title("Mapa dos Bairros de Fortaleza")
#st.success(f"Dados carregados {len(gdf_bairros["Nome"])}")
st.write(f"CRS original: {gdf_bairros.crs}")
if gdf_bairros.crs.to_epsg() != 4326:
    gdf_bairros = gdf_bairros.to_crs(epsg = 4326)
# Converter as geometrias para formato que o pydeck entende
# Criar uma nova coluna com as coordenadas das bordas
gdf_bairros["coordinates"] = gdf_bairros["geometry"].apply(lambda x: list(x.exterior.coords))

# Transformar para dataframe puro para o pydeck
df_plot = gdf_bairros[["coordinates"]].copy()

 

st.pydeck_chart(
    pdk.Deck(
        initial_view_state = 
            pdk.ViewState(
                latitude=gdf_bairros.geometry.centroid.y.mean(),  # Centro aproximado
                longitude=gdf_bairros.geometry.centroid.x.mean(),
                zoom=11,
                pitch=0
                ),
        map_style="mapbox://styles/mapbox/light-v9"
    ),
        layers = 
            [pdk.Layer(
                "Poligonos",
                df_plot,
                get_polygon = "coordinates",
                get_fill_color="[71, 176, 250, 60]",
                get_line_color="[90, 150, 186]",
                pickable = True,
                strocked = True,
                extruded = False,
                )],
)


