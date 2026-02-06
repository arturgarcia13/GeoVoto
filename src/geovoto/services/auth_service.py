from typing import Optional, Dict

from geovoto.infrastructure.database.user_repository import UserRepository
import logging

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, user_repository: Optional[UserRepository] = None):
        self.user_repository = user_repository or UserRepository()

    def validate_token(self, token: str) -> Optional[Dict]:
        """Validates the login token."""
        if not token or len(token) < 20: # Basic validation rule from original code
            logger.warning("Attempted to validate malformed token")
            return None
            
        return self.user_repository.validate_token(token)

    def is_admin(self, user_data: Dict) -> bool:
        """Checks if the user data corresponds to an admin."""
        return user_data.get("tipo") == "admin"
        
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        return self.user_repository.get_by_email(email)
