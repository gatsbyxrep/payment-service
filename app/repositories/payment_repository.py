from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from config.config import ConfigLoader
from entities.payment import Payment, PaymentCreate
from db.models import PaymentDB

class PaymentRepository:
    def __init__(self, session: AsyncSession, config: ConfigLoader):
        self.session = session
        self.config = config
        
    async def exists(self, transaction_id: str) -> bool:
        result = await self.session.execute(
            select(exists().where(PaymentDB.transaction_id == transaction_id))
        )
        return result.scalar()
    
    async def create(self, payment: PaymentCreate) -> Payment:
        db_payment = PaymentDB(
            transaction_id=payment.transaction_id,
            account_id=payment.account_id,
            amount=payment.amount,
            created_at=datetime.now(timezone.utc)
        )
        self.session.add(db_payment)
        await self.session.commit() 
        await self.session.refresh(db_payment) 
        return Payment.from_orm(db_payment)
    
    async def get_by_id(self, payment_id: int) -> Optional[Payment]:
        result = await self.session.execute(
            select(PaymentDB).where(PaymentDB.id == payment_id)
        )
        if db_payment := result.scalar_one_or_none():
            return Payment.from_orm(db_payment)
        return None
