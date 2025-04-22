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
    
    session = async_session_factory()
    
    app.ctx.db_session = session

    @app.middleware("request")
    async def inject_dependencies(request):
        request.ctx.user_repo = UserRepository(app.ctx.db_session, config)
        request.ctx.account_repo = AccountRepository(app.ctx.db_session, config)
        request.ctx.payment_repo = PaymentRepository(app.ctx.db_session, config)
        request.ctx.admin_use_case = AdminUseCase(user_repo=request.ctx.user_repo, account_repo=request.ctx.account_repo, config=config)
        request.ctx.auth_use_case = AuthUseCase(user_repo=request.ctx.user_repo, config=config)
        request.ctx.payment_use_case = PaymentUseCase(payment_repo=request.ctx.payment_repo, account_repo=request.ctx.account_repo, config=config)
    
    app.blueprint(auth_routes.bp)
    app.blueprint(admin_routes.bp)
    app.blueprint(payment_routes.bp)

    @app.middleware("response")
    async def close_session(request, response):
        if hasattr(request.ctx, "db_session"):
            await request.ctx.db_session.close()
    
    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, auto_reload=True)