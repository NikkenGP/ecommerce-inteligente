"""Seguridad: hashing de contraseñas y emisión/verificación de JWT."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from src.config import get_settings


def hash_password(password: str) -> str:
    """Hashea una contraseña con bcrypt (cost factor >= 12)."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verifica una contraseña contra su hash bcrypt."""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def _create_token(subject: str, role: str, token_type: str, expires_delta: timedelta) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "role": role,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: str, role: str) -> str:
    return _create_token(user_id, role, "access", timedelta(minutes=get_settings().access_token_expire_minutes))


def create_refresh_token(user_id: str, role: str) -> str:
    return _create_token(user_id, role, "refresh", timedelta(days=get_settings().refresh_token_expire_days))


def decode_token(token: str) -> dict:
    """Decodifica y valida firma/expiración. Lanza jwt.PyJWTError si es inválido."""
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
