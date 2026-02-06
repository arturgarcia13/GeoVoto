# ui/pages/users_page.py
import streamlit as st
from ui.pages.base_page import BasePage
from core.auth_manager import AuthManager
from ui.manager_user import user_manager

class UsersPage(BasePage):
    """Página de gerenciamento de usuários (apenas admins)"""
    
    def __init__(self):
        super().__init__("👥 Gerenciamento de Usuários")
        self.auth_manager = AuthManager()
    
    def _render_content(self):
        """Renderiza conteúdo da página de usuários"""
        
        # Verifica se é admin
        if not self.auth_manager.is_admin():
            st.error("🚫 Acesso restrito a administradores")
            st.stop()
        
        try:
            # Usa o gerenciador de usuários existente
            user_manager()
            
        except Exception as e:
            self.show_error("Erro ao carregar gerenciamento de usuários", e)
            
            # Fallback básico
            self._render_fallback_user_management()
    
    def _render_fallback_user_management(self):
        """Gerenciamento básico em caso de erro"""
        st.warning("Carregando gerenciamento em modo simplificado...")
        
        st.markdown("""
        ### 👥 Gerenciamento de Usuários
        
        **Funcionalidades disponíveis:**
        - Visualizar usuários cadastrados
        - Alterar tipos de usuário
        - Remover usuários
        - Estatísticas de acesso
        
        💡 Para funcionalidade completa, verifique a conexão com o banco de dados.
        """)