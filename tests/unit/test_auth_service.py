import pytest
from unittest.mock import MagicMock
from geovoto.services.auth_service import AuthService
from geovoto.infrastructure.database.user_repository import UserRepository

@pytest.fixture
def mock_user_repo():
    return MagicMock(spec=UserRepository)

@pytest.fixture
def auth_service(mock_user_repo):
    return AuthService(user_repository=mock_user_repo)

def test_validate_token_success(auth_service, mock_user_repo):
    token = "valid-token-12345678901234567890" # > 20 chars
    mock_user_repo.validate_token.return_value = {"nome": "Test User", "email": "test@example.com"}
    
    result = auth_service.validate_token(token)
    
    assert result is not None
    assert result["email"] == "test@example.com"
    mock_user_repo.validate_token.assert_called_once_with(token)

def test_validate_token_short(auth_service, mock_user_repo):
    token = "short"
    result = auth_service.validate_token(token)
    assert result is None
    mock_user_repo.validate_token.assert_not_called()

def test_is_admin(auth_service):
    assert auth_service.is_admin({"tipo": "admin"}) is True
    assert auth_service.is_admin({"tipo": "user"}) is False
