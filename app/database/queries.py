# app/database/queries.py

from sqlalchemy import text
from app.database.connection import get_engine
from pathlib import Path


def get_user_by_email(email):
    engine = get_engine()
    query = text("SELECT * FROM usuarios WHERE email = :email")
    with engine.connect() as conn:
        result = conn.execute(query, {"email": email}).mappings().fetchone()
    return result

def update_user_token(email, token):
    engine = get_engine()
    query = text("UPDATE usuarios SET token = :token WHERE email = :email")
    with engine.connect() as conn:
        conn.execute(query, {"token": token, "email": email})
        conn.commit()

def validate_token(token):
    engine = get_engine()
    query = text("SELECT * FROM usuarios WHERE token = :token")
    with engine.connect() as conn:
        result = conn.execute(query, {"token": token}).mappings().fetchone()
    return result

def read_sql_file(filename):
    path = Path("app/sql") / filename
    with open(path, "r", encoding="utf-8") as f:
        return f.read()