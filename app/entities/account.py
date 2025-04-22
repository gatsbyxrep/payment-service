from dataclasses import dataclass
from datetime import datetime
from typing import Any

@dataclass
class Account:
    id: int
    user_id: int
    balance: float
    created_at: datetime
    
    @classmethod
    def from_orm(cls, orm_obj: Any):
        return Account(
            id=orm_obj.id,
            user_id=orm_obj.user_id,
            balance=orm_obj.balance,
            created_at=orm_obj.created_at
        )