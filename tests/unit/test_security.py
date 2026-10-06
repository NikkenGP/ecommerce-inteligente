"""Pruebas unitarias de hashing y JWT."""

import time
from datetime import datetime, timedelta, timezone

import jwt as pyjwt
import pytest

from src.config import get_settings
from src.services.auth.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

pytestmark = pytest.mark.unit


def test_hash_password_generates_distinct_salts():
    h1 = hash_password("Secret123!")
    h2 = hash_password("Secret123!")
    assert h1 != h2
    assert verify_password("Secret123!", h1)
    assert verify_password("Secret123!", h2)


def test_verify_password_rejects_wrong_password():
    hashed = hash_password("Secret123!")
    assert not verify_password("otra-clave", hashed)


def test_access_token_contains_required_claims():
    token = create_access_token("user-1", "Cliente")
    payload = decode_token(token)
    assert payload["sub"] == "user-1"
    assert payload["role"] == "Cliente"
    assert payload["type"] == "access"
    assert {"sub", "role", "exp", "iat", "jti"} <= set(payload)


def test_decode_rejects_wrong_key():
    token = create_access_token("user-1", "Cliente")
    with pytest.raises(pyjwt.PyJWTError):
        pyjwt.decode(token, "clave-incorrecta", algorithms=["HS256"])


def test_decode_rejects_expired_token():
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "user-1",
        "role": "Cliente",
        "type": "access",
        "iat": now - timedelta(hours=2),
        "exp": now - timedelta(hours=1),
        "jti": "x",
    }
    token = pyjwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    with pytest.raises(pyjwt.ExpiredSignatureError):
        decode_token(token)


def test_refresh_token_type():
    token = create_refresh_token("user-1", "Administrador")
    assert decode_token(token)["type"] == "refresh"
