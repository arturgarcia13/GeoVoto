import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from app.data.carga_dados import carregar_bairros_fortaleza

def preparar_dados_mapa_bairro():
    gdf_bairros = carregar_bairros_fortaleza()
    gdf_bairros["coordinates"] = gdf_bairros["geometry"].apply(lambda x: list(x.exterior.coords))
    df_plot = gdf_bairros[["coordinates", "Nome", "Área (ha)"]].copy()
    return df_plot
