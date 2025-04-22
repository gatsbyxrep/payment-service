import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from datetime import datetime, timezone

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config.config import ConfigLoader
from db.models import PaymentDB
from repositories.payment_repository import PaymentRepository
from repositories.account_repository import AccountRepository
from repositories.user_repository import UserRepository
from entities.payment import PaymentCreate

@pytest_asyncio.fixture(scope="function")
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(PaymentDB.metadata.create_all)
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
    config_path: str = "app/config/config.yml"
    config = ConfigLoader(config_path)
    return AccountRepository(async_session, config)

@pytest.fixture
def payment_repo(async_session: AsyncSession):
    config_path: str = "app/config/config.yml"
    config = ConfigLoader(config_path)
    return PaymentRepository(async_session, config)

@pytest.fixture
def user_repo(async_session: AsyncSession):
    config_path: str = "app/config/config.yml"
    config = ConfigLoader(config_path)
    return UserRepository(async_session, config)

@pytest.mark.asyncio
async def test_create_payment(payment_repo: PaymentRepository, async_session: AsyncSession):
    payment_data = PaymentCreate(
        transaction_id="txn_12345",
        account_id=1,
        amount=100.0
    )

    payment = await payment_repo.create(payment_data)

    assert payment.id is not None
    assert payment.transaction_id == "txn_12345"
    assert payment.account_id == 1
    assert payment.amount == 100.0
    assert isinstance(payment.created_at, datetime)

@pytest.mark.asyncio
async def test_exists_payment_by_transaction_id(payment_repo: PaymentRepository, async_session: AsyncSession):
    db_payment = PaymentDB(
        transaction_id="txn_12345",
        account_id=1,
        amount=100.0,
        created_at=datetime.now(timezone.utc)
    )
    async_session.add(db_payment)
    await async_session.commit()
    await async_session.refresh(db_payment)

    exists_result = await payment_repo.exists("txn_12345")

    assert exists_result is True

@pytest.mark.asyncio
async def test_exists_payment_by_non_existing_transaction_id(payment_repo: PaymentRepository):
    exists_result = await payment_repo.exists("non_existing_txn")

    assert exists_result is False

@pytest.mark.asyncio
async def test_get_payment_by_id_existing(payment_repo: PaymentRepository, async_session: AsyncSession):
    db_payment = PaymentDB(
        transaction_id="txn_12345",
        account_id=1,
        amount=100.0,
        created_at=datetime.now(timezone.utc)
    )
    async_session.add(db_payment)
    await async_session.commit()
    await async_session.refresh(db_payment)

    payment = await payment_repo.get_by_id(db_payment.id)

    assert payment is not None
    assert payment.id == db_payment.id
    assert payment.transaction_id == "txn_12345"
    assert payment.account_id == 1
    assert payment.amount == 100.0

@pytest.mark.asyncio
async def test_get_payment_by_id_non_existing(payment_repo: PaymentRepository):
    payment = await payment_repo.get_by_id(999)

    assert payment is None