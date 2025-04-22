from datetime import timedelta

from config.config import ConfigLoader
from entities.user import User
from security.security import verify_password, create_access_token

class AuthUseCase:
    def __init__(self, user_repo, config: ConfigLoader):
        self.user_repo = user_repo
        self.config = config

    async def authenticate(self, email: str, password: str) -> tuple[User | None, str | None]:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            return None, "Invalid credentials"
        
        access_token = create_access_token(
            data={"sub": user.email},
            secret_key=self.config.get("jwt.secret"),
            expires_delta=timedelta(minutes=self.config.get("jwt.expire_minutes", 30))
        )
        return user, access_token