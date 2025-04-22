from functools import wraps
import jwt
from jwt import PyJWTError as JWTError
from sanic import Request
from sanic.exceptions import Unauthorized, Forbidden

def jwt_protected(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise Unauthorized("Missing authorization token")
        
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(
                token,
                request.app.config.get("jwt.secret"),
                algorithms=["HS256"]
            )
            user = await request.ctx.user_repo.get_by_email(payload["sub"])
            if not user:
                raise Unauthorized("Invalid token")
            request.ctx.current_user = user
        except JWTError:
            raise Unauthorized("Invalid token")
        
        return await func(request, *args, **kwargs)
    return wrapper

def admin_required(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        if request.ctx.current_user.role != "admin":
            raise Forbidden("Admin access required")
        return await func(request, *args, **kwargs)
    return wrapper