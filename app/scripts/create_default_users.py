import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func
import asyncio

from config.config import ConfigLoader
from db.models import UserDB
from security.security import get_password_hash
from entities.user import UserRole

from repositories.account_repository import AccountRepository
from repositories.user_repository import UserRepository
from repositories.payment_repository import PaymentRepository

async def main():
    config_path: str = "config/config.yml"
    config = ConfigLoader(config_path)

    db_url = (
        f"postgresql+asyncpg://{config.get('database.user')}:"
        f"{config.get('database.password')}@"
        f"{config.get('database.host')}:{config.get('database.port')}/"
        f"{config.get('database.name')}"
    )
    engine = create_async_engine(db_url)

    session_factory = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )

    async with session_factory() as session:
        user_repo = UserRepository(session, config)
        account_repo = AccountRepository(session, config)

        result = await session.execute(select(func.count()).select_from(UserDB))
        users_count = result.scalar_one()

        if users_count == 0:
            adminMail = config.get('default_users.admin.email')
            adminPassHash = get_password_hash(
                config.get('default_users.admin.password') 
            )
            adminName = config.get('default_users.admin.full_name')
            await user_repo.create(adminMail, adminPassHash, adminName, UserRole.ADMIN.value)

            userMail = config.get('default_users.user.email')
            userPassHash = get_password_hash(
                config.get('default_users.user.password') 
            )
            userName = config.get('default_users.user.full_name')
            await user_repo.create(userMail, userPassHash, userName, UserRole.USER.value)
            
            await account_repo.create(user_id=2) 
            await account_repo.update_balance(1, 100.0) 


if __name__ == "__main__":
    asyncio.run(main())