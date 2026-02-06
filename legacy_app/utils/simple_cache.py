# utils/simple_cache.py - Solução temporária para compatibilidade
import streamlit as st
from functools import wraps
from typing import Callable

def simple_cached_static(func: Callable) -> Callable:
    """Cache simples para dados estáticos usando Streamlit"""
    return st.cache_data(ttl=86400, show_spinner="Carregando dados estáticos...")(func)

def simple_cached_semi_static(func: Callable) -> Callable:
    """Cache simples para dados semi-estáticos usando Streamlit"""
    return st.cache_data(ttl=3600, show_spinner="Carregando dados...")(func)

def simple_cached_dynamic(func: Callable) -> Callable:
    """Cache simples para dados dinâmicos usando Streamlit"""
    return st.cache_data(ttl=900, show_spinner="Atualizando dados...")(func)

def simple_cached_volatile(func: Callable) -> Callable:
    """Cache simples para dados voláteis usando Streamlit"""
    return st.cache_data(ttl=300, show_spinner="Carregando...")(func)