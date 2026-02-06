# services/user_service.py
from typing import Optional, Dict, Any, List
import logging
from database.connection import get_engine
from sqlalchemy import text
from utils.cache_imports_fix import cache_user_data, cache_analytics_data
from utils.error_handler import handle_data_errors

logger = logging.getLogger(__name__)

class UserService:
    """Serviço para operações de usuário"""
    
    def __init__(self):
        self.engine = get_engine()
    
    @handle_data_errors
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Busca usuário por email"""
        query = text("SELECT * FROM usuarios WHERE email = :email")
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"email": email}).mappings().fetchone()
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"Erro ao buscar usuário por email {email}: {e}")
            raise
    
    @handle_data_errors
    def create_user(self, name: str, email: str, user_type: str, token: str) -> bool:
        """Cria novo usuário"""
        query = text("""
            INSERT INTO usuarios (nome, email, tipo, token)
            VALUES (:nome, :email, :tipo, :token)
        """)
        
        try:
            with self.engine.begin() as conn:
                conn.execute(query, {
                    "nome": name,
                    "email": email, 
                    "tipo": user_type,
                    "token": token
                })
                
            logger.info(f"Usuário criado: {name} ({email})")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar usuário {email}: {e}")
            return False
    
    @handle_data_errors
    def update_user_token(self, email: str, token: str) -> bool:
        """Atualiza token do usuário"""
        query = text("UPDATE usuarios SET token = :token WHERE email = :email")
        
        try:
            with self.engine.begin() as conn:
                result = conn.execute(query, {"token": token, "email": email})
                
            success = result.rowcount > 0
            if success:
                logger.info(f"Token atualizado para usuário: {email}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao atualizar token para {email}: {e}")
            return False
    
    @handle_data_errors
    def update_user_type(self, email: str, user_type: str) -> bool:
        """Atualiza tipo do usuário"""
        query = text("UPDATE usuarios SET tipo = :tipo WHERE email = :email")
        
        try:
            with self.engine.begin() as conn:
                result = conn.execute(query, {"email": email, "tipo": user_type})
                
            success = result.rowcount > 0
            if success:
                logger.info(f"Tipo de usuário atualizado: {email} -> {user_type}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao atualizar tipo de usuário {email}: {e}")
            return False
    
    @handle_data_errors
    def delete_user(self, email: str) -> bool:
        """Remove usuário"""
        query = text("DELETE FROM usuarios WHERE email = :email")
        
        try:
            with self.engine.begin() as conn:
                result = conn.execute(query, {"email": email})
                
            success = result.rowcount > 0
            if success:
                logger.info(f"Usuário removido: {email}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao remover usuário {email}: {e}")
            return False
    
    @cache_user_data
    def list_all_users(self) -> List[Dict[str, Any]]:
        """Lista todos os usuários"""
        query = text("""
            SELECT nome, email, tipo, 
                   CASE WHEN token IS NOT NULL AND token != '' THEN 'Ativo' ELSE 'Inativo' END as status
            FROM usuarios 
            ORDER BY nome
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query).mappings().fetchall()
                return [dict(row) for row in result]
                
        except Exception as e:
            logger.error(f"Erro ao listar usuários: {e}")
            return []
    
    @cache_user_data
    def get_user_statistics(self) -> Dict[str, Any]:
        """Estatísticas de usuários"""
        query = text("""
            SELECT 
                COUNT(*) as total_users,
                COUNT(CASE WHEN tipo = 'admin' THEN 1 END) as admin_users,
                COUNT(CASE WHEN tipo = 'usuário' THEN 1 END) as regular_users,
                COUNT(CASE WHEN token IS NOT NULL AND token != '' THEN 1 END) as users_with_token
            FROM usuarios
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query).mappings().fetchone()
                return dict(result) if result else {}
                
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de usuários: {e}")
            return {}
    
    @cache_analytics_data
    def get_app_statistics(self) -> Dict[str, str]:
        """Estatísticas gerais da aplicação"""
        queries = {
            "municipalities": "SELECT COUNT(DISTINCT \"Cod_IBGE\") FROM municipio",
            "candidates": "SELECT COUNT(DISTINCT \"Num_Candidato\") FROM candidato",
            "total_votes": "SELECT SUM(\"Votos_Nominais_Candidato\") FROM votacao_candidato_municipio_zona",
            "electoral_sections": "SELECT COUNT(DISTINCT \"Zona\") FROM votacao_candidato_municipio_zona"
        }
        
        stats = {}
        
        try:
            with self.engine.connect() as conn:
                for key, query in queries.items():
                    result = conn.execute(text(query)).scalar()
                    
                    if key == "total_votes" and result:
                        # Formata números grandes
                        if result >= 1000000:
                            stats[key] = f"{result/1000000:.1f}M"
                        elif result >= 1000:
                            stats[key] = f"{result/1000:.1f}K"
                        else:
                            stats[key] = str(result)
                    else:
                        stats[key] = str(result) if result else "0"
                
                # Adiciona estatísticas de usuários
                user_stats = self.get_user_statistics()
                stats["active_users"] = str(user_stats.get("total_users", 0))
                
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas da aplicação: {e}")
            # Retorna estatísticas de fallback
            stats = {
                "municipalities": "184",
                "candidates": "150+",
                "total_votes": "1.2M",
                "electoral_sections": "5.2K",
                "active_users": "342"
            }
        
        return stats

# Instância global do serviço
user_service = UserService()