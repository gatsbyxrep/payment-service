from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from config.config import ConfigLoader
from entities.payment import PaymentCreate
from entities.account import Account
from repositories.payment_repository import PaymentRepository
from repositories.account_repository import AccountRepository
from exceptions.exceptions import (
    DuplicateTransactionError,
    AccountNotFoundError,
    PaymentProcessingError
)

class PaymentUseCase:
    def __init__(
        self,
        payment_repo: PaymentRepository,
        account_repo: AccountRepository,
        config: ConfigLoader
    ):
        self.payment_repo = payment_repo
        self.account_repo = account_repo

    async def process_payment(self, payment_data: dict) -> dict:
        transaction_id = payment_data["transaction_id"]     
        try:
            if await self.payment_repo.exists(transaction_id):
                raise DuplicateTransactionError()

            account = await self._get_or_create_account(
                payment_data["user_id"],
                payment_data["account_id"]
            )
                
            payment = PaymentCreate(
                transaction_id=transaction_id,
                account_id=account.id,
                amount=payment_data["amount"]
            )
            created_payment = await self.payment_repo.create(payment)

            await self.account_repo.update_balance(
                account.id,
                payment.amount
            )

            return {
                "payment_id": created_payment.id,
                "new_balance": account.balance + payment.amount
            }
        
        except Exception as e:
            raise PaymentProcessingError(str(e))

    async def _get_or_create_account(
        self,
        user_id: int,
        account_id: Optional[int] = None
    ) -> Account:
        if account_id:
            account = await self.account_repo.get_by_id(account_id)
            if not account or account.user_id != user_id:
                raise AccountNotFoundError()
            return account

        return await self.account_repo.create(user_id)