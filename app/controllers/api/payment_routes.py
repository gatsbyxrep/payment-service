from sanic import Blueprint, Request
from sanic.response import json

from security.security import validate_webhook_signature
from usecases.payments import PaymentUseCase

bp = Blueprint("Payments", url_prefix="/payments")

@bp.post("/webhook")
async def webhook(request: Request):
    config = request.config
    data = request.json

    if not validate_webhook_signature(
        data=data,
        secret_key=config.get("secret_key"),
        received_signature=data.get("signature")
    ):
        return json({"error": "Invalid signature"}, status=403)

    use_case = request.ctx.payment_use_case
    
    try:
        result = await use_case.process_payment(data)
    except ValueError as e:
        return json({"error": str(e)}, status=400)
    
    return json(result.dict(), status=201)