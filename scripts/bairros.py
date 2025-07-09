import streamlit as st
import pydeck as pdk
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from app.data.preparadores.preparar_dados_mapa_bairro import preparar_dados_mapa_bairro
from app.ui.convert_colors import hex_to_rgb


df_plot = preparar_dados_mapa_bairro()

col1, col2 = st.columns([9, 2])
with col1:
    if st.button("🏠 Home"):
        with st.spinner("Redirecionando", show_time=False):
            st.switch_page("pages/home.py")
with col2:
    if st.button("🚪 Sair"):
        st.success("Bye 👋")
        # st.logout()

tab1, = st.tabs(["🌎 Mapa dos bairros"])
with tab1:
    st.title("Mapa dos Bairros de Fortaleza")

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        mostrar_mapa = st.toggle("Visualizar Mapa", value=True)
    with col2:
        mostrar_bairro = st.toggle("Visualizar Bairros", value=False) if mostrar_mapa else False

    if mostrar_mapa and mostrar_bairro:
        color_hex = st.color_picker("Cor dos Bairros", "#47B0FA")
        color_rgba = hex_to_rgb(color_hex)
    
    if mostrar_mapa:
        st.pydeck_chart(
            pdk.Deck(
                map_style="mapbox://styles/mapbox/light-v9",
                initial_view_state=pdk.ViewState(
                    latitude=-3.79,
                    longitude=-38.526,
                    zoom=10.6,
                    pitch=0
                ),
                layers=[
                    pdk.Layer(
                        "PolygonLayer",
                        data=df_plot,
                        get_polygon="coordinates",
                        get_fill_color=color_rgba,
                        get_line_color=[0, 0, 250],
                        get_line_width=2,
                        line_width_min_pixels=1,
                        pickable=True,
                        stroked=True,
                        extruded=False,
                    ),
                ] if mostrar_bairro else None,
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
            use_container_width=True
        )
