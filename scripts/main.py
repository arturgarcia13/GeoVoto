import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Dashboard de Análise Eleitoral",
    page_icon="📊",
    layout="wide"
)


##########################################################!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!NÃO MEXER PARTE DE LINK

# --- CONEXÃO COM O BANCO DE DADOS (CACHEADA) ---
@st.cache_resource
def get_engine():
    try:
        database_url = st.secrets["POSTGRES_URL"]
        return create_engine(database_url, connect_args={"sslmode": "require"})
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

engine = get_engine()

##########################################################!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!NÃO MEXER PARTE DE LINK


# --- CARREGAMENTO DOS DADOS (CACHEADO) ---
@st.cache_data(ttl=600)
def load_data(_engine):
    if _engine is None: return pd.DataFrame()
    query = text("""
        SELECT
            m."Nome_Municipio" AS nome_municipio, m."Unidade_Geografica" AS uf,
            c."Nome_Urna" AS nome_urna_candidato, c."FK_Sigla_Partido" AS sigla_partido,
            p."Num_Partido" AS numero_partido, v."Zona" AS zona_eleitoral,
            v."Votos_Nominais_Candidato" AS votos_candidato
        FROM public.votacao_candidato_municipio_zona AS v
        LEFT JOIN public.candidato AS c ON v."FK_Num_Candidato" = c."Num_Candidato"
        LEFT JOIN public.municipio AS m ON v."FK_Cod_Municipio" = m."Cod_IBGE"
        LEFT JOIN public.partido AS p ON c."FK_Sigla_Partido" = p."Sigla_Partido"
        WHERE v."Votos_Nominais_Candidato" IS NOT NULL AND v."Votos_Nominais_Candidato" > 0;
    """)
    try:
        with _engine.connect() as conn:
            return pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Erro ao carregar os dados do dashboard: {e}")
        return pd.DataFrame()

##########################################################!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!NÃO MEXER PARTE DE LINK

# --- FUNÇÃO DO DASHBOARD (COMPLETA) ---
def build_dashboard():
    """Constrói e exibe o dashboard principal."""
    df = load_data(engine)
    
    st.sidebar.success(f"Logado como: {st.session_state.email}")
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.title("📊 Dashboard de Análise Eleitoral")
    st.markdown("Use os filtros na barra lateral para explorar os resultados.")
    
    st.sidebar.header("Filtros")
    if not df.empty:
        municipios = sorted(df['nome_municipio'].unique())
        municipio_selecionado = st.sidebar.selectbox("Selecione um Município", ["Todos os Municípios"] + municipios)
        partidos = sorted(df['sigla_partido'].unique())
        partido_selecionado = st.sidebar.selectbox("Selecione um Partido", ["Todos os Partidos"] + partidos)

        df_filtrado = df.copy()
        if municipio_selecionado != "Todos os Municípios": df_filtrado = df_filtrado[df_filtrado['nome_municipio'] == municipio_selecionado]
        if partido_selecionado != "Todos os Partidos": df_filtrado = df_filtrado[df_filtrado['sigla_partido'] == partido_selecionado]

        if df_filtrado.empty:
            st.warning("Nenhum dado encontrado para os filtros selecionados.")
        else:
            # --- SEÇÃO DE MÉTRICAS (KPIs) ---
            # Esta parte já estava funcionando, agora completa.
            total_votos = int(df_filtrado['votos_candidato'].sum())
            num_candidatos = df_filtrado['nome_urna_candidato'].nunique()
            num_partidos = df_filtrado['sigla_partido'].nunique()

            col1, col2, col3 = st.columns(3)
            col1.metric("Total de Votos Válidos", f"{total_votos:,}".replace(",", "."))
            col2.metric("Nº de Candidatos", num_candidatos)
            col3.metric("Nº de Partidos", num_partidos)

            st.markdown("---") # Linha divisória

            # --- SEÇÃO DE GRÁFICOS (ADICIONADA DE VOLTA) ---
            col_graf1, col_graf2 = st.columns(2)

            with col_graf1:
                st.subheader("Top 10 Candidatos Mais Votados")
                votos_por_candidato = df_filtrado.groupby('nome_urna_candidato')['votos_candidato'].sum().sort_values(ascending=False).head(10)
                st.bar_chart(votos_por_candidato)

            with col_graf2:
                st.subheader("Distribuição de Votos por Partido")
                votos_por_partido = df_filtrado.groupby('sigla_partido')['votos_candidato'].sum().sort_values(ascending=False)
                st.bar_chart(votos_por_partido, color="#FF4B4B") # Exemplo de cor
            
            st.markdown("---") # Linha divisória

            # --- SEÇÃO DE DADOS DETALHADOS (ADICIONADA DE VOLTA) ---
            with st.expander("Ver dados detalhados da seleção"):
                st.dataframe(df_filtrado, use_container_width=True)

    else:
        st.error("Não foi possível carregar os dados. Verifique a conexão e a query.")


# --- LÓGICA DA TELA DE LOGIN SIMULADA ---
def login_screen():
    st.title("Bem-vindo ao Dashboard Eleitoral!")
    st.subheader("Login de Usuário")

    if 'login_step' not in st.session_state:
        st.session_state.login_step = "enter_email"

    # Etapa 1: Pedir o e-mail
    if st.session_state.login_step == "enter_email":
        with st.form("email_form"):
            email = st.text_input("Seu e-mail", placeholder="aluno@email.com")
            submitted = st.form_submit_button("Efetuar login")
            if submitted and email:
                st.session_state.email = email
                st.session_state.login_step = "Prosseguir"
                st.rerun()

    # Etapa 2: Simular o clique no link
    if st.session_state.login_step == "Prosseguir":
        with st.form("password_form"):
            # Usamos type="password" para que o texto digitado não seja exibido
            password = st.text_input("Senha", type="password")
            submitted = st.form_submit_button("Verificar e Entrar")
            if submitted and password: # Apenas verificamos se algo foi digitado
                st.session_state.logged_in = True
                del st.session_state.login_step # Limpa a etapa de login
                st.rerun()
            elif submitted and not password:
                st.warning("Por favor, insira uma senha.")


# --- CONTROLE PRINCIPAL DO FLUXO DO APP ---
if st.session_state.get("logged_in", False):
    build_dashboard()
else:
    login_screen()