
import streamlit as st
import hashlib
import pickle
import time
from functools import wraps
from typing import Any, Callable, Optional
from config.settings import app_config

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

# Cache para dados com TTL configurável
@st.cache_data(ttl=app_config.cache_ttl, show_spinner="📊 Carregando dados...")
def cached_query(_query_func: Callable, *args, **kwargs) -> Any:
    """Cache inteligente para queries de banco"""
    return _query_func(*args, **kwargs)

# Cache específico para dados do dashboard
@st.cache_data(ttl=300, show_spinner="📈 Atualizando dashboard...")  # 5 minutos
def cached_dashboard_data(_data_loader_func: Callable, _engine) -> Any:
    """Cache otimizado para dados do dashboard"""
    return _data_loader_func(_engine)

# Cache para dados geoespaciais (mais duradouro)
@st.cache_data(ttl=3600, show_spinner="🗺️ Carregando mapas...")  # 1 hora
def cached_geodata(_loader_func: Callable, *args) -> Any:
    """Cache para dados geoespaciais que mudam pouco"""
    return _loader_func(*args)

# Cache para autenticação
@st.cache_data(ttl=900, show_spinner="🔐 Verificando usuário...")  # 15 minutos
def cached_user_data(_user_func: Callable, identifier: str) -> Any:
    """Cache para dados de usuário"""
    return _user_func(identifier)

def smart_cache(ttl: int = None, key_func: Optional[Callable] = None):
    """Decorator para cache personalizado"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_ttl = ttl or app_config.cache_ttl
            
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
        "cache_keys": cache_keys[:10]  # Primeiros 10
    }
