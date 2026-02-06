from typing import Optional
from pydantic import BaseModel, EmailStr


class User(BaseModel):
    """Domain entity representing a User."""
    nome: str
    email: EmailStr
    tipo: str  # enum? 'admin', 'user'
    token: Optional[str] = None
    
    # Can add more fields as needed based on database schema
