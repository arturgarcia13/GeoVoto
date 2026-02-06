# utils/error_handler.py
import streamlit as st
import logging
import functools
from typing import Callable, Any
from datetime import datetime

# Configuração básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def handle_page_errors(func: Callable) -> Callable:
    """Decorator para tratamento de erros em páginas"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = f"Erro na página {func.__name__}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            st.error("❌ Ocorreu um erro inesperado")
            
            # Mostra detalhes em modo debug
            if st.secrets.get("DEBUG", False):
                st.exception(e)
                st.code(error_msg)
            
            # Botão para tentar novamente
            if st.button("🔄 Tentar Novamente"):
                st.rerun()
                
    return wrapper

def handle_data_errors(func: Callable) -> Callable:
    """Decorator para tratamento de erros de dados"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = f"Erro ao processar dados em {func.__name__}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            st.error("❌ Erro ao processar dados")
            st.info("🔍 Verifique a conexão com banco de dados ou a integridade dos dados")
            
            if st.secrets.get("DEBUG", False):
                st.exception(e)
                
            return None
            
    return wrapper

def safe_execute(func: Callable, *args, fallback_value: Any = None, **kwargs) -> Any:
    """Executa função de forma segura com valor de fallback"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Erro em safe_execute: {str(e)}")
        return fallback_value

class ErrorReporter:
    """Classe para reportar erros de forma estruturada"""
    
    @staticmethod
    def show_data_error(operation: str, details: str = ""):
        """Mostra erro relacionado a dados"""
        st.error(f"❌ Erro na operação: {operation}")
        if details:
            st.info(f"Detalhes: {details}")
    
    @staticmethod
    def show_connection_error():
        """Mostra erro de conexão"""
        st.error("❌ Erro de conexão com banco de dados")
        st.info("🔧 Verifique sua conexão e tente novamente")
    
    @staticmethod
    def show_validation_error(field: str, message: str):
        """Mostra erro de validação"""
        st.error(f"❌ Erro no campo '{field}': {message}")
    
    @staticmethod
    def show_permission_error():
        """Mostra erro de permissão"""
        st.error("🚫 Você não tem permissão para executar esta ação")
    
    @staticmethod
    def log_error(error: Exception, context: str = ""):
        """Registra erro no log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.error(f"[{timestamp}] {context}: {str(error)}", exc_info=True)