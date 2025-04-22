from sanic import Blueprint, Request
from sanic.response import json
from sanic.exceptions import Unauthorized

from usecases.auth import AuthUseCase
from controllers.api.decorators import jwt_protected

bp = Blueprint("Auth", url_prefix="/auth")

@bp.post("/login")
async def login(request: Request):
    data = request.json
    if not data or "email" not in data or "password" not in data:
        return json({"error": "Invalid credentials"}, status=400)
 
    use_case = request.ctx.auth_use_case
    
    user, token = await use_case.authenticate(data["email"], data["password"])
    if not user:
        return json({"error": "Invalid email or password"}, status=401)
    
    return json({
        "user_id": user.id,
        "email": user.email,
        "access_token": token
    })

@bp.get("/me")
@jwt_protected
async def get_me(request: Request):
    user = request.ctx.current_user
    return json({
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name
    })