# Arquitetura e Funcionamento do Projeto GeoVoto

Este documento descreve a arquitetura, os pontos de entrada, os principais módulos e o fluxo de execução da aplicação GeoVoto presente neste repositório.

> Observação: o repositório contém múltiplas variantes da aplicação. As duas principais que identifiquei são:

- A versão refatorada/empacotada em `src/geovoto` (usada pelo `run.py`).
- Uma versão mais direta/legada em `app_v1` (interface Streamlit com lógica embutida).

**Conteúdo**

- Visão Geral
- Pontos de Entrada
- Estrutura de Pastas
- Componentes Principais
- Fluxo de Execução
- Banco de Dados e Consultas Relevantes
- Configuração e Variáveis de Ambiente
- Como Rodar
- Observações e Recomendações

---

## Visão Geral

GeoVoto é uma aplicação de análise e visualização geoespacial de dados eleitorais construída principalmente com Streamlit, pandas/geopandas e uma camada de persistência em PostgreSQL. O código contém uma implementação mais madura em `src/geovoto` (arquitetura em camadas) e uma implementação funcional em `app_v1` (mais direta), usada para desenvolvimento rápido.

## Pontos de Entrada

- `run.py` — Script helper que executa `src/geovoto/main.py` via `streamlit run`. (Recomendado para rodar a versão empacotada)
- `src/geovoto/main.py` — Entrypoint principal da versão organizada (inicializa sessão, layouts e serviços).
- `app_v1/main.py` — Versão alternativa/legada que monta a UI Streamlit diretamente (válida para desenvolvimento local rápido).

## Estrutura de Pastas (resumo)

- `src/geovoto/` — Implementação refatorada (camadas: config, core, domain, services, infrastructure, ui, utils).
- `app_v1/` — Implementação mais monolítica com páginas Streamlit, `auth`, `ui`, `database`, `config`.
- `legacy_app/` — Código legado / histórico.
- `data/` — Dados geoespaciais (shapefiles) e outros artefatos.
- `docs/` — Documentos (aqui foi adicionado este arquivo).
- `pyproject.toml` — Dependências e configuração do projeto.

## Componentes Principais

- UI (Streamlit)
  - `app_v1/ui/*` e `src/geovoto/ui/*`: páginas, layouts e componentes. Fornece telas de login, dashboard, mapas e gerenciamento de usuários.
  - Módulos de interesse: `login_page`, `dashboard`, `app_page`, `manager_user`, `map_utils`.

- Autenticação
  - Abordagem: login via token (UUID) enviado por email/gerado; token validado contra a tabela `usuarios`.
  - Implementações: `app_v1/auth/*` e `src/geovoto/services/auth_service.py` + `infrastructure.database.user_repository`.

- Banco de Dados
  - Conexão via SQLAlchemy: `app_v1/database/connection.py` e `src/geovoto/infrastructure/database/connection`.
  - A URL de conexão é obtida de `st.secrets["POSTGRES_URL"]` (versão `app_v1`) ou via `Settings`/variáveis de ambiente na versão em `src`.

- Serviços de Dados
  - `src/geovoto/services/data_service.py`: encapsula consultas SQL, carregamento e transformação com caching (decorators `cache_static`, `cache_semi_static`, `cache_dynamic`).
  - Em `app_v1/main.py` existem funções com `@st.cache_data` para operações de leitura de shapefile e consultas SQL diretas para montagem do dashboard.

- Mapas
  - `app_v1/ui/map_utils.py` usa Folium + `streamlit_folium` para renderizar mapas interativos a partir de GeoDataFrames.
  - A versão `src` centraliza leitura de geodados em `DataService.get_geographic_data` e já normaliza CRS e simplifica geometrias.

- Repositório de Usuários / Queries
  - `app_v1/database/queries.py` e `src/geovoto/infrastructure/database/user_repository.py` contêm as queries para criar/listar/excluir/validar usuários e atualizar token/tipo.

## Fluxo de Execução (alto nível)

