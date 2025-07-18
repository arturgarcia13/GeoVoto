import streamlit as st

def page_app():
    """Página de apresentação da aplicação"""

    st.markdown("""
    # 🗳️ GeoVoto - Sistema de Análise Eleitoral

    ### 📊 Bem-vindo ao Sistema de Visualização de Dados Eleitorais

    O **GeoVoto** é uma plataforma completa para análise e visualização de dados eleitorais, 
    oferecendo insights poderosos através de:

    #### 🎯 Principais Funcionalidades

    - **📈 Dashboard Interativo**: Visualize métricas em tempo real
    - **🗺️ Análise Geográfica**: Mapas e dados geoespaciais  
    - **📊 Gráficos Dinâmicos**: Charts interativos e personalizáveis
    - **🔍 Filtros Avançados**: Segmente dados por múltiplos critérios
    - **📱 Interface Responsiva**: Acesse de qualquer dispositivo

    #### 💡 Como Funciona

    1. **🔐 Faça Login**: Clique na aba "Login" para acessar
    2. **📊 Explore o Dashboard**: Analise dados dos candidatos
    3. **🗺️ Visualize Mapas**: Examine distribuição geográfica
    4. **📈 Compare Resultados**: Use filtros para insights específicos

    #### 🛡️ Segurança e Privacidade

    - ✅ Autenticação segura por email
    - ✅ Dados criptografados
    - ✅ Acesso controlado por perfil
    - ✅ Logs de auditoria

    ---

    **👆 Clique na aba "Login" acima para começar!**
    """)

    # Estatísticas mockadas
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📊 Dados Processados", "1.2M", "↗️ +15%")

    with col2:
        st.metric("🏛️ Municípios", "184", "✅ 100%")

    with col3:
        st.metric("🗳️ Seções Eleitorais", "5.2K", "📈 Ativo")

    with col4:
        st.metric("👥 Usuários Ativos", "342", "↗️ +8%")