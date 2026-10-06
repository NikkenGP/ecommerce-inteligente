"""Dependencias FastAPI para autenticación y autorización por rol."""

from __future__ import annotations

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.services.auth.security import decode_token
from src.services.auth.store import get_token_store

bearer_scheme = HTTPBearer(auto_error=True)


def _is_revoked(jti: str) -> bool:
    return get_token_store().get(f"blacklist:{jti}") is not None


def revoke_token(jti: str, exp_ts: float | None = None) -> None:
    """Marca un token como revocado en la lista negra hasta su expiración."""
    ttl = 3600
    if exp_ts is not None:
        import time

        ttl = max(int(exp_ts - time.time()), 1)
    get_token_store().set(f"blacklist:{jti}", "1", ttl)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado")
    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tipo de token inválido")
    if _is_revoked(payload.get("jti", "")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revocado")
    return payload


def require_role(*roles: str):
    """Devuelve una dependencia que exige uno de los roles indicados."""

    def checker(user: dict = Depends(get_current_user)) -> dict:
        if user.get("role") not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes")
        return user

    return checker
