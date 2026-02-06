# config/settings.py - Compatibilidade com código antigo
"""
Este arquivo mantém compatibilidade com imports antigos do settings.py
Novos desenvolvimentos devem usar config_manager.py
"""

from config.config_manager import config_manager, legacy_app_config
import os
from dataclasses import dataclass
from pathlib import Path

@dataclass
class AppConfig:
    """Configurações gerais da aplicação - LEGACY"""
    app_name: str = "GeoVoto - Análise Eleitoral"
    app_icon: str = "🗳️"
    page_layout: str = "wide"
    initial_sidebar_state: str = "collapsed"
    
    # Propriedades dinâmicas para compatibilidade
    @property
    def cache_ttl(self):
        return config_manager.cache.dynamic_ttl
    
    @property
    def shapefile_path(self):
        return config_manager.data.shapefile_path
    
    @property
    def default_candidate_id(self):
        return config_manager.data.default_candidate_id

# Instância global para compatibilidade
app_config = legacy_app_config

# Cria diretórios necessários
Path("app/data").mkdir(parents=True, exist_ok=True)

# Aviso de depreciação para desenvolvimento
import logging
logger = logging.getLogger(__name__)

if config_manager.is_debug_enabled():
    logger.warning(
        "DEPRECATION: config/settings.py está obsoleto. "
        "Use config/config_manager.py para novos desenvolvimentos."
    )