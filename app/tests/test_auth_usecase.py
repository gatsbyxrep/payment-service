import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from datetime import datetime, timedelta, timezone
import hashlib
import bcrypt
import jwt
import pytest
from unittest.mock import patch
from security.security import (
    get_password_hash,
    verify_password,
    validate_webhook_signature,
    create_access_token,
    JWTError,
)

@pytest.mark.asyncio
async def test_get_password_hash():
    password = "password123"
    hashed_password = get_password_hash(password)
    assert hashed_password != password
    assert bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

@pytest.mark.asyncio
async def test_verify_password_success():
    password = "password123"
    hashed_password = get_password_hash(password)
    # Verify the password matches the hash
    assert verify_password(password, hashed_password) is True

@pytest.mark.asyncio
async def test_verify_password_failure():
    password = "password123"
    incorrect_password = "wrongpassword"
    hashed_password = get_password_hash(password)
    assert verify_password(incorrect_password, hashed_password) is False

@pytest.mark.asyncio
async def test_validate_webhook_signature_success():
    secret_key = "secret123"
    data = {"amount": 100, "currency": "USD", "timestamp": "2023-10-01T12:00:00Z"}
    signature_str = "".join(str(v) for k, v in sorted(data.items()) if k != "signature") + secret_key
    received_signature = hashlib.sha256(signature_str.encode()).hexdigest()
    assert validate_webhook_signature(data, secret_key, received_signature) is True

@pytest.mark.asyncio
async def test_validate_webhook_signature_failure():
    secret_key = "secret123"
    data = {"amount": 100, "currency": "USD", "timestamp": "2023-10-01T12:00:00Z"}
    signature_str = "".join(str(v) for k, v in sorted(data.items()) if k != "signature") + secret_key
    received_signature = hashlib.sha256(signature_str.encode()).hexdigest()
    altered_data = {"amount": 200, "currency": "USD", "timestamp": "2023-10-01T12:00:00Z"}
    assert validate_webhook_signature(altered_data, secret_key, received_signature) is False

@pytest.mark.asyncio
async def test_create_access_token():
    secret_key = "secret123"
    data = {"sub": "user123", "role": "admin"}
    expires_delta = timedelta(minutes=30)
    token = create_access_token(data, secret_key, expires_delta)
    try:
        decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
        assert decoded["sub"] == data["sub"]
        assert decoded["role"] == data["role"]
        assert "exp" in decoded
    except JWTError:
        pytest.fail("Failed to decode the access token")

@pytest.mark.asyncio
async def test_create_access_token_with_invalid_secret_key():
    secret_key = "secret123"
    invalid_secret_key = "invalid123"
    data = {"sub": "user123", "role": "admin"}
    expires_delta = timedelta(minutes=30)
    token = create_access_token(data, secret_key, expires_delta)
    with pytest.raises(JWTError):
        jwt.decode(token, invalid_secret_key, algorithms=["HS256"])

@pytest.mark.asyncio
async def test_create_access_token_with_expired_token():
    secret_key = "secret123"
    data = {"sub": "user123", "role": "admin"}
    expires_delta = timedelta(minutes=-10)
    token = create_access_token(data, secret_key, expires_delta)
    with pytest.raises(JWTError):
        jwt.decode(token, secret_key, algorithms=["HS256"], options={"verify_exp": True})