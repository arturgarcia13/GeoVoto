# utils/advanced_cache.py
import streamlit as st
import hashlib
import time
import pickle
import logging
from functools import wraps
from typing import Any, Callable, Optional, Dict, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CacheLevel(Enum):
    """Níveis de cache com diferentes TTLs"""
    STATIC = "static"          # Dados que raramente mudam (1 dia)
    SEMI_STATIC = "semi_static"  # Dados que mudam ocasionalmente (1 hora) 
    DYNAMIC = "dynamic"        # Dados que mudam frequentemente (15 min)
    VOLATILE = "volatile"      # Dados que mudam constantemente (5 min)

@dataclass
class CacheConfig:
    """Configuração de cache por nível"""
    level: CacheLevel
    ttl_seconds: int
    max_size: int = 100
    compress: bool = False
    
    @classmethod
    def get_config(cls, level: CacheLevel) -> 'CacheConfig':
        """Retorna configuração padrão por nível"""
        configs = {
            CacheLevel.STATIC: cls(CacheLevel.STATIC, 86400, 50, True),      # 1 dia
            CacheLevel.SEMI_STATIC: cls(CacheLevel.SEMI_STATIC, 3600, 100, False),  # 1 hora
            CacheLevel.DYNAMIC: cls(CacheLevel.DYNAMIC, 900, 150, False),    # 15 min
            CacheLevel.VOLATILE: cls(CacheLevel.VOLATILE, 300, 200, False)   # 5 min
        }
        return configs[level]

class CacheStats:
    """Estatísticas de performance do cache"""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.start_time = time.time()
    
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0
    
    @property
    def total_requests(self) -> int:
        return self.hits + self.misses
    
    def record_hit(self):
        self.hits += 1
    
    def record_miss(self):
        self.misses += 1
    
    def record_eviction(self):
        self.evictions += 1