1. Usuário abre a aplicação (via `streamlit run ...` ou `python run.py`).
2. O entrypoint (`src/geovoto/main.py` ou `app_v1/main.py`) inicializa configuração de UI e o gerenciador de sessão.
3. Se houver token na URL, o fluxo tenta validar o token (consulta `usuarios`) e faz login automático.
4. Usuário não autenticado vê a tela de `Login`. Após login, o `st.session_state` é preenchido e as abas do app são exibidas.
5. O dashboard carrega dados do banco com consultas SQL (tabelas principais usadas: `votacao_candidato_municipio_zona`, `manifestacao_eleitorado_municipio`, `candidato`, `votos_partido_municipio`, `apoio_prefeito_candidato`).
6. GeoDataFrames são carregados a partir dos shapefiles em `data/Limites_municipais_Ceara_2025/...` e unidos aos DataFrames carregados do banco para gerar mapas coropléticos.
7. Visualizações (tabelas, métricas, mapas) são renderizadas em Streamlit; operações pesadas são cacheadas para evitar recálculos.

## Banco de Dados e Consultas Relevantes

- Tabelas observadas nas consultas:
  - `usuarios` — login/token/tipo
  - `votacao_candidato_municipio_zona` — votos por candidato por zona/município
  - `manifestacao_eleitorado_municipio` — eleitorado e votos válidos por município
  - `candidato` — metadados de candidatos
  - `votos_partido_municipio` — votos por partido por município
  - `apoio_prefeito_candidato` — informações de apoio local

- Conexão: SQLAlchemy `create_engine(database_url)`; na versão `src` existe uma `Settings.database.connection_string` gerada via Pydantic.

## Configuração e Variáveis de Ambiente

- `st.secrets["POSTGRES_URL"]` (usado em `app_v1`) ou arquivo `.env`/variáveis de ambiente lidas por `src/geovoto/config/settings.py` (via `pydantic-settings`).
- Arquivos de dados geoespaciais: `data/Limites_municipais_Ceara_2025/*.shp` + acompanhamentos (`.dbf`, `.prj`, etc.).

## Como Rodar (resumo)

1. Instalar dependências (Poetry recomendado):

```bash
poetry install
```

2. Rodar a versão empacotada (recomendada):

```bash
python run.py
# ou
streamlit run src/geovoto/main.py
```

3. Rodar a versão de desenvolvimento rápida:

```bash
streamlit run app_v1/main.py
```

Observação: certifique-se de definir a URL do banco com `st.secrets` (ou `.env`) antes de iniciar.

## Observações e Recomendações

- Existem duas bases de código paralelas (`app_v1` e `src/geovoto`). Recomendo padronizar em uma única implementação (preferencialmente `src/geovoto`, que segue arquitetura em camadas).
- Centralizar a configuração de conexão (uso de `pydantic`/`Settings` é uma boa prática já presente na versão `src`).
- Garantir que todas as consultas SQL usem parametrização e tratamento de exceções (já presente nas camadas de repositório mas existia código direto em `app_v1`).
- Acrescentar documentação de esquema do banco (DDL) e exemplo de `st.secrets`/`.env` no README para facilitar deploy.

---

Arquivo gerado automaticamente por auditoria de código. Se desejar, posso:

- Expandir o diagrama de componentes (Mermaid).
- Gerar um diagrama de sequência do fluxo de login ou do carregamento de dados.
- Produzir um checklist de hardening e observabilidade (logs, métricas, testes).

---

## Branches criadas

Durante a auditoria foram criadas duas branches para organizar as versões principais do projeto:

- `version/app_v1` — contém a versão direta/monolítica presente em `app_v1/`.
- `version/app_v2` — destinada à versão refatorada em `src/geovoto/`.

Ambas as branches foram empurradas para o remoto `origin` e já existem no repositório remoto.

Para trabalhar em cada branch localmente:

```bash
git fetch origin
git checkout version/app_v1
# ou
git checkout version/app_v2
```

Se desejar, posso limpar cada branch para manter apenas os arquivos relevantes (por exemplo deixar somente `app_v1/` em `version/app_v1`). Quer que eu faça essa limpeza agora?
