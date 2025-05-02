## 1. Introdução

No primeiro mês de projeto, dedicamo-nos a avaliar, instalar, configurar e aplicar quatro bibliotecas Python fundamentais para o desenvolvimento de um dashboard geoespacial de bairros de Fortaleza: **Streamlit**, **GeoPandas**, **PyDeck** e **pandas**. O objetivo desta etapa foi construir um protótipo funcional que permita carregar dados geoespaciais, aplicar filtros interativos e exibir mapas vetoriais em uma interface web leve.

## 2. Ambiente de Desenvolvimento

- **Sistema Operacional:** Ubuntu 22.04 LTS  
- **Versão do Python:** 3.10.x  
- **Gerenciador de pacotes:** `pip` (via ambiente virtual `venv`)  

### 2.1 Criação do ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Instalação e Configuração das Bibliotecas

Exemplos de comandos de instalação, realizados pelo time:

```bash
pip install streamlit           # Framework para apps web interativos
pip install geopandas           # Manipulação de dados geoespaciais
pip install pydeck              # Visualização 3D/2D baseada em deck.gl
pip install pandas              # Manipulação de tabelas e CSV
pip install ipython             # Para uso de display em notebooks, se necessário
```

Em seguida, foi validado que cada biblioteca estivesse corretamente disponível:

```python
import streamlit as st
import geopandas as gpd
import pydeck as pdk
import pandas as pd
```

## 4. Descrição do Código e Fluxo de Aplicação

O script principal (`app.py`) implementa as seguintes etapas:

1. **Leitura do shapefile**  
   Utilizamos o GeoPandas para carregar a camada de bairros de Fortaleza:  
   ```python
   caminho_shp = "bairros_fortaleza/vw_Fortaleza_Bairros.shp"
   gdf_bairros = gpd.read_file(caminho_shp)
   ```
2. **Verificação e conversão de CRS**  
   Garantimos que o sistema de referência de coordenadas seja EPSG:4326 (WGS84):  
   ```python
   if gdf_bairros.crs.to_epsg() != 4326:
       gdf_bairros = gdf_bairros.to_crs(epsg=4326)
   ```
3. **Extração das coordenadas das bordas**  
   Criamos uma coluna `coordinates` com as listas de vértices de cada polígono:  
   ```python
   gdf_bairros["coordinates"] = gdf_bairros.geometry.apply(lambda x: list(x.exterior.coords))
   ```
4. **Interface Streamlit**  
   - **Barra de navegação:** botões “Home” e “Sair” dispostos em colunas responsivas.  
   - **Tabs:** uso de `st.tabs` para organizar diferentes visões (inicialmente apenas “Mapa dos bairros”).  
   - **Título e avisos:**  
     ```python
     st.title("Mapa dos Bairros de Fortaleza")
     st.warning("CRS inadequado. Conversão em andamento...")
     ```
5. **Dropdown de filtros**  
   Lista ordenada de bairros obtida de `gdf_bairros["Nome"].unique()`, permitindo seleção de um bairro ou todos.  
6. **Preparação dos dados para plot**  
   Convertemos o GeoDataFrame filtrado em um DataFrame puro (`df_plot`) contendo apenas `coordinates`, `Nome` e `Área (ha)`.  
7. **Toggles de camadas**  
   Dois switches (`st.toggle`) para ativar/desativar o mapa base e a camada de polígonos de bairros.  
8. **Construção do mapa com PyDeck**  
   - **PolygonLayer:** cor de preenchimento semitransparente e contorno azul.  
   - **ViewState inicial:** centrado em latitude –3.79, longitude –38.526 (Fortaleza), zoom 10.6.  
   - **Tooltip customizado:** exibe nome do bairro e área em hectares ao passar o mouse.  
   ```python
   pdk.Layer(
     "PolygonLayer",
     data=df_plot,
     get_polygon="coordinates",
     get_fill_color=[71,176,250,60],
     get_line_color=[0,0,250],
     pickable=True,
     stroked=True,
   )
   ```

## 5. Atividades da Equipe no Primeiro Mês

| Membro             | Atividade Principal                                                                                      |
|--------------------|----------------------------------------------------------------------------------------------------------|
| **Artur Garcia, Artur Saraiva, Iuri Sales, Letícia Frota, Lucas Lopes**     | • Pesquisa e seleção das bibliotecas adequadas;<br>• Criação e configuração do ambiente virtual (venv);<br>• Documentação inicial dos comandos de instalação. |
| **Lucas Lopes, Letícia Frota** | • Estudo dos formatos de arquivo geoespaciais (shapefile);<br>• Carregamento e pré-processamento de dados com GeoPandas;<br>• Tratamento de CRSs e geração de coluna `coordinates`. |
| **Artur Garcia, Artur Saraiva, Iuri Sales, Letícia Frota, Lucas Lopes**  | • Desenvolvimento da interface web com Streamlit;<br>• Implementação de navegação (botões, abas e dropdown);<br>• Testes de responsividade e layout. |
| **Artur Garcia, Artur Saraiva, Iuri Sales, Letícia Frota, Lucas Lopes**    | • Configuração e teste das camadas de visualização em PyDeck;<br>• Customização do estilo do mapa e tooltips;<br>|

## 6. Conclusão

No decorrer do primeiro mês, a equipe estabeleceu com sucesso o fluxo completo: desde a instalação das bibliotecas essenciais até a implementação prototípica de um mapa interativo de bairros. Cada membro contribuiu de forma especializada para garantir robustez no carregamento de dados, clareza na interface e qualidade na visualização geoespacial. Nas próximas etapas, planejamos:

1. Integrar fontes de dados adicionais (por ex. população, infraestrutura).  
2. Ampliar interatividade (filtros por área, estatísticas em tempo real).  
3. Documentar e versionar o código no repositório GitHub.  

Com essa base, avançaremos para o desenvolvimento de análises mais complexas e relatórios automatizados para stakeholders.
