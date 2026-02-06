from typing import List, Optional, Mapping, Any
from sqlalchemy import text, Engine
from geovoto.domain.user import User
from geovoto.infrastructure.database.connection import get_engine
import logging

logger = logging.getLogger(__name__)

class UserRepository:
    def __init__(self, engine: Optional[Engine] = None):
        self.engine = engine or get_engine()

    def get_by_email(self, email: str) -> Optional[dict]:
        query = text("SELECT * FROM usuarios WHERE email = :email")
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"email": email}).mappings().fetchone()
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error fetching user by email: {e}")
            return None

    def update_token(self, email: str, token: str) -> None:
        query = text("UPDATE usuarios SET token = :token WHERE email = :email")
        try:
            with self.engine.begin() as conn:
                conn.execute(query, {"token": token, "email": email})
        except Exception as e:
            logger.error(f"Error updating user token: {e}")

    def update_type(self, email: str, user_type: str) -> bool:
        query = text("UPDATE usuarios SET tipo = :tipo WHERE email = :email")
        try:
            with self.engine.begin() as conn:
                conn.execute(query, {"email": email, "tipo": user_type})
            return True
        except Exception as e:
            logger.error(f"Error updating user type: {e}")
            return False

    def validate_token(self, token: str) -> Optional[dict]:
        query = text("SELECT * FROM usuarios WHERE token = :token")
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"token": token}).mappings().fetchone()
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error validating token: {e}")
            return None

    def delete(self, email: str) -> bool:
        query = text("DELETE FROM usuarios WHERE email = :email")
        try:
            with self.engine.begin() as conn:
                result = conn.execute(query, {"email": email})
            return result.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False

    def create(self, nome: str, email: str, tipo: str, token: str = "") -> bool:
        query = text("""
            INSERT INTO usuarios (nome, email, tipo, token)
            VALUES (:nome, :email, :tipo, :token)
        """)
        try:
            with self.engine.begin() as conn:
                conn.execute(query, {"nome": nome, "email": email, "tipo": tipo, "token": token})
            return True
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False

    def list_all(self) -> Optional[List[dict]]:
        query = text("SELECT * FROM usuarios")
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query).mappings().fetchall()
            return [dict(row) for row in result]
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return None
