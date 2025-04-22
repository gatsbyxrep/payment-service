from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from config.config import ConfigLoader
from entities.account import Account
from entities.payment import Payment
from db.models import PaymentDB, AccountDB

class AccountRepository:
    def __init__(self, session: AsyncSession, config: ConfigLoader):
        self.session = session
        self.config = config
        
    async def get_by_id(self, account_id: int) -> Optional[Account]:
        result = await self.session.execute(
            select(AccountDB).where(AccountDB.id == account_id)
        )
        if db_account := result.scalar_one_or_none():
            return Account.from_orm(db_account)
        return None

    async def update_balance(self, account_id: int, amount: float) -> None:
        await self.session.execute(
            update(AccountDB)
            .where(AccountDB.id == account_id)
            .values(balance=AccountDB.balance + amount)
        )
        await self.session.commit() 

    async def create(self, user_id: int) -> Account:
        created_at = datetime.now(timezone.utc)
        db_account = AccountDB(
            user_id=user_id,
            balance=0.0,
            created_at=created_at 
        )
        self.session.add(db_account)
        await self.session.commit() 
        await self.session.refresh(db_account) 
        return Account.from_orm(db_account)