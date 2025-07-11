import folium
from folium import Map, Choropleth, GeoJson, LayerControl
from folium.plugins import Fullscreen
from streamlit_folium import st_folium

def gerar_mapa(gdf_final, tipo="candidato", sigla=None):

    lat_center = -5.2
    lon_center = -39 if tipo == "candidato" else -36

    gdf_final = gdf_final.to_crs(epsg=4326)
    geojson_data = gdf_final.to_json()

    m = Map(location=[lat_center, lon_center], zoom_start=7, tiles=None)
    Fullscreen(position="topleft", title="Tela cheia", title_cancel="Sair da tela cheia").add_to(m)

    if tipo == "candidato":
        nome_layer = "Votos por Município"
        coluna_valor = "Votos_Candidato"
        legenda = "Votos por Município"
    else:
        nome_layer = f"Votos do {sigla}"
        coluna_valor = "Votos_Partido"
        legenda = f"Votos do {sigla}"

    Choropleth(
        geo_data=geojson_data,
        name=nome_layer,
        data=gdf_final,
        columns=["Cod_IBGE", coluna_valor],
        key_on="feature.properties.Cod_IBGE",
        fill_color="YlOrRd" if tipo == "candidato" else "BuPu",
        fill_opacity=0.7,
        line_opacity=0.4,
        line_color="gray",
        line_weight=0.7,
        legend_name=legenda,
        nan_fill_color="gray"
    ).add_to(m)

    tooltip_fields = ["Municipio", coluna_valor, "Percentual_Votos_Validos", "Eleitores_Aptos", "Abstencao"]
    tooltip_aliases = ["Município", "Votos", "% Votos Válidos", "Eleitores Aptos", "Abstenções"]

    if tipo == "partido":
        tooltip_fields.insert(1, "Sigla_Partido")
        tooltip_aliases.insert(1, "Partido")

    GeoJson(
        geojson_data,
        name="Municípios",
        style_function=lambda feature: {
            "fillColor": "#555555",
            "color": "#666666",
            "weight": 0.5,
            "fillOpacity": 0.3,
            "opacity": 0.6,
        },
        tooltip=folium.features.GeoJsonTooltip(
            fields=tooltip_fields,
            aliases=tooltip_aliases,
            localize=True,
            sticky=True
        )
    ).add_to(m)

    LayerControl(position="bottomleft").add_to(m)
    return st_folium(m, width=1400, height=600)