"""Rutas de autenticación: register, login, refresh y logout."""

from __future__ import annotations

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.user import User
from src.schemas.auth import LoginRequest, RefreshRequest, TokenResponse, UserCreate, UserResponse
from src.services.auth import rate_limit
from src.services.auth.dependencies import bearer_scheme, get_current_user, revoke_token
from src.services.auth.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from src.services.auth.store import get_token_store

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


@router.post("/register", response_model=UserResponse, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=409, detail="El email ya está registrado")
    user = User(email=payload.email, hashed_password=hash_password(payload.password), role="Cliente")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    ip = _client_ip(request)
    if rate_limit.is_rate_limited(ip):
        raise HTTPException(status_code=429, detail="Demasiados intentos. Intente más tarde.")
    user = db.query(User).filter(User.email == payload.email).first()
    # Respuesta 401 genérica para no revelar si el email existe (CL-01)
    if not user or not verify_password(payload.password, user.hashed_password):
        rate_limit.register_failed_attempt(ip)
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    access = create_access_token(user.id, user.role)
    refresh = create_refresh_token(user.id, user.role)
    # Registrar refresh token vigente para rotación/detección de reuso
    refresh_payload = decode_token(refresh)
    get_token_store().add_to_set(f"refresh:{user.id}", refresh_payload["jti"])
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest):
    try:
        token_payload = decode_token(payload.refresh_token)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Refresh token inválido o expirado")
    if token_payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Tipo de token inválido")

    store = get_token_store()
    jti = token_payload.get("jti", "")
    user_id = token_payload.get("sub", "")
    if store.get(f"blacklist:{jti}") is not None or jti not in store.set_members(f"refresh:{user_id}"):
        # Detección de reuso (RF-05): revocar toda la cadena del usuario
        store.delete_key(f"refresh:{user_id}")
        raise HTTPException(status_code=401, detail="Refresh token revocado o reutilizado")

    # Rotar: revocar el refresh anterior y emitir nuevos tokens
    gather = store.set_members(f"refresh:{user_id}")
    gather.discard(jti)
    revoke_token(jti, token_payload.get("exp"))

    role = token_payload.get("role", "Cliente")
    new_access = create_access_token(user_id, role)
    new_refresh = create_refresh_token(user_id, role)
    new_payload = decode_token(new_refresh)
    gather.add(new_payload["jti"])
    store.delete_key(f"refresh:{user_id}")
    for j in gather:
        store.add_to_set(f"refresh:{user_id}", j)
    return TokenResponse(access_token=new_access, refresh_token=new_refresh)


@router.post("/logout", status_code=204)
def logout(payload: RefreshRequest, user: dict = Depends(get_current_user)):
    store = get_token_store()
    # Revocar el access token actual
    revoke_token(user.get("jti", ""), user.get("exp"))
    try:
        refresh_payload = decode_token(payload.refresh_token)
        if refresh_payload.get("sub") == user.get("sub"):
            revoke_token(refresh_payload.get("jti", ""), refresh_payload.get("exp"))
            current = store.set_members(f"refresh:{user['sub']}")
            current.discard(refresh_payload.get("jti", ""))
            store.delete_key(f"refresh:{user['sub']}")
            for j in current:
                store.add_to_set(f"refresh:{user['sub']}", j)
    except jwt.PyJWTError:
        pass
    return None