class SmartCache:
    """Sistema de cache inteligente com múltiplos níveis"""
    
    def __init__(self):
        self.stats = CacheStats()
        self._initialize_session_cache()
    
    def _initialize_session_cache(self):
        """Inicializa cache na sessão se não existir"""
        if "smart_cache" not in st.session_state:
            st.session_state.smart_cache = {}
        if "cache_metadata" not in st.session_state:
            st.session_state.cache_metadata = {}
    
    def _generate_cache_key(self, func: Callable, args: tuple, kwargs: dict) -> str:
        """Gera chave única para cache"""
        key_data = f"{func.__module__}.{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _is_cache_valid(self, metadata: dict, config: CacheConfig) -> bool:
        """Verifica se cache ainda é válido"""
        cache_time = metadata.get("timestamp", 0)
        return time.time() - cache_time < config.ttl_seconds
    
    def _compress_data(self, data: Any) -> bytes:
        """Comprime dados para economia de memória"""
        return pickle.dumps(data)
    
    def _decompress_data(self, compressed_data: bytes) -> Any:
        """Descomprime dados"""
        return pickle.loads(compressed_data)
    
    def _evict_expired_entries(self, config: CacheConfig):
        """Remove entradas expiradas do cache"""
        current_time = time.time()
        expired_keys = []
        
        for key, metadata in st.session_state.cache_metadata.items():
            if current_time - metadata.get("timestamp", 0) > config.ttl_seconds:
                expired_keys.append(key)
        
        for key in expired_keys:
            self._remove_cache_entry(key)
            self.stats.record_eviction()
    
    def _remove_cache_entry(self, key: str):
        """Remove entrada específica do cache"""
        if key in st.session_state.smart_cache:
            del st.session_state.smart_cache[key]
        if key in st.session_state.cache_metadata:
            del st.session_state.cache_metadata[key]
    
    def _enforce_size_limit(self, config: CacheConfig):
        """Força limite de tamanho do cache (LRU)"""
        cache_size = len(st.session_state.smart_cache)
        
        if cache_size >= config.max_size:
            # Remove entradas mais antigas (LRU)
            sorted_entries = sorted(
                st.session_state.cache_metadata.items(),
                key=lambda x: x[1].get("last_access", 0)
            )
            
            # Remove 20% das entradas mais antigas
            entries_to_remove = max(1, int(config.max_size * 0.2))
            
            for key, _ in sorted_entries[:entries_to_remove]:
                self._remove_cache_entry(key)
                self.stats.record_eviction()
    
    def get(self, key: str, config: CacheConfig) -> Optional[Any]:
        """Recupera valor do cache se válido"""
        if key not in st.session_state.smart_cache:
            self.stats.record_miss()
            return None
        
        metadata = st.session_state.cache_metadata.get(key, {})
        
        if not self._is_cache_valid(metadata, config):
            self._remove_cache_entry(key)
            self.stats.record_miss()
            return None
        
        # Atualiza último acesso (LRU)
        metadata["last_access"] = time.time()
        st.session_state.cache_metadata[key] = metadata
        
        self.stats.record_hit()
        
        # Descomprime se necessário
        data = st.session_state.smart_cache[key]
        if config.compress and isinstance(data, bytes):
            return self._decompress_data(data)
        
        return data
    
    def set(self, key: str, value: Any, config: CacheConfig):
        """Armazena valor no cache"""
        self._evict_expired_entries(config)
        self._enforce_size_limit(config)
        
        # Comprime se configurado
        if config.compress:
            value = self._compress_data(value)
        
        # Armazena dados e metadata
        st.session_state.smart_cache[key] = value
        st.session_state.cache_metadata[key] = {
            "timestamp": time.time(),
            "last_access": time.time(),
            "level": config.level.value,
            "compressed": config.compress
        }
    
    def invalidate_pattern(self, pattern: str):
        """Invalida cache por padrão"""
        keys_to_remove = [
            key for key in st.session_state.smart_cache.keys()
            if pattern in key
        ]
        
        for key in keys_to_remove:
            self._remove_cache_entry(key)
    
    def clear_level(self, level: CacheLevel):
        """Limpa cache de um nível específico"""
        keys_to_remove = [
            key for key, metadata in st.session_state.cache_metadata.items()
            if metadata.get("level") == level.value
        ]
        
        for key in keys_to_remove:
            self._remove_cache_entry(key)
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Retorna informações do cache"""
        total_size = len(st.session_state.smart_cache)
        levels_count = {}
        
        for metadata in st.session_state.cache_metadata.values():
            level = metadata.get("level", "unknown")
            levels_count[level] = levels_count.get(level, 0) + 1
        
        return {
            "total_entries": total_size,
            "hit_rate": self.stats.hit_rate,
            "total_requests": self.stats.total_requests,
            "entries_by_level": levels_count,
            "uptime_minutes": (time.time() - self.stats.start_time) / 60
        }

# Instância global do cache
smart_cache = SmartCache()

def cached(level: CacheLevel = CacheLevel.SEMI_STATIC, key_func: Optional[Callable] = None):
    """Decorator para cache automático com níveis"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(self, *args, **kwargs):  # Adiciona 'self' para métodos de instância
            config = CacheConfig.get_config(level)
            
            # Gera chave do cache
            if key_func:
                cache_key = key_func(self, *args, **kwargs)
            else:
                cache_key = smart_cache._generate_cache_key(func, args, kwargs)
            
            # Tenta recuperar do cache
            cached_result = smart_cache.get(cache_key, config)
            if cached_result is not None:
                return cached_result
            
            # Executa função e armazena resultado
            result = func(self, *args, **kwargs)
            smart_cache.set(cache_key, result, config)
            
            return result
        
        # Adiciona métodos de controle de cache
        wrapper.clear_cache = lambda: smart_cache.invalidate_pattern(func.__name__)
        wrapper.cache_info = smart_cache.get_cache_info
        
        return wrapper
    return decorator

# Decorators específicos para diferentes níveis
def cached_static(func: Callable) -> Callable:
    """Cache para dados estáticos (1 dia)"""
    return cached(CacheLevel.STATIC)(func)

def cached_semi_static(func: Callable) -> Callable:
    """Cache para dados semi-estáticos (1 hora)"""
    return cached(CacheLevel.SEMI_STATIC)(func)

def cached_dynamic(func: Callable) -> Callable:
    """Cache para dados dinâmicos (15 min)"""
    return cached(CacheLevel.DYNAMIC)(func)

def cached_volatile(func: Callable) -> Callable:
    """Cache para dados voláteis (5 min)"""
    return cached(CacheLevel.VOLATILE)(func)

# Cache específico para Streamlit
def st_cached_data(ttl: int = 3600, show_spinner: str = "Carregando..."):
    """Wrapper melhorado do st.cache_data"""
    def decorator(func: Callable):
        # Usa cache nativo do Streamlit para melhor integração
        cached_func = st.cache_data(ttl=ttl, show_spinner=show_spinner)(func)
        
        # Adiciona controles extras
        cached_func.clear_cache = lambda: st.cache_data.clear()
        
        return cached_func
    return decorator 