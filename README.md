# GeoVoto 🗳️

Sistema de Inteligência Geográfica Eleitoral profissional, refatorado para escalabilidade e manutenção.

## 🚀 Funcionalidades

- **Dashboard Interativo**: Acompanhamento em tempo real das eleições.
- **Mapas Eleitorais**: Visualização coroplética de votos por município.
- **Análise de Apoio**: Correlação entre apoio político e resultados.
- **Gestão de Usuários**: Autenticação segura via token.

## 🏗️ Arquitetura

O projeto segue uma arquitetura em camadas (Layered Architecture):

```
geovoto/
├── src/geovoto/
│   ├── config/         # Configurações (Pydantic Settings)
│   ├── core/           # Exceções, Logging, Base
│   ├── domain/         # Modelos de Domínio
│   ├── services/       # Lógica de Negócios (Auth, Data, Map)
│   ├── infrastructure/ # Banco de Dados, Cache
│   ├── ui/             # Interface Streamlit (Layouts, Pages, Components)
│   └── utils/          # Utilitários
├── tests/              # Testes Automatizados (Pytest)
├── data/               # Arquivos de Dados (Shapefiles, etc)
└── pyproject.toml      # Gerenciamento de Dependências
```


## 🛠️ Instalação (via Poetry - Recomendado)

1.  Certifique-se de ter o [Poetry](https://python-poetry.org/) instalado.
2.  Instale as dependências:
    ```bash
    poetry install
    ```
3.  Ative o ambiente virtual:
    ```bash
    poetry shell
    ```

## ▶️ Como Rodar

### Via Poetry
```bash
poetry run streamlit run src/geovoto/main.py
```

### Via Script (se ambiente estiver ativo)
```bash
python run.py
```

## 🧪 Testes

Para rodar os testes unitários:
```bash
pytest
```

## 👥 Contribuição

Siga os padrões de código definidos no `pyproject.toml` (Ruff, Black).
