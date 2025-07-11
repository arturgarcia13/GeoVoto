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
    cache_ttl: int = 300  # 5 minutos

# @dataclass 
# class DatabaseConfig:
#     """Configurações do banco de dados"""
#     users_file: str = "app/data/usuarios.json"
#     db_type: str = "json"  # json ou postgresql

#     # PostgreSQL (se disponível)
#     host: str = os.getenv("DB_HOST", "localhost")
#     port: int = int(os.getenv("DB_PORT", "5432"))
#     database: str = os.getenv("DB_NAME", "eleicoes")
#     username: str = os.getenv("DB_USER", "postgres")
#     password: str = os.getenv("DB_PASSWORD", "")

# Instâncias globais
app_config = AppConfig()
# db_config = DatabaseConfig()

# Cria diretórios necessários
Path("app/data").mkdir(parents=True, exist_ok=True)