# app/utils/cache.py - Sistema de cache simplificado e funcional
import streamlit as st
import hashlib
import time
from functools import wraps
from typing import Any, Callable, Optional
from config.config_manager import config_manager

class CacheManager:
    """Gerenciador de cache inteligente com diferentes estratégias"""
    
    @staticmethod
    def generate_cache_key(*args, **kwargs) -> str:
        """Gera uma chave de cache única baseada nos argumentos"""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    @staticmethod
    def is_cache_valid(cache_time: float, ttl: int) -> bool:
        """Verifica se o cache ainda é válido"""
        return time.time() - cache_time < ttl

# Cache para recursos (conexões, etc.)
@st.cache_resource(show_spinner="🔧 Inicializando recursos...")
def cached_engine(_factory_func: Callable) -> Any:
    """Cache para engines de banco e recursos pesados"""
    return _factory_func()

# Funções de cache específicas para diferentes tipos de dados
def cache_electoral_data(func: Callable) -> Callable:
    """Cache específico para dados eleitorais"""
    ttl = config_manager.cache.semi_static_ttl
    return st.cache_data(ttl=ttl, show_spinner="🗳️ Carregando dados eleitorais...")(func)

def cache_geographic_data(func: Callable) -> Callable:
    """Cache específico para dados geográficos"""
    ttl = config_manager.cache.static_ttl
    return st.cache_data(ttl=ttl, show_spinner="🗺️ Carregando dados geográficos...")(func)

def cache_user_data(func: Callable) -> Callable:
    """Cache específico para dados de usuário"""
    ttl = config_manager.cache.volatile_ttl * 3  # 15 minutos
    return st.cache_data(ttl=ttl, show_spinner="👤 Carregando dados do usuário...")(func)

def cache_analytics_data(func: Callable) -> Callable:
    """Cache específico para dados analíticos"""
    ttl = config_manager.cache.dynamic_ttl
    return st.cache_data(ttl=ttl, show_spinner="📊 Processando análises...")(func)

# Cache para dados do dashboard
def cached_dashboard_data(ttl: int = None, show_spinner: str = "📈 Atualizando dashboard..."):
    """Cache otimizado para dados do dashboard"""
    if ttl is None:
        ttl = config_manager.cache.semi_static_ttl
    
    return st.cache_data(ttl=ttl, show_spinner=show_spinner)

# Cache para dados geoespaciais (mais duradouro)
def cached_geodata(ttl: int = None, show_spinner: str = "🗺️ Carregando mapas..."):
    """Cache para dados geoespaciais que mudam pouco"""
    if ttl is None:
        ttl = config_manager.cache.static_ttl
    
    return st.cache_data(ttl=ttl, show_spinner=show_spinner)

# Cache para autenticação
def cached_user_data_auth(ttl: int = None, show_spinner: str = "🔐 Verificando usuário..."):
    """Cache para dados de usuário - autenticação"""
    if ttl is None:
        ttl = config_manager.cache.volatile_ttl * 3  # 15 minutos para dados de usuário
    
    return st.cache_data(ttl=ttl, show_spinner=show_spinner)

