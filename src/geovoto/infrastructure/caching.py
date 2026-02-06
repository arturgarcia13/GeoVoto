from typing import Callable, Any
import streamlit as st
from geovoto.config.settings import settings

def cache_data(ttl: int | None = None, show_spinner: str | bool = True) -> Callable:
    """Wrapper around st.cache_data using application settings."""
    def decorator(func: Callable) -> Callable:
        return st.cache_data(ttl=ttl, show_spinner=show_spinner)(func)
    return decorator

def cache_resource(ttl: int | None = None, show_spinner: str | bool = True) -> Callable:
    """Wrapper around st.cache_resource using application settings."""
    def decorator(func: Callable) -> Callable:
        return st.cache_resource(ttl=ttl, show_spinner=show_spinner)(func)
    return decorator


# Specialized cache decorators
def cache_static(func: Callable) -> Callable:
    """Cache for static data (long TTL)."""
    return cache_data(ttl=settings.cache.static_ttl, show_spinner="Loading static data...")(func)

def cache_semi_static(func: Callable) -> Callable:
    """Cache for semi-static data (medium TTL)."""
    return cache_data(ttl=settings.cache.semi_static_ttl, show_spinner="Loading data...")(func)

def cache_dynamic(func: Callable) -> Callable:
    """Cache for dynamic analytics data (short TTL)."""
    return cache_data(ttl=settings.cache.dynamic_ttl, show_spinner="Processing analytics...")(func)
