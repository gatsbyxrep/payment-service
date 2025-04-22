from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from entities.user import User, UserRole
from db.models import UserDB
from config.config import ConfigLoader
from security.security import get_password_hash

class UserRepository:
    def __init__(self, session: AsyncSession, config: ConfigLoader):
        self.session = session
        self.config = config
        
    async def create(self, email: str, password_hash: str,
                   full_name: str, role: UserRole) -> User:
        db_user = UserDB(
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            role=role
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return User.from_orm(db_user)

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(UserDB).where(UserDB.email == email)
        )
        if db_user := result.scalar_one_or_none():
            return User.from_orm(db_user)
        return None
    
    async def get_all(self) -> list[User]:
        result = await self.session.execute(select(UserDB))
        return [User.from_orm(u) for u in result.scalars()]

    async def delete(self, user_id: int) -> bool:
        user = await self.session.get(UserDB, user_id)
        if not user:
            return False
        await self.session.delete(user)
        await self.session.commit()
        return True