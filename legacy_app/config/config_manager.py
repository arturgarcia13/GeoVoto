# config/config_manager.py
import os
import streamlit as st
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class Environment(Enum):
    """Ambientes de execução"""
    DEVELOPMENT = "development"
    STAGING = "staging" 
    PRODUCTION = "production"
    LOCAL = "local"

@dataclass
class DatabaseConfig:
    """Configurações de banco de dados"""
    host: str = "localhost"
    port: int = 5432
    database: str = "electoral_data"
    username: str = "postgres"
    password: str = ""
    pool_size: int = 10
    pool_timeout: int = 30
    ssl_mode: str = "prefer"
    
    @property
    def connection_string(self) -> str:
        """Gera string de conexão"""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}?sslmode={self.ssl_mode}"

@dataclass  
class CacheConfig:
    """Configurações de cache"""
    static_ttl: int = 86400      # 24 horas
    semi_static_ttl: int = 3600  # 1 hora
    dynamic_ttl: int = 900       # 15 minutos
    volatile_ttl: int = 300      # 5 minutos
    max_size: int = 500          # Máximo de entradas
    enable_compression: bool = True
    auto_cleanup: bool = True

@dataclass
class UIConfig:
    """Configurações de interface"""
    page_title: str = "GeoVoto - Sistema de Análise Eleitoral"
    page_icon: str = "🗳️"
    layout: str = "wide"
    initial_sidebar_state: str = "collapsed"
    theme: str = "light"
    show_performance_metrics: bool = False
    enable_debug_mode: bool = False

@dataclass
class DataConfig:
    """Configurações de dados"""
    shapefile_path: str = "app/data/Limites_municipais_Ceara_2025/Limites_municipais_IPECE_2025_utm_sirgas_2000.shp"
    default_candidate_id: int = 1221
    batch_size: int = 1000
    max_memory_per_df: int = 100  # MB
    enable_data_validation: bool = True
    auto_optimize_dtypes: bool = True

@dataclass
class SecurityConfig:
    """Configurações de segurança"""
    token_expiry_hours: int = 24
    max_login_attempts: int = 5
    session_timeout_minutes: int = 120
    require_https: bool = False
    enable_audit_log: bool = True
    allowed_file_types: list = field(default_factory=lambda: ['.shp', '.csv', '.xlsx'])

@dataclass
class PerformanceConfig:
    """Configurações de performance"""
    enable_query_optimization: bool = True
    enable_performance_monitoring: bool = True
    slow_query_threshold: float = 2.0  # segundos
    memory_warning_threshold: float = 85.0  # percentual
    cache_warning_threshold: float = 50.0  # hit rate mínimo
    auto_cleanup_interval: int = 3600  # segundos

