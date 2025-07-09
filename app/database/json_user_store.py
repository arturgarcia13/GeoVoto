# app/database/json_user_store.py

import json
from pathlib import Path

USERS_PATH = Path("app/data/usuarios.json")

def _load_users():
    with open(USERS_PATH, "r") as f:
        return json.load(f)

def _save_users(users):
    with open(USERS_PATH, "w") as f:
        json.dump(users, f, indent=2)

def get_user_by_email(email):
    users = _load_users()
    return next((u for u in users if u["email"] == email), None)

def update_user_token(email, token):
    users = _load_users()
    for user in users:
        if user["email"] == email:
            user["token"] = token
            break
    _save_users(users)

def validate_token(token):
    users = _load_users()
    return next((u for u in users if u["token"] == token), None)