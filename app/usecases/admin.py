from config.config import ConfigLoader
from entities.user import User, UserRole
from security.security import get_password_hash

class AdminUseCase:
    def __init__(self, user_repo, account_repo, config: ConfigLoader):
        self.user_repo = user_repo
        self.account_repo = account_repo

    async def create_user(self, email: str, password: str, 
                        full_name: str, role: UserRole) -> User:
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise ValueError("User already exists")
        
        hashed_password = get_password_hash(password)
        new_user = await self.user_repo.create(
            email=email,
            password_hash=hashed_password,
            full_name=full_name,
            role=role
        )
     
        await self.account_repo.create(new_user.id)
        
        return new_user

    async def get_all_users(self):
        return await self.user_repo.get_all()

    async def delete_user(self, user_id: int) -> bool:
        return await self.user_repo.delete(user_id)