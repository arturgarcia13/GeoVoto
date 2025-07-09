# json_user_store.py
import json
from pathlib import Path

USERS_PATH = Path("app/data/usuarios.json")

def get_user_by_email(email):
    with open(USERS_PATH, "r", encoding="utf-8") as f:
        users = json.load(f)
    return next((u for u in users if u["email"] == email), None)

def update_user_token(email, token):
    with open(USERS_PATH, "r", encoding="utf-8") as f:
        users = json.load(f)
    for u in users:
        if u["email"] == email:
            u["token"] = token
            break
    with open(USERS_PATH, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

def validate_token(token):
    # print(f"[DEBUG] Token recebido para validação: {token}")
    with open(USERS_PATH, "r", encoding="utf-8") as f:
        users = json.load(f)
        for u in users:
            # print(f"[DEBUG] Usuário {u['email']} → token: {u.get('token')}")
            if token == u.get('token'):
                return u
