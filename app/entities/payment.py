from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel

@dataclass
class Payment:
    id: int
    transaction_id: str
    account_id: int
    amount: float
    created_at: datetime

    @classmethod
    def from_orm(cls, orm_obj: Any):
        return Payment(
            id=orm_obj.id,
            transaction_id=orm_obj.transaction_id,
            account_id=orm_obj.account_id,
            amount=float(orm_obj.amount),
            created_at=orm_obj.created_at
        )

class PaymentCreate(BaseModel):
    transaction_id: str
    account_id: int
    amount: float

class PaymentResponse(BaseModel):
    id: int
    transaction_id: str
    account_id: int
    amount: float
    created_at: datetime
