import streamlit as st
from database.queries import list_users, delete_user, update_user_type

def user_manager():
    st.title("Gerenciamento de Usuários")

    # Lista usuários
    users = list_users()
    if not users:
        st.warning("Nenhum usuário encontrado.")
        return

    # Inicializa estado de confirmação se não existir
    if 'confirm_delete' not in st.session_state:
        st.session_state.confirm_delete = {}

    for user in users:
        user_email = user['email']
        
        # Container para cada usuário
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{user['nome']}** ({user_email}) - Tipo: {user['tipo']}")
            
            with col2:
                _handle_delete_user(user)
            
            with col3:
                _handle_user_type_change(user)

def _handle_delete_user(user):
    """Gerencia a exclusão de usuário com confirmação"""
    user_email = user['email']
    confirm_key = f"confirm_delete_{user_email}"
    
    # Se não está em modo de confirmação
    if confirm_key not in st.session_state.confirm_delete:
        if st.button("Excluir", key=f"delete_{user_email}", type="secondary"):
            st.session_state.confirm_delete[confirm_key] = True
            st.rerun()
    else:
        # Modo de confirmação
        st.warning("Tem certeza?")
        col_yes, col_no = st.columns(2)
        
        with col_yes:
            if st.button("Sim", key=f"confirm_yes_{user_email}", type="primary"):
                if delete_user(user_email):
                    st.success(f"Usuário {user['nome']} excluído!")
                    # Limpa o estado de confirmação
                    if confirm_key in st.session_state.confirm_delete:
                        del st.session_state.confirm_delete[confirm_key]
                    st.rerun()
                else:
                    st.error("Erro ao excluir usuário.")
        
        with col_no:
            if st.button("Não", key=f"confirm_no_{user_email}"):
                # Cancela a confirmação
                if confirm_key in st.session_state.confirm_delete:
                    del st.session_state.confirm_delete[confirm_key]
                st.rerun()

def _handle_user_type_change(user):
    """Gerencia a mudança de tipo de usuário"""
    user_email = user['email']
    user_type = user['tipo']
    
    if user_type == 'admin':
        if st.button("Tornar Usuário", key=f"revoke_admin_{user_email}"):
            if update_user_type(user_email, 'usuário'):
                st.success(f"{user['nome']} agora é usuário regular!")
                st.rerun()
            else:
                st.error("Erro ao alterar tipo do usuário.")
                
    elif user_type == 'usuário':
        if st.button("Tornar Admin", key=f"make_admin_{user_email}"):
            if update_user_type(user_email, 'admin'):
                st.success(f"{user['nome']} agora é administrador!")
                st.rerun()
            else:
                st.error("Erro ao alterar tipo do usuário.")