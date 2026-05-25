from sanic import Sanic
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config.config import ConfigLoader
from db.models import UserDB, Base
from controllers.api import auth_routes, admin_routes, payment_routes
from usecases.admin import AdminUseCase
from usecases.payments import PaymentUseCase
from usecases.auth import AuthUseCase
from repositories.account_repository import AccountRepository
from repositories.user_repository import UserRepository
from repositories.payment_repository import PaymentRepository

from types import SimpleNamespace

class RequestContext(SimpleNamespace):
    def __init__(self, app, config, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.config = config
        self._db_session = None
        self._user_repo = None
        self._account_repo = None
        self._payment_repo = None
        self._admin_use_case = None
        self._auth_use_case = None
        self._payment_use_case = None

    @property
    def db_session(self) -> AsyncSession:
        if self._db_session is None:
            self._db_session = self.app.ctx.async_session_factory()
        return self._db_session

    @property
    def user_repo(self) -> UserRepository:
        if self._user_repo is None:
            self._user_repo = UserRepository(self.db_session, self.config)
        return self._user_repo

    @property
    def account_repo(self) -> AccountRepository:
        if self._account_repo is None:
            self._account_repo = AccountRepository(self.db_session, self.config)
        return self._account_repo

    @property
    def payment_repo(self) -> PaymentRepository:
        if self._payment_repo is None:
            self._payment_repo = PaymentRepository(self.db_session, self.config)
        return self._payment_repo

    @property
    def admin_use_case(self) -> AdminUseCase:
        if self._admin_use_case is None:
            self._admin_use_case = AdminUseCase(
                user_repo=self.user_repo,
                account_repo=self.account_repo,
                config=self.config
            )
        return self._admin_use_case

    @property
    def auth_use_case(self) -> AuthUseCase:
        if self._auth_use_case is None:
            self._auth_use_case = AuthUseCase(
                user_repo=self.user_repo,
                config=self.config
            )
        return self._auth_use_case

    @property
    def payment_use_case(self) -> PaymentUseCase:
        if self._payment_use_case is None:
            self._payment_use_case = PaymentUseCase(
                payment_repo=self.payment_repo,
                account_repo=self.account_repo,
                config=self.config
            )
        return self._payment_use_case

    async def close(self):
        if self._db_session is not None:
            await self._db_session.close()

def create_app(config_path: str = "config/config.yml") -> Sanic:
    app = Sanic(__name__)
    config = ConfigLoader(config_path)

    db_url = (
        f"postgresql+asyncpg://{config.get('database.user')}:"
        f"{config.get('database.password')}@"
        f"{config.get('database.host')}:{config.get('database.port')}/"
        f"{config.get('database.name')}"
    )
    engine = create_async_engine(db_url)

    async_session_factory = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )
    
    app.ctx.async_session_factory = async_session_factory

    @app.middleware("request")
    async def inject_dependencies(request):
        request.ctx = RequestContext(app, config)
    
    app.blueprint(auth_routes.bp)
    app.blueprint(admin_routes.bp)
    app.blueprint(payment_routes.bp)

    @app.middleware("response")
    async def close_session(request, response):
        if hasattr(request.ctx, "close") and callable(request.ctx.close):
            await request.ctx.close()
    
    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, auto_reload=True)