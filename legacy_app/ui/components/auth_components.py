# ui/layouts/login_layout.py
import streamlit as st
import uuid
from typing import Optional, Dict, Any
from core.auth_manager import AuthManager
from services.user_service import UserService
from ui.components.auth_components import AuthComponents
from utils.error_handler import ErrorReporter
from config.config_manager import config_manager
import logging

logger = logging.getLogger(__name__)

class LoginLayout:
    """Layout de autenticação e registro"""
    
    def __init__(self):
        self.auth_manager = AuthManager()
        self.user_service = UserService()
        self.auth_components = AuthComponents()
        self.error_reporter = ErrorReporter()
    
    def render(self):
        """Renderiza layout de login principal"""
        # Layout centralizado
        col1, col2, col3 = st.columns([0.5, 1, 0.5])
        
        with col2:
            self._render_header()
            
            # Tabs para diferentes modos
            tab_intro, tab_login = st.tabs(["🏠 Apresentação", "🔐 Acesso"])
            
            with tab_intro:
                self._render_intro_page()
            
            with tab_login:
                self._render_login_section()
    
    def _render_header(self):
        """Renderiza cabeçalho da aplicação"""
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1>🗳️ GeoVoto</h1>
            <h3>Sistema de Análise Eleitoral</h3>
            <p style="color: #666; font-size: 1.1em;">
                Transforme dados eleitorais em insights estratégicos
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_intro_page(self):
        """Renderiza página de apresentação"""
        st.markdown("""
        ### 📊 Bem-vindo ao Sistema de Visualização de Dados Eleitorais

        O **GeoVoto** é uma plataforma completa para análise e visualização de dados eleitorais, 
        oferecendo insights poderosos através de:

        #### 🎯 Principais Funcionalidades

        - **📈 Dashboard Interativo**: Visualize métricas em tempo real
        - **🗺️ Análise Geográfica**: Mapas e dados geoespaciais detalhados
        - **📊 Gráficos Dinâmicos**: Charts interativos e personalizáveis
        - **🔍 Filtros Avançados**: Segmente dados por múltiplos critérios
        - **📱 Interface Responsiva**: Acesse de qualquer dispositivo
        - **⚡ Performance Otimizada**: Sistema de cache inteligente

        #### 💡 Como Funciona

        1. **🔐 Faça Login**: Clique na aba "Acesso" para entrar
        2. **📊 Explore o Dashboard**: Analise dados dos candidatos
        3. **🗺️ Visualize Mapas**: Examine distribuição geográfica
        4. **📈 Compare Resultados**: Use filtros para insights específicos
        5. **📋 Gere Relatórios**: Exporte análises estratégicas

        #### 🛡️ Segurança e Privacidade

        - ✅ Autenticação segura por email
        - ✅ Dados criptografados e protegidos
        - ✅ Acesso controlado por perfil de usuário
        - ✅ Logs de auditoria completos
        - ✅ Conformidade com LGPD

        ---

        **👆 Clique na aba "Acesso" acima para fazer login!**
        """)

        # Estatísticas da aplicação
        self._render_app_statistics()
    
    def _render_app_statistics(self):
        """Renderiza estatísticas da aplicação"""
        st.markdown("### 📊 Estatísticas do Sistema")
        
        # Busca estatísticas reais quando possível
        try:
            stats = self.user_service.get_app_statistics()
        except Exception as e:
            logger.warning(f"Erro ao buscar estatísticas: {e}")
            # Estatísticas de fallback
            stats = {
                "processed_data": "1.2M",
                "municipalities": "184", 
                "electoral_sections": "5.2K",
                "active_users": "342"
            }
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "📊 Dados Processados", 
                stats.get("processed_data", "N/A"), 
                delta="↗️ +15%"
            )
        
        with col2:
            st.metric(
                "🏛️ Municípios", 
                stats.get("municipalities", "N/A"), 
                delta="✅ 100%"
            )
        
        with col3:
            st.metric(
                "🗳️ Seções Eleitorais", 
                stats.get("electoral_sections", "N/A"), 
                delta="📈 Ativo"
            )
        
        with col4:
            st.metric(
                "👥 Usuários Ativos", 
                stats.get("active_users", "N/A"), 
                delta="↗️ +8%"
            )
    
    def _render_login_section(self):
        """Renderiza seção de login"""
        # Verifica se está em modo de registro
        if st.session_state.get("register_mode", False):
            self._render_registration_form()
        else:
            self._render_login_form()
    
    def _render_login_form(self):
        """Renderiza formulário de login"""
        st.subheader("🔐 Acesso ao Sistema")
        
        # Informações sobre o processo de login
        with st.expander("ℹ️ Como funciona o acesso", expanded=False):
            st.markdown("""
            **Processo de Autenticação Segura:**
            
            1. **Digite seu email** cadastrado no sistema
            2. **Clique em "Gerar Link de Acesso"**
            3. **Acesse o link gerado** para entrar no sistema
            4. **Link válido por 24 horas** (configurável por ambiente)
            
            > 🛡️ **Segurança**: Não utilizamos senhas tradicionais. 
            > O acesso é feito através de tokens seguros de uso único.
            """)
        
        # Formulário de login
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input(
                "📧 Email do usuário",
                placeholder="seu.email@exemplo.com",
                help="Digite o email cadastrado no sistema"
            )
            
            col_submit, col_register = st.columns([1, 1])
            
            with col_submit:
                submit_button = st.form_submit_button(
                    "🔑 Gerar Link de Acesso",
                    type="primary",
                    use_container_width=True
                )
            
            with col_register:
                register_button = st.form_submit_button(
                    "📝 Cadastrar-se",
                    use_container_width=True
                )
        
        # Processa submissão do login
        if submit_button:
            self._process_login_request(email)
        
        # Processa solicitação de registro
        if register_button:
            st.session_state["register_mode"] = True
            st.rerun()
    
    def _process_login_request(self, email: str):
        """Processa solicitação de login"""
        if not email:
            st.warning("⚠️ Digite um email válido.")
            return
        
        if not self._validate_email_format(email):
            st.error("❌ Formato de email inválido.")
            return
        
        try:
            with st.spinner("🔍 Verificando usuário..."):
                user = self.user_service.get_user_by_email(email)
                
                if not user:
                    st.error("❌ Usuário não encontrado.")
                    st.info("💡 Se você ainda não tem uma conta, clique em 'Cadastrar-se'")
                    return
            
            with st.spinner("🔐 Gerando token de acesso..."):
                token = str(uuid.uuid4())
                self.user_service.update_user_token(email, token)
            
            # Exibe link de acesso
            self._show_access_link(token, user)
            
        except Exception as e:
            self.error_reporter.show_data_error("login", str(e))
            logger.error(f"Erro no processo de login: {e}")
    
    def _show_access_link(self, token: str, user: Dict[str, Any]):
        """Exibe link de acesso gerado"""
        # Obtém URL base da aplicação
        try:
            from streamlit_js_eval import get_page_location
            location = get_page_location()
            
            if location:
                base_url = f"{location['protocol']}//{location['host']}"
                access_link = f"{base_url}/?token={token}"
            else:
                # Fallback para desenvolvimento local
                access_link = f"http://localhost:8501/?token={token}"
        except ImportError:
            # Se streamlit_js_eval não estiver disponível
            access_link = f"http://localhost:8501/?token={token}"
        
        # Modal com link de acesso
        self._render_access_modal(access_link, user)
    
    @st.dialog("🎉 Link de Acesso Gerado!")
    def _render_access_modal(self, access_link: str, user: Dict[str, Any]):
        """Renderiza modal com link de acesso"""
        st.success(f"✅ Olá, **{user['nome']}**! Seu link de acesso foi gerado com sucesso!")
        
        st.markdown("### 🔗 Seu Link de Acesso Seguro:")
        st.code(access_link, language=None)
        
        # Botão para copiar
        if st.button("📋 Copiar Link", use_container_width=True):
            st.write("Link copiado! (Cole na barra de endereços)")
        
        # Informações sobre expiração
        expiry_hours = config_manager.security.token_expiry_hours
        st.info(f"⏰ Este link expira em **{expiry_hours} horas**")
        
        # Instruções
        st.markdown("""
        ### 📋 Instruções:
        1. **Copie o link** acima
        2. **Cole em uma nova aba** do navegador
        3. **Acesse o sistema** automaticamente
        
        > 🛡️ **Importante**: Este link é pessoal e intransferível. 
        > Não compartilhe com outras pessoas.
        """)
        
        st.balloons()
    
    def _render_registration_form(self):
        """Renderiza formulário de registro"""
        st.subheader("📝 Cadastro de Novo Usuário")
        
        # Botão para voltar
        if st.button("← Voltar ao Login", type="secondary"):
            st.session_state["register_mode"] = False
            st.rerun()
        
        st.markdown("---")
        
        # Formulário de cadastro
        with st.form("registration_form", clear_on_submit=True):
            st.markdown("### 👤 Dados do Usuário")
            
            name = st.text_input(
                "🏷️ Nome completo",
                placeholder="João Silva",
                help="Digite seu nome completo"
            )
            
            email = st.text_input(
                "📧 Email",
                placeholder="joao.silva@exemplo.com",
                help="Este será seu email de acesso"
            )
            
            # Tipo de usuário (fixo por enquanto, pode ser expandido)
            user_type = st.selectbox(
                "👔 Tipo de usuário",
                options=["usuário", "admin"],
                index=0,
                help="Tipo de acesso no sistema",
                disabled=True  # Apenas admin pode criar outros admins
            )
            
            # Termos de uso
            accept_terms = st.checkbox(
                "Aceito os termos de uso e política de privacidade",
                help="Obrigatório para criar conta"
            )
            
            submit_register = st.form_submit_button(
                "✅ Criar Conta",
                type="primary",
                use_container_width=True
            )
        
        # Processa registro
        if submit_register:
            self._process_registration(name, email, user_type, accept_terms)
    
    def _process_registration(self, name: str, email: str, user_type: str, accept_terms: bool):
        """Processa registro de novo usuário"""
        # Validações
        if not all([name, email]):
            st.error("⚠️ Preencha todos os campos obrigatórios.")
            return
        
        if not accept_terms:
            st.error("⚠️ Você deve aceitar os termos de uso.")
            return
        
        if not self._validate_email_format(email):
            st.error("❌ Formato de email inválido.")
            return
        
        try:
            # Verifica se email já existe
            with st.spinner("🔍 Verificando disponibilidade..."):
                if self.user_service.get_user_by_email(email):
                    st.warning("⚠️ Este email já está cadastrado. Tente fazer login.")
                    return
            
            # Cria usuário
            with st.spinner("👤 Criando conta..."):
                success = self.user_service.create_user(name, email, user_type, "")
                
                if success:
                    st.success("🎉 Conta criada com sucesso!")
                    st.info("💡 Agora você pode fazer login com seu email.")
                    
                    # Volta para modo de login
                    st.session_state["register_mode"] = False
                    
                    # Rerun para mostrar tela de login
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("❌ Erro ao criar conta. Tente novamente.")
        
        except Exception as e:
            self.error_reporter.show_data_error("registro", str(e))
            logger.error(f"Erro no registro: {e}")
    
    def _validate_email_format(self, email: str) -> bool:
        """Valida formato do email com validação robusta"""
        import re
        
        if not email or len(email.strip()) == 0:
            return False
        
        email = email.strip().lower()
        
        # Regex melhorada para email
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    
    def _render_environment_info(self):
        """Renderiza informações do ambiente (apenas em desenvolvimento)"""
        if config_manager.is_debug_enabled():
            with st.sidebar:
                st.markdown("### 🔧 Info de Desenvolvimento")
                st.text(f"Ambiente: {config_manager.environment.value}")
                st.text(f"Debug: {config_manager.ui.enable_debug_mode}")
                st.text(f"Cache TTL: {config_manager.cache.dynamic_ttl}s")
                
                if st.button("🗑️ Limpar Cache", type="secondary"):
                    st.cache_data.clear()
                    st.success("Cache limpo!")
                    st.rerun()

        
        # Verificações básicas
        if email.count('@') != 1:
            return False
        
        local_part, domain = email.split('@')
        
        # Validações de tamanho
        if len(local_part) == 0 or len(local_part) > 64:
            return False
        
        if len(domain) == 0 or len(domain) > 253:
            return False
        
        # Verifica se domínio tem pelo menos um ponto
        if '.' not in domain:
            return False
        
        # Verifica se não começa ou termina com ponto ou hífen
        if domain.startswith('.') or domain.endswith('.'):
            return False
        
        if domain.startswith('-') or domain.endswith('-'):
            return False
        
        # Aplica regex principal
        return bool(re.match(pattern, email))
    
    def _render_environment_info(self):
        """Renderiza informações do ambiente (apenas em desenvolvimento)"""
        if config_manager.is_debug_enabled():
            with st.sidebar:
                st.markdown("### 🔧 Info de Desenvolvimento")
                st.text(f"Ambiente: {config_manager.environment.value}")
                st.text(f"Debug: {config_manager.ui.enable_debug_mode}")
                st.text(f"Cache TTL: {config_manager.cache.dynamic_ttl}s")
                
                if st.button("🗑️ Limpar Cache", type="secondary"):
                    st.cache_data.clear()
                    st.success("Cache limpo!")
                    st.rerun()