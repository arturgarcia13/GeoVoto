import streamlit as st

@st.cache_resource
def cached_engine(_factory_func):
    return _factory_func()

@st.cache_data(ttl=600)
def cached_query(query_func, *args):
    return query_func(*args)