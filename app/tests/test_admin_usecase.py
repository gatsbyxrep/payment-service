import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import bcrypt
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from entities.user import User, UserRole
from security.security import get_password_hash
from config.config import ConfigLoader
from usecases.admin import AdminUseCase

@pytest.fixture
def mock_user_repo():
    return AsyncMock()

@pytest.fixture
def mock_account_repo():
    return AsyncMock()

@pytest.fixture
def admin_use_case(mock_user_repo, mock_account_repo):
    config = MagicMock()
    return AdminUseCase(user_repo=mock_user_repo, account_repo=mock_account_repo, config=config)

@pytest.mark.asyncio
async def test_create_user_success(admin_use_case, mock_user_repo, mock_account_repo):
    email = "test@example.com"
    password = "password123"
    full_name = "Test User"
    role = UserRole.USER
    mock_password_hash = "mocked_password_hash"

    with patch("usecases.admin.get_password_hash", return_value=mock_password_hash):
        mock_user_repo.get_by_email.return_value = None
        mock_user_repo.create.return_value = User(
            id=1,
            email=email,
            password_hash=mock_password_hash,
            full_name=full_name,
            role=role
        )

        result = await admin_use_case.create_user(email, password, full_name, role)

        assert result.email == email
        assert result.full_name == full_name
        assert result.role == role
        assert result.password_hash == mock_password_hash

        mock_user_repo.get_by_email.assert_called_once_with(email)
        mock_user_repo.create.assert_called_once_with(
            email=email,
            password_hash=mock_password_hash,
            full_name=full_name,
            role=role
        )
        mock_account_repo.create.assert_called_once_with(1)

    real_password_hash = get_password_hash(password)
    assert bcrypt.checkpw(password.encode("utf-8"), real_password_hash.encode("utf-8"))

@pytest.mark.asyncio
async def test_create_user_already_exists(admin_use_case, mock_user_repo):
    email = "existing@example.com"
    password = "password123"
    full_name = "Existing User"
    role = UserRole.USER

    existing_user = User(id=1, email=email, password_hash=get_password_hash(password), full_name=full_name, role=role)
    mock_user_repo.get_by_email.return_value = existing_user

    with pytest.raises(ValueError, match="User already exists"):
        await admin_use_case.create_user(email, password, full_name, role)

    mock_user_repo.get_by_email.assert_called_once_with(email)
    mock_user_repo.create.assert_not_called()

@pytest.mark.asyncio
async def test_get_all_users(admin_use_case, mock_user_repo):
    users = [
        User(id=1, email="user1@example.com", password_hash="test_hash_1", full_name="User One", role=UserRole.USER),
        User(id=2, email="user2@example.com", password_hash="test_hash_2", full_name="User Two", role=UserRole.ADMIN)
    ]
    mock_user_repo.get_all.return_value = users

    result = await admin_use_case.get_all_users()

    assert result == users
    mock_user_repo.get_all.assert_called_once()

@pytest.mark.asyncio
async def test_delete_user_success(admin_use_case, mock_user_repo):
    user_id = 1
    mock_user_repo.delete.return_value = True

    result = await admin_use_case.delete_user(user_id)

    assert result is True
    mock_user_repo.delete.assert_called_once_with(user_id)

@pytest.mark.asyncio
async def test_delete_user_failure(admin_use_case, mock_user_repo):
    user_id = 1
    mock_user_repo.delete.return_value = False

    result = await admin_use_case.delete_user(user_id)

    assert result is False
    mock_user_repo.delete.assert_called_once_with(user_id)