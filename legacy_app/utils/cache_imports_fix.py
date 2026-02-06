# utils/cache_imports_fix.py - Correção definitiva para imports
"""
Este arquivo resolve todos os problemas de import do sistema de cache
Usa apenas funcionalidades simples e funcionais do Streamlit
"""

import streamlit as st
from config.config_manager import config_manager

# Cache específico para diferentes tipos de dados usando apenas st.cache_data
def cache_electoral_data(func):
    """Cache para dados eleitorais (1 hora)"""
    ttl = getattr(config_manager.cache, 'semi_static_ttl', 3600)
    return st.cache_data(ttl=ttl, show_spinner="🗳️ Carregando dados eleitorais...")(func)

def cache_geographic_data(func):
    """Cache para dados geográficos (2 horas)"""
    ttl = getattr(config_manager.cache, 'static_ttl', 7200)
    return st.cache_data(ttl=ttl, show_spinner="🗺️ Carregando dados geográficos...")(func)

def cache_analytics_data(func):
    """Cache para dados analíticos (15 minutos)"""
    ttl = getattr(config_manager.cache, 'dynamic_ttl', 900)
    return st.cache_data(ttl=ttl, show_spinner="📊 Processando análises...")(func)

def cache_user_data(func):
    """Cache para dados de usuário (5 minutos)"""
    ttl = getattr(config_manager.cache, 'volatile_ttl', 300)
    return st.cache_data(ttl=ttl, show_spinner="👤 Carregando dados do usuário...")(func)

def cached_dashboard_data(ttl=None, show_spinner="📈 Atualizando dashboard..."):
    """Cache para dados do dashboard"""
    if ttl is None:
        ttl = getattr(config_manager.cache, 'semi_static_ttl', 3600)
    return st.cache_data(ttl=ttl, show_spinner=show_spinner)

def get_cache_stats():
    """Retorna estatísticas básicas do cache"""
    cache_keys = [key for key in st.session_state.keys() if key.startswith("cache_")]
    return {
        "total_cached_items": len(cache_keys),
        "cache_size_mb": len(str(st.session_state)) / 1024 / 1024,
        "cache_type": "streamlit_native",
        "status": "active"
    }

def clear_all_cache():
    """Limpa todo o cache"""
    st.cache_data.clear()
    
    # Limpa cache do session_state também
    cache_keys = [key for key in st.session_state.keys() if key.startswith("cache_")]
    for key in cache_keys:
        del st.session_state[key]

def clear_cache_by_pattern(pattern: str):
    """Limpa cache por padrão"""
    keys_to_remove = [key for key in st.session_state.keys() if pattern in key]
    for key in keys_to_remove:
        del st.session_state[key]
    
    # Para Streamlit native cache, limpa tudo
    st.cache_data.clear()

# Aliases para compatibilidade com nomes antigos
cached_dynamic = cache_analytics_data
cached_static = cache_electoral_data
cached_semi_static = cache_electoral_data
cached_user_data = cache_user_data
cached_query = cache_analytics_data

# Classe para monitoramento básico
class CacheMonitor:
    @staticmethod
    def get_hit_rate():
        return 75.0  # Valor simulado
    
    @staticmethod
    def get_memory_usage():
        cache_size = len(str(st.session_state)) / 1024 / 1024
        return {
            "cache_size_mb": round(cache_size, 2),
            "max_recommended_mb": 50,
            "usage_percentage": min(100, (cache_size / 50) * 100)
        }
    
    @staticmethod
    def should_clear_cache():
        memory_info = CacheMonitor.get_memory_usage()
        return memory_info["usage_percentage"] > 80
    
    @staticmethod
    def auto_cleanup():
        if CacheMonitor.should_clear_cache():
            clear_all_cache()

# Função de verificação melhorada
def verify_cache_imports():
    """Verifica se todos os imports estão funcionando"""
    try:
        @cache_electoral_data
        def test_electoral():
            return "OK"
        
        @cache_geographic_data  
        def test_geographic():
            return "OK"
        
        @cache_analytics_data
        def test_analytics():
            return "OK"
        
        @cache_user_data
        def test_user():
            return "OK"
        
        # Testa execução
        assert test_electoral() == "OK"
        assert test_geographic() == "OK"
        assert test_analytics() == "OK"
        assert test_user() == "OK"
        
        return {
            "electoral_cache": "✅ OK",
            "geographic_cache": "✅ OK", 
            "analytics_cache": "✅ OK",
            "user_cache": "✅ OK",
            "status": "✅ ALL_IMPORTS_WORKING"
        }
        
    except Exception as e:
        return {
            "status": "❌ ERROR",
            "error": str(e),
            "fallback": "Using basic Streamlit cache"
        }

# Log de status para debugging
if config_manager.is_debug_enabled():
    result = verify_cache_imports()
    print("🔧 Cache imports verification:", result)