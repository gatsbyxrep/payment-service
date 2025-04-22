from dataclasses import dataclass
from enum import Enum
from typing import Any

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

@dataclass
class User:
    id: int
    email: str
    password_hash: str
    full_name: str
    role: UserRole
    is_active: bool = True
    
    @classmethod
    def from_orm(cls, orm_obj: Any) -> "User":
        return User(
            id=orm_obj.id,
            email=orm_obj.email,
            password_hash=orm_obj.password_hash,
            full_name=orm_obj.full_name,
            role=UserRole(orm_obj.role),
            is_active=orm_obj.is_active or True 
        )
    