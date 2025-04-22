import hashlib
import jwt
from jwt import PyJWTError as JWTError
from datetime import datetime, timedelta, timezone
import bcrypt
from typing import Union

def get_password_hash(password: Union[str, bytes]) -> str:
    if isinstance(password, str):
        password = password.encode("utf-8")
    return bcrypt.hashpw(password, bcrypt.gensalt()).decode("utf-8")

def verify_password(
    plain_password: Union[str, bytes],
    hashed_password: Union[str, bytes]
) -> bool:
    try:
        if isinstance(plain_password, str):
            plain_password = plain_password.encode("utf-8")
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode("utf-8")
        return bcrypt.checkpw(plain_password, hashed_password)
    except (ValueError, UnicodeEncodeError) as e:
        return False

def validate_webhook_signature(data: dict, secret_key: str, received_signature: str) -> bool:
    ordered_data = sorted(data.items(), key=lambda x: x[0])
    signature_str = "".join(str(v) for k, v in ordered_data if k != "signature") + secret_key
    calculated = hashlib.sha256(signature_str.encode()).hexdigest()
    return calculated == received_signature

def create_access_token(data: dict, secret_key: str, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm="HS256")