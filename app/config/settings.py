import os
from dataclasses import dataclass
from pathlib import Path

@dataclass
class AppConfig:
    """Configurações gerais da aplicação"""
    app_name: str = "GeoVoto - Análise Eleitoral"
    app_icon: str = "🗳️"
    page_layout: str = "wide"
    initial_sidebar_state: str = "collapsed"

# Instâncias globais
app_config = AppConfig()
# db_config = DatabaseConfig()

# Cria diretórios necessários
Path("app/data").mkdir(parents=True, exist_ok=True)