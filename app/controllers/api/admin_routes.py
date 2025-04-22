from sanic import Blueprint, Request
from sanic.response import json
from sanic.exceptions import Forbidden

from entities.user import UserRole
from usecases.admin import AdminUseCase
from controllers.api.decorators import admin_required, jwt_protected

bp = Blueprint("Admin", url_prefix="/admin")

@bp.get("/users")
@jwt_protected
@admin_required
async def list_users(request: Request):
    use_case = request.ctx.admin_use_case
    users = await use_case.get_all_users()
    return json([{
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "role": u.role.value
    } for u in users])

@bp.post("/users")
@jwt_protected
@admin_required
async def create_user(request: Request):
    data = request.json
    if not data or "email" not in data or "password" not in data:
        return json({"error": "Missing required fields"}, status=400)
    
    use_case = request.ctx.admin_use_case
    
    try:
        user = await use_case.create_user(
            email=data["email"],
            password=data["password"],
            full_name=data.get("full_name", ""),
            role=UserRole(data.get("role", "user"))
        )
    except ValueError as e:
        return json({"error": str(e)}, status=400)
    
    return json({
        "id": user.id,
        "email": user.email,
        "role": user.role.value
    }, status=201)

@bp.delete("/users/<user_id:int>")
@jwt_protected
@admin_required
async def delete_user(request: Request, user_id: int):
    use_case = request.ctx.admin_use_case
    if not await use_case.delete_user(user_id):
        return json({"error": "User not found"}, status=404)
    
    return json({}, status=204)