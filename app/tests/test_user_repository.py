import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from datetime import datetime, timezone
import pytest
import pytest_asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config.config import ConfigLoader
from db.models import UserDB
from repositories.user_repository import UserRepository
from entities.user import UserRole
from security.security import get_password_hash

@pytest_asyncio.fixture(scope="function")
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(UserDB.metadata.create_all)
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        class_=AsyncSession
    )
    session = TestingSessionLocal()
    yield session
    await session.close()
    await engine.dispose()

@pytest.fixture
def user_repo(async_session: AsyncSession):
    config_path: str = "app/config/config.yml"
    config = ConfigLoader(config_path)
    return UserRepository(async_session, config)

@pytest.mark.asyncio
async def test_create_user(user_repo: UserRepository):
    email = "test@example.com"
    password_hash = get_password_hash("password123")
    full_name = "Test User"
    role = UserRole.USER

    user = await user_repo.create(email=email, password_hash=password_hash, full_name=full_name, role=role)
    
    assert user.id is not None
    assert user.email == email
    assert user.password_hash == password_hash
    assert user.full_name == full_name
    assert user.role == role

@pytest.mark.asyncio
async def test_get_all_users(user_repo: UserRepository, async_session: AsyncSession):
    user1 = UserDB(email="user1@example.com", password_hash="hash1", full_name="User One", role=UserRole.USER)
    user2 = UserDB(email="user2@example.com", password_hash="hash2", full_name="User Two", role=UserRole.ADMIN)
    async_session.add_all([user1, user2])
    await async_session.commit()

    users = await user_repo.get_all()

    assert len(users) == 2
    assert users[0].email == "user1@example.com"
    assert users[1].email == "user2@example.com"

@pytest.mark.asyncio
async def test_delete_existing_user(user_repo: UserRepository, async_session: AsyncSession):
    db_user = UserDB(email="user@example.com", password_hash="hash", full_name="Test User", role=UserRole.USER)
    async_session.add(db_user)
    await async_session.commit()
    await async_session.refresh(db_user)

    deleted = await user_repo.delete(db_user.id)

    assert deleted is True

    result = await async_session.execute(select(UserDB).where(UserDB.id == db_user.id))
    assert result.scalars().first() is None

@pytest.mark.asyncio
async def test_delete_non_existing_user(user_repo: UserRepository):
    deleted = await user_repo.delete(999)

    assert deleted is False