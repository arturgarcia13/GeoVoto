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
            print(result)
        return result
    except Exception as e:
        print(f"Erro ao buscar usuário por e-mail: {e}")
        return None

def update_user_token(email: str, token: str) -> None:
    engine = get_engine()
    query = text("UPDATE usuarios SET token = :token WHERE email = :email")
    try:
        with engine.begin() as conn:  # faz commit automaticamente
            conn.execute(query, {"token": token, "email": email})
    except Exception as e:
        print(f"Erro ao atualizar token do usuário: {e}")

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

def read_sql_file(filename: str) -> str:
    path = Path("app/sql") / filename
    if not path.exists():
        raise FileNotFoundError(f"Arquivo {path} não encontrado.")
    with path.open("r", encoding="utf-8") as f:
        return f.read()