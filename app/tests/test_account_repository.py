import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from datetime import datetime, timezone

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config.config import ConfigLoader
from db.models import AccountDB
from repositories.account_repository import AccountRepository

@pytest_asyncio.fixture(scope="function")
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(AccountDB.metadata.create_all)

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
def account_repo(async_session: AsyncSession):
    config = MagicMock()
    return AccountRepository(async_session, config)

@pytest.mark.asyncio
async def test_create_account(account_repo: AccountRepository):
    account = await account_repo.create(user_id=1)
    assert account.id is not None
    assert account.balance == 0.0

@pytest.mark.asyncio
async def test_update_balance(account_repo: AccountRepository, async_session: AsyncSession):
    account = await account_repo.create(user_id=1)
    
    await account_repo.update_balance(account.id, 100.0)
    
    updated = await account_repo.get_by_id(account.id)
    assert updated.balance == 100.0
    
@pytest.mark.asyncio
async def test_get_by_id_existing(account_repo: AccountRepository, async_session: AsyncSession):
    db_account = AccountDB(user_id=1, balance=100.0, created_at=datetime.now(timezone.utc))
    async_session.add(db_account)
    await async_session.commit()
    await async_session.refresh(db_account) 
    result = await account_repo.get_by_id(db_account.id)

    assert result is not None
    assert result.id == db_account.id
    assert result.user_id == 1
    assert result.balance == 100.0

@pytest.mark.asyncio
async def test_get_by_id_non_existing(account_repo: AccountRepository):
    result = await account_repo.get_by_id(999)
    assert result is None