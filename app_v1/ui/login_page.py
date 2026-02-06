import streamlit as st
from auth.login import login_screen, login_scan
from auth.register import register_user


# Função alternativa mais simples (sem classe)
def page_login():
    # Processa token da URL
    query_params = st.query_params
    token = query_params.get("token", None)
    
    if token and not st.session_state.get("token_processed", False):
        st.session_state["token_processed"] = True
        
        with st.spinner("Processando login..."):
            if login_scan(token):
                st.session_state["logged_in"] = True
                st.success("✅ Login realizado!")
                st.rerun()
                return
            else:
                st.error("❌ Token inválido")
    
    # Interface principal
    if st.session_state["register_mode"]:
        st.title("Cadastro")
        register_user()
        if st.button("Voltar"):
            st.session_state["register_mode"] = False
            st.rerun()
    else:
        login_screen()
        if st.button("Cadastrar"):
            st.session_state["register_mode"] = True
            st.rerun()