class ConfigManager:
    """Gerenciador centralizado de configurações"""
    
    def __init__(self, environment: Optional[Environment] = None):
        self.environment = environment or self._detect_environment()
        self._config_cache: Dict[str, Any] = {}
        self.load_configurations()
    
    def _detect_environment(self) -> Environment:
        """Detecta ambiente atual baseado em variáveis"""
        env_name = os.getenv("STREAMLIT_ENV", "local").lower()
        
        env_mapping = {
            "prod": Environment.PRODUCTION,
            "production": Environment.PRODUCTION,
            "staging": Environment.STAGING,
            "stage": Environment.STAGING,
            "dev": Environment.DEVELOPMENT,
            "development": Environment.DEVELOPMENT,
            "local": Environment.LOCAL
        }
        
        return env_mapping.get(env_name, Environment.LOCAL)
    
    def load_configurations(self):
        """Carrega todas as configurações"""
        try:
            self.database = self._load_database_config()
            self.cache = self._load_cache_config()
            self.ui = self._load_ui_config()
            self.data = self._load_data_config()
            self.security = self._load_security_config()
            self.performance = self._load_performance_config()
            
            logger.info(f"Configurações carregadas para ambiente: {self.environment.value}")
            
        except Exception as e:
            logger.error(f"Erro ao carregar configurações: {e}")
            self._load_default_configurations()
    
    def _load_database_config(self) -> DatabaseConfig:
        """Carrega configurações de banco"""
        if self.environment == Environment.PRODUCTION:
            return DatabaseConfig(
                host=st.secrets.get("DB_HOST", "localhost"),
                port=int(st.secrets.get("DB_PORT", 5432)),
                database=st.secrets.get("DB_NAME", "electoral_data"),
                username=st.secrets.get("DB_USER", "postgres"),
                password=st.secrets.get("DB_PASSWORD", ""),
                pool_size=20,
                pool_timeout=60,
                ssl_mode="require"
            )
        elif self.environment == Environment.STAGING:
            return DatabaseConfig(
                host=st.secrets.get("DB_HOST", "staging-db"),
                port=int(st.secrets.get("DB_PORT", 5432)),
                database=st.secrets.get("DB_NAME", "electoral_staging"),
                username=st.secrets.get("DB_USER", "postgres"),
                password=st.secrets.get("DB_PASSWORD", ""),
                pool_size=10,
                ssl_mode="require"
            )
        else:  # DEVELOPMENT/LOCAL
            return DatabaseConfig(
                host="localhost",
                port=5432,
                database="electoral_local",
                username="postgres",
                password="postgres",
                pool_size=5,
                ssl_mode="prefer"
            )
    
    def _load_cache_config(self) -> CacheConfig:
        """Carrega configurações de cache"""
        if self.environment == Environment.PRODUCTION:
            return CacheConfig(
                static_ttl=86400,      # 24 horas
                semi_static_ttl=7200,  # 2 horas
                dynamic_ttl=1800,      # 30 minutos
                volatile_ttl=600,      # 10 minutos
                max_size=1000,
                enable_compression=True,
                auto_cleanup=True
            )
        elif self.environment == Environment.STAGING:
            return CacheConfig(
                static_ttl=43200,      # 12 horas
                semi_static_ttl=3600,  # 1 hora
                dynamic_ttl=900,       # 15 minutos
                volatile_ttl=300,      # 5 minutos
                max_size=500,
                enable_compression=True,
                auto_cleanup=True
            )
        else:  # DEVELOPMENT/LOCAL
            return CacheConfig(
                static_ttl=3600,       # 1 hora
                semi_static_ttl=1800,  # 30 minutos
                dynamic_ttl=600,       # 10 minutos
                volatile_ttl=180,      # 3 minutos
                max_size=200,
                enable_compression=False,
                auto_cleanup=True
            )
    
    def _load_ui_config(self) -> UIConfig:
        """Carrega configurações de interface"""
        base_config = UIConfig()
        
        if self.environment == Environment.PRODUCTION:
            base_config.show_performance_metrics = False
            base_config.enable_debug_mode = False
            base_config.initial_sidebar_state = "collapsed"
        elif self.environment == Environment.STAGING:
            base_config.show_performance_metrics = True
            base_config.enable_debug_mode = False
            base_config.initial_sidebar_state = "expanded"
        else:  # DEVELOPMENT/LOCAL
            base_config.show_performance_metrics = True
            base_config.enable_debug_mode = True
            base_config.initial_sidebar_state = "expanded"
        
        return base_config
    
    def _load_data_config(self) -> DataConfig:
        """Carrega configurações de dados"""
        base_config = DataConfig()
        
        # Ajusta configurações por ambiente
        if self.environment == Environment.PRODUCTION:
            base_config.batch_size = 2000
            base_config.max_memory_per_df = 200  # MB
            base_config.auto_optimize_dtypes = True
        elif self.environment == Environment.STAGING:
            base_config.batch_size = 1500
            base_config.max_memory_per_df = 150  # MB
        else:  # DEVELOPMENT/LOCAL
            base_config.batch_size = 500
            base_config.max_memory_per_df = 50  # MB
            base_config.enable_data_validation = False  # Mais rápido para dev
        
        return base_config
    
    def _load_security_config(self) -> SecurityConfig:
        """Carrega configurações de segurança"""
        base_config = SecurityConfig()
        
        if self.environment == Environment.PRODUCTION:
            base_config.token_expiry_hours = 8
            base_config.max_login_attempts = 3
            base_config.session_timeout_minutes = 60
            base_config.require_https = True
            base_config.enable_audit_log = True
        elif self.environment == Environment.STAGING:
            base_config.token_expiry_hours = 12
            base_config.session_timeout_minutes = 120
            base_config.require_https = True
        else:  # DEVELOPMENT/LOCAL
            base_config.token_expiry_hours = 48
            base_config.max_login_attempts = 10
            base_config.session_timeout_minutes = 480
            base_config.require_https = False
            base_config.enable_audit_log = False
        
        return base_config
    
    def _load_performance_config(self) -> PerformanceConfig:
        """Carrega configurações de performance"""
        base_config = PerformanceConfig()
        
        if self.environment == Environment.PRODUCTION:
            base_config.slow_query_threshold = 1.0
            base_config.memory_warning_threshold = 80.0
            base_config.cache_warning_threshold = 70.0
            base_config.auto_cleanup_interval = 1800  # 30 min
        elif self.environment == Environment.STAGING:
            base_config.slow_query_threshold = 2.0
            base_config.memory_warning_threshold = 85.0
            base_config.auto_cleanup_interval = 3600  # 1 hora
        else:  # DEVELOPMENT/LOCAL
            base_config.slow_query_threshold = 5.0
            base_config.memory_warning_threshold = 90.0
            base_config.cache_warning_threshold = 30.0
            base_config.auto_cleanup_interval = 7200  # 2 horas
        
        return base_config
    
    def _load_default_configurations(self):
        """Carrega configurações padrão em caso de erro"""
        logger.warning("Carregando configurações padrão devido a erro")
        
        self.database = DatabaseConfig()
        self.cache = CacheConfig()
        self.ui = UIConfig()
        self.data = DataConfig()
        self.security = SecurityConfig()
        self.performance = PerformanceConfig()
    
    def get_streamlit_config(self) -> Dict[str, Any]:
        """Retorna configurações para st.set_page_config"""
        return {
            "page_title": self.ui.page_title,
            "page_icon": self.ui.page_icon,
            "layout": self.ui.layout,
            "initial_sidebar_state": self.ui.initial_sidebar_state
        }
    
    def get_database_url(self) -> str:
        """Retorna URL de conexão do banco"""
        if hasattr(st, 'secrets') and "POSTGRES_URL" in st.secrets:
            return st.secrets["POSTGRES_URL"]
        return self.database.connection_string
    
    def is_debug_enabled(self) -> bool:
        """Verifica se debug está habilitado"""
        return self.ui.enable_debug_mode
    
    def is_production(self) -> bool:
        """Verifica se está em produção"""
        return self.environment == Environment.PRODUCTION
    
    def get_feature_flags(self) -> Dict[str, bool]:
        """Retorna feature flags baseadas no ambiente"""
        return {
            "enable_performance_monitoring": self.performance.enable_performance_monitoring,
            "enable_query_optimization": self.performance.enable_query_optimization,
            "show_debug_info": self.ui.enable_debug_mode,
            "enable_audit_log": self.security.enable_audit_log,
            "auto_optimize_data": self.data.auto_optimize_dtypes,
            "enable_data_validation": self.data.enable_data_validation
        }
    
    def update_config(self, section: str, key: str, value: Any):
        """Atualiza configuração em runtime"""
        if hasattr(self, section):
            config_obj = getattr(self, section)
            if hasattr(config_obj, key):
                setattr(config_obj, key, value)
                logger.info(f"Configuração atualizada: {section}.{key} = {value}")
            else:
                logger.warning(f"Chave de configuração não encontrada: {section}.{key}")
        else:
            logger.warning(f"Seção de configuração não encontrada: {section}")
    
    def export_config(self) -> Dict[str, Any]:
        """Exporta configurações atuais (sem dados sensíveis)"""
        return {
            "environment": self.environment.value,
            "database": {
                "host": self.database.host,
                "port": self.database.port,
                "database": self.database.database,
                "pool_size": self.database.pool_size,
                "ssl_mode": self.database.ssl_mode
                # Senha omitida por segurança
            },
            "cache": {
                "static_ttl": self.cache.static_ttl,
                "semi_static_ttl": self.cache.semi_static_ttl,
                "dynamic_ttl": self.cache.dynamic_ttl,
                "max_size": self.cache.max_size,
                "enable_compression": self.cache.enable_compression
            },
            "ui": {
                "page_title": self.ui.page_title,
                "layout": self.ui.layout,
                "theme": self.ui.theme,
                "show_performance_metrics": self.ui.show_performance_metrics,
                "enable_debug_mode": self.ui.enable_debug_mode
            },
            "performance": {
                "enable_monitoring": self.performance.enable_performance_monitoring,
                "slow_query_threshold": self.performance.slow_query_threshold,
                "memory_warning_threshold": self.performance.memory_warning_threshold
            }
        }
    
    def validate_configuration(self) -> list[str]:
        """Valida configurações e retorna lista de problemas"""
        issues = []
        
        # Validações de banco
        if not self.database.host:
            issues.append("Host do banco não configurado")
        if self.database.port < 1 or self.database.port > 65535:
            issues.append("Porta do banco inválida")
        
        # Validações de cache
        if self.cache.static_ttl < self.cache.dynamic_ttl:
            issues.append("TTL estático deve ser maior que dinâmico")
        
        # Validações de arquivos
        shapefile_path = Path(self.data.shapefile_path)
        if not shapefile_path.exists():
            issues.append(f"Shapefile não encontrado: {self.data.shapefile_path}")
        
        # Validações de performance
        if self.performance.slow_query_threshold <= 0:
            issues.append("Threshold de query lenta deve ser positivo")
        
        return issues

# Instância global do gerenciador de configurações
config_manager = ConfigManager()

# Shortcuts para configurações mais usadas
app_config = config_manager.ui
db_config = config_manager.database
cache_config = config_manager.cache
data_config = config_manager.data
performance_config = config_manager.performance
security_config = config_manager.security

# Compatibilidade com código antigo
class LegacyAppConfig:
    """Classe de compatibilidade para o código antigo"""
    
    @property
    def app_name(self):
        return config_manager.ui.page_title
    
    @property
    def app_icon(self):
        return config_manager.ui.page_icon
    
    @property
    def page_layout(self):
        return config_manager.ui.layout
    
    @property
    def initial_sidebar_state(self):
        return config_manager.ui.initial_sidebar_state
    
    @property
    def cache_ttl(self):
        return config_manager.cache.dynamic_ttl
    
    @property
    def shapefile_path(self):
        return config_manager.data.shapefile_path
    
    @property
    def default_candidate_id(self):
        return config_manager.data.default_candidate_id

# Para compatibilidade com imports antigos
legacy_app_config = LegacyAppConfig()