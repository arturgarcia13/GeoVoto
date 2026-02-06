import os
from enum import Enum
from pathlib import Path
from typing import List, Optional

from pydantic import Field, PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    LOCAL = "local"


class DatabaseSettings(BaseSettings):
    host: str = "localhost"
    port: int = 5432
    database: str = "electoral_data"
    username: str = "postgres"
    password: str = ""
    pool_size: int = 10
    pool_timeout: int = 30
    ssl_mode: str = "prefer"

    @computed_field
    def connection_string(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql",
                username=self.username,
                password=self.password,
                host=self.host,
                port=self.port,
                path=self.database,
                query=f"sslmode={self.ssl_mode}" if self.ssl_mode else None,
            )
        )


class CacheSettings(BaseSettings):
    static_ttl: int = 86400  # 24 hours
    semi_static_ttl: int = 3600  # 1 hour
    dynamic_ttl: int = 900  # 15 minutes
    volatile_ttl: int = 300  # 5 minutes
    max_size: int = 500
    enable_compression: bool = True
    auto_cleanup: bool = True


class UISettings(BaseSettings):
    page_title: str = "GeoVoto - Sistema de Análise Eleitoral"
    page_icon: str = "🗳️"
    layout: str = "wide"
    initial_sidebar_state: str = "collapsed"
    theme: str = "light"
    show_performance_metrics: bool = False
    enable_debug_mode: bool = False


class DataSettings(BaseSettings):
    shapefile_path: str = Field(
        default="data/Limites_municipais_Ceara_2025/Limites_municipais_IPECE_2025_utm_sirgas_2000.shp"
    )
    default_candidate_id: int = 1221
    batch_size: int = 1000
    max_memory_per_df: int = 100  # MB
    enable_data_validation: bool = True
    auto_optimize_dtypes: bool = True


class SecuritySettings(BaseSettings):
    token_expiry_hours: int = 24
    max_login_attempts: int = 5
    session_timeout_minutes: int = 120
    require_https: bool = False
    enable_audit_log: bool = True
    allowed_file_types: List[str] = [".shp", ".csv", ".xlsx"]


class PerformanceSettings(BaseSettings):
    enable_query_optimization: bool = True
    enable_performance_monitoring: bool = True
    slow_query_threshold: float = 2.0
    memory_warning_threshold: float = 85.0
    cache_warning_threshold: float = 50.0
    auto_cleanup_interval: int = 3600


class Settings(BaseSettings):
    """
    Main settings class for the application.
    Reads from environment variables and .env files.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore"
    )

    environment: Environment = Environment.LOCAL
    
    # Nested configs
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    ui: UISettings = Field(default_factory=UISettings)
    data: DataSettings = Field(default_factory=DataSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    performance: PerformanceSettings = Field(default_factory=PerformanceSettings)

    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION

    def is_debug(self) -> bool:
        return self.ui.enable_debug_mode


# Global settings instance
settings = Settings()
