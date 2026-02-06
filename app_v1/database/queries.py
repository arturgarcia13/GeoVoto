# app/database/queries.py

from sqlalchemy import text
from database.connection import get_engine
from pathlib import Path
from typing import Optional, Dict

def get_user_by_email(email: str) -> Optional[Dict]:
    engine = get_engine()
    query = text("SELECT * FROM usuarios WHERE email = :email")
    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"email": email}).mappings().fetchone()
        return result
    except Exception as e:
        return f"Erro ao buscar usuário por e-mail: {e}"
    
def update_user_token(email: str, token: str) -> None:
    engine = get_engine()
    query = text("UPDATE usuarios SET token = :token WHERE email = :email")
    try:
        with engine.begin() as conn:  # faz commit automaticamente
            conn.execute(query, {"token": token, "email": email})
    except Exception as e:
        print(f"Erro ao atualizar token do usuário: {e}")


def update_user_type(email: str, tipo: str) -> None:
    """
    Atualiza o tipo de usuário para 'usuário' no banco de dados.
    """
    engine = get_engine()
    query = text("UPDATE usuarios SET tipo = :tipo WHERE email = :email")
    try:
        with engine.begin() as conn:
            conn.execute(query, {"email": email, "tipo": tipo})
        return True
    except Exception as e:
        print(f"Erro ao atualizar tipo de usuário: {e}")

def validate_token(token: str) -> Optional[Dict]:
    engine = get_engine()
    query = text("SELECT * FROM usuarios WHERE token = :token")
    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"token": token}).mappings().fetchone()
        return result
    except Exception as e:
        print(f"Erro ao validar token: {e}")
        return None

def get_tipo_usuario(token: str) -> Optional[str]:
    """
    Retorna o tipo de usuário associado ao token fornecido.
    Se o token não for encontrado, retorna None.
    """
    user = validate_token(token)
    if user:
        return user.get("tipo")
    return None

# Excluir um usuario
def delete_user(email: str) -> bool:
    """
    Exclui um usuário da tabela 'usuarios' pelo e-mail.
    Retorna True se for bem-sucedido, False caso contrário.
    """
    engine = get_engine()
    query = text("DELETE FROM usuarios WHERE email = :email")
    try:
        with engine.begin() as conn:
            result = conn.execute(query, {"email": email})
        return result.rowcount > 0
    except Exception as e:
        print(f"Erro ao excluir usuário: {e}")
        return False


def create_user(nome: str, email: str, tipo: str, token: str) -> bool:
    """
    Insere um novo usuário na tabela 'usuarios'.
    Retorna True se for bem-sucedido, False caso contrário.
    """
    engine = get_engine()
    query = text("""
        INSERT INTO usuarios (nome, email, tipo, token)
        VALUES (:nome, :email, :tipo, :token)
    """)
    try:
        with engine.begin() as conn:
            conn.execute(query, {"nome": nome, "email": email, "tipo": tipo, "token": ""})
        return True
    except Exception as e:
        print(f"Erro ao criar usuário: {e}")
        return False
    
# listar todos os usuários
def list_users() -> Optional[list]:
    """
    Retorna uma lista de todos os usuários cadastrados.
    Se ocorrer um erro, retorna None.
    """
    engine = get_engine()
    query = text("SELECT * FROM usuarios")
    try:
        with engine.connect() as conn:
            result = conn.execute(query).mappings().fetchall()
        return result
    
    except Exception as e:
        print(f"Erro ao listar usuários: {e}")
        return None

def read_sql_file(filename: str) -> str:
    path = Path("app/sql") / filename
    if not path.exists():
        raise FileNotFoundError(f"Arquivo {path} não encontrado.")
    with path.open("r", encoding="utf-8") as f:
        return f.read()