def smart_cache(ttl: int = None, key_func: Optional[Callable] = None):
    """Decorator para cache personalizado"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # TTL dinâmico baseado na configuração
            cache_ttl = ttl or config_manager.cache.dynamic_ttl
            
            # Gera chave do cache
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = CacheManager.generate_cache_key(*args, **kwargs)
            
            # Verifica se existe cache válido
            if f"cache_{cache_key}" in st.session_state:
                cache_data, cache_time = st.session_state[f"cache_{cache_key}"]
                if CacheManager.is_cache_valid(cache_time, cache_ttl):
                    return cache_data
            
            # Executa função e salva no cache
            result = func(*args, **kwargs)
            st.session_state[f"cache_{cache_key}"] = (result, time.time())
            
            return result
        return wrapper
    return decorator

def clear_cache_by_pattern(pattern: str):
    """Limpa cache baseado em padrão"""
    keys_to_remove = [key for key in st.session_state.keys() if pattern in key]
    for key in keys_to_remove:
        del st.session_state[key]

def get_cache_stats() -> dict:
    """Retorna estatísticas do cache"""
    cache_keys = [key for key in st.session_state.keys() if key.startswith("cache_")]
    return {
        "total_cached_items": len(cache_keys),
        "cache_size_mb": len(str(st.session_state)) / 1024 / 1024,
        "cache_keys": cache_keys[:10],  # Primeiros 10
        "config": {
            "static_ttl": config_manager.cache.static_ttl,
            "semi_static_ttl": config_manager.cache.semi_static_ttl,
            "dynamic_ttl": config_manager.cache.dynamic_ttl,
            "volatile_ttl": config_manager.cache.volatile_ttl,
            "max_size": config_manager.cache.max_size,
            "compression_enabled": config_manager.cache.enable_compression
        }
    }

def clear_all_cache():
    """Limpa todo o cache da aplicação"""
    st.cache_data.clear()
    st.cache_resource.clear()
    
    # Limpa cache do session_state
    cache_keys = [key for key in st.session_state.keys() if key.startswith("cache_")]
    for key in cache_keys:
        del st.session_state[key]

def optimize_cache_settings():
    """Otimiza configurações de cache baseado no ambiente"""
    if config_manager.is_production():
        # Produção: Cache mais agressivo
        return {
            "enable_compression": True,
            "auto_cleanup": True,
            "aggressive_caching": True
        }
    else:
        # Desenvolvimento: Cache mais permissivo
        return {
            "enable_compression": False,
            "auto_cleanup": True,
            "aggressive_caching": False
        }

# Monitoramento de cache
class CacheMonitor:
    """Monitor para acompanhar performance do cache"""
    
    @staticmethod
    def get_hit_rate() -> float:
        """Calcula taxa de hit do cache (simulado)"""
        # Em implementação real, seria calculado baseado em métricas
        return 75.0  # Placeholder
    
    @staticmethod
    def get_memory_usage() -> dict:
        """Retorna uso de memória do cache"""
        cache_size = len(str(st.session_state)) / 1024 / 1024  # MB
        return {
            "cache_size_mb": round(cache_size, 2),
            "max_recommended_mb": 50,
            "usage_percentage": min(100, (cache_size / 50) * 100)
        }
    
    @staticmethod
    def should_clear_cache() -> bool:
        """Determina se o cache deve ser limpo"""
        memory_info = CacheMonitor.get_memory_usage()
        return memory_info["usage_percentage"] > 80
    
    @staticmethod
    def auto_cleanup():
        """Limpeza automática do cache quando necessário"""
        if CacheMonitor.should_clear_cache():
            # Remove apenas cache mais antigo
            cache_keys = [k for k in st.session_state.keys() if k.startswith("cache_")]
            if len(cache_keys) > config_manager.cache.max_size:
                # Remove 20% dos caches mais antigos
                keys_to_remove = cache_keys[:len(cache_keys) // 5]
                for key in keys_to_remove:
                    if key in st.session_state:
                        del st.session_state[key]

# Inicialização do sistema de cache
def initialize_cache_system():
    """Inicializa o sistema de cache"""
    if config_manager.cache.auto_cleanup:
        CacheMonitor.auto_cleanup()
    
    # Log das configurações de cache se em debug
    if config_manager.is_debug_enabled():
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Cache inicializado - TTLs: "
                   f"Static={config_manager.cache.static_ttl}s, "
                   f"Semi-static={config_manager.cache.semi_static_ttl}s, "
                   f"Dynamic={config_manager.cache.dynamic_ttl}s, "
                   f"Volatile={config_manager.cache.volatile_ttl}s")

# Compatibilidade com código antigo
def get_cache_config():
    """Retorna configuração de cache para compatibilidade"""
    return {
        "ttl": config_manager.cache.dynamic_ttl,
        "max_size": config_manager.cache.max_size,
        "enable_compression": config_manager.cache.enable_compression
    }

# Aliases para compatibilidade
cached_query = cache_analytics_data

# Inicializa o sistema na importação
initialize_cache_system()