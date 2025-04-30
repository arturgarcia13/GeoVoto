import streamlit as st
import geopandas as gpd

import os

@st.cache_data
def carregar_bairros_fortaleza():
    caminho_shp = os.path.join("data", "bairros_fortaleza", "vw_Fortaleza_Bairros.shp")
    gdf = gpd.read_file(caminho_shp)
    if gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)
    return gdf