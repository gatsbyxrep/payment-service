import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from datetime import datetime, timezone
import pytest
from unittest.mock import AsyncMock, MagicMock
from entities.payment import PaymentCreate
from entities.account import Account
from exceptions.exceptions import (
    DuplicateTransactionError,
    AccountNotFoundError,
    PaymentProcessingError
)
from repositories.account_repository import AccountRepository
from repositories.payment_repository import PaymentRepository
from usecases.payments import PaymentUseCase

@pytest.fixture
def mock_payment_repo():
    return AsyncMock()

@pytest.fixture
def mock_account_repo():
    return AsyncMock()

@pytest.fixture
def payment_use_case(mock_payment_repo, mock_account_repo):
    config = MagicMock()
    return PaymentUseCase(payment_repo=mock_payment_repo, account_repo=mock_account_repo, config=config)

@pytest.mark.asyncio
async def test_process_payment_success(payment_use_case, mock_payment_repo, mock_account_repo):
    payment_data = {
        "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
        "user_id": 1,
        "account_id": 101,
        "amount": 100.0
    }
    mock_account = Account(id=101, user_id=1, balance=500.0, created_at=datetime.now(timezone.utc))
    mock_payment = PaymentCreate(
        transaction_id="5eae174f-7cd0-472c-bd36-35660f00132b",
        account_id=101,
        amount=100.0
    )
    created_payment = MagicMock()
    created_payment.id = 201

    mock_payment_repo.exists.return_value = False
    mock_account_repo.get_by_id.return_value = mock_account
    mock_payment_repo.create.return_value = created_payment

    result = await payment_use_case.process_payment(payment_data)

    mock_payment_repo.exists.assert_called_once_with("5eae174f-7cd0-472c-bd36-35660f00132b")
    mock_account_repo.get_by_id.assert_called_once_with(101)
    mock_payment_repo.create.assert_called_once_with(mock_payment)
    mock_account_repo.update_balance.assert_called_once_with(101, 100.0)
    assert result == {"payment_id": 201, "new_balance": 600.0}

@pytest.mark.asyncio
async def test_process_payment_success(payment_use_case, mock_payment_repo, mock_account_repo):
    payment_data = {
        "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
        "user_id": 1,
        "account_id": 101,
        "amount": 100.0
    }
    mock_account = Account(
        id=101,
        user_id=1,
        balance=500.0,
        created_at=datetime.now(timezone.utc)
    )
    mock_payment = PaymentCreate(
        transaction_id="5eae174f-7cd0-472c-bd36-35660f00132b",
        account_id=101,
        amount=100.0
    )
    created_payment = MagicMock()
    created_payment.id = 201

    mock_payment_repo.exists.return_value = False
    mock_account_repo.get_by_id.return_value = mock_account
    mock_payment_repo.create.return_value = created_payment

    result = await payment_use_case.process_payment(payment_data)

    mock_payment_repo.exists.assert_called_once_with("5eae174f-7cd0-472c-bd36-35660f00132b")
    mock_account_repo.get_by_id.assert_called_once_with(101)
    mock_payment_repo.create.assert_called_once_with(mock_payment)
    mock_account_repo.update_balance.assert_called_once_with(101, 100.0)
    assert result == {"payment_id": 201, "new_balance": 600.0}

@pytest.mark.asyncio
async def test_process_payment_account_not_found(payment_use_case, mock_payment_repo, mock_account_repo):
    payment_data = {
        "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
        "user_id": 1,
        "account_id": 101,
        "amount": 100.0
    }

    mock_payment_repo.exists.return_value = False
    mock_account_repo.get_by_id.return_value = None  # Simulate no account found

    with pytest.raises(PaymentProcessingError) as exc_info:
        await payment_use_case.process_payment(payment_data)

    assert str(exc_info.value) == "Account not found or doesn't belong to user"  # Check the exception message
    mock_payment_repo.exists.assert_called_once_with("5eae174f-7cd0-472c-bd36-35660f00132b")
    mock_account_repo.get_by_id.assert_called_once_with(101)

@pytest.mark.asyncio
async def test_process_payment_create_new_account(payment_use_case, mock_payment_repo, mock_account_repo):
    payment_data = {
        "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
        "user_id": 1,
        "account_id": None,
        "amount": 100.0
    }
    new_account = Account(id=102, user_id=1, balance=0.0, created_at=datetime.now(timezone.utc))
    mock_payment = PaymentCreate(
        transaction_id="5eae174f-7cd0-472c-bd36-35660f00132b",
        account_id=102,
        amount=100.0
    )
    created_payment = MagicMock()
    created_payment.id = 202

    mock_payment_repo.exists.return_value = False
    mock_account_repo.create.return_value = new_account
    mock_payment_repo.create.return_value = created_payment

    result = await payment_use_case.process_payment(payment_data)

    mock_payment_repo.exists.assert_called_once_with("5eae174f-7cd0-472c-bd36-35660f00132b")
    mock_account_repo.create.assert_called_once_with(1)
    mock_payment_repo.create.assert_called_once_with(mock_payment)
    mock_account_repo.update_balance.assert_called_once_with(102, 100.0)
    assert result == {"payment_id": 202, "new_balance": 100.0}

@pytest.mark.asyncio
async def test_get_or_create_account_existing_account(payment_use_case, mock_account_repo):
    user_id = 1
    account_id = 101
    mock_account = Account(id=101, user_id=1, balance=500.0, created_at=datetime.now(timezone.utc))

    mock_account_repo.get_by_id.return_value = mock_account

    account = await payment_use_case._get_or_create_account(user_id, account_id)

    mock_account_repo.get_by_id.assert_called_once_with(101)
    assert account == mock_account

@pytest.mark.asyncio
async def test_get_or_create_account_non_matching_user(payment_use_case, mock_account_repo):
    user_id = 1
    account_id = 101
    mock_account = Account(id=101, user_id=2, balance=500.0, created_at=datetime.now(timezone.utc))

    mock_account_repo.get_by_id.return_value = mock_account

    with pytest.raises(AccountNotFoundError):
        await payment_use_case._get_or_create_account(user_id, account_id)

    mock_account_repo.get_by_id.assert_called_once_with(101)

@pytest.mark.asyncio
async def test_get_or_create_account_create_new_account(payment_use_case, mock_account_repo):
    user_id = 1
    account_id = None
    new_account = Account(id=102, user_id=1, balance=0.0, created_at=datetime.now(timezone.utc))

    mock_account_repo.create.return_value = new_account

    account = await payment_use_case._get_or_create_account(user_id, account_id)

    mock_account_repo.create.assert_called_once_with(1)
    assert account == new_account