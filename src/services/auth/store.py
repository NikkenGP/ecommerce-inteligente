"""Almacén con TTL usado para blacklist de tokens y control de intentos de login.

Usa Redis si está disponible y, en caso contrario, un diccionario en memoria
(degradación elegante según CL-03 de la spec maestra).
"""

from __future__ import annotations

import time

from src.config import get_settings


class TTLStore:
    """Interfaz de almacenamiento clave-valor con expiración."""

    def set(self, key: str, value: str, ttl_seconds: int) -> None: ...
    def get(self, key: str) -> str | None: ...
    def delete(self, key: str) -> None: ...
    def add_to_set(self, key: str, value: str) -> None: ...
    def set_members(self, key: str) -> set[str]: ...
    def delete_key(self, key: str) -> None: ...


class MemoryStore(TTLStore):
    def __init__(self) -> None:
        self._data: dict[str, tuple[str, float]] = {}
        self._sets: dict[str, set[str]] = {}

    def _expired(self, key: str) -> bool:
        item = self._data.get(key)
        if item and item[1] < time.time():
            del self._data[key]
            return True
        return False

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        self._data[key] = (value, time.time() + ttl_seconds)

    def get(self, key: str) -> str | None:
        if self._expired(key):
            return None
        item = self._data.get(key)
        return item[0] if item else None

    def delete(self, key: str) -> None:
        self._data.pop(key, None)

    def add_to_set(self, key: str, value: str) -> None:
        self._sets.setdefault(key, set()).add(value)

    def set_members(self, key: str) -> set[str]:
        return set(self._sets.get(key, set()))

    def delete_key(self, key: str) -> None:
        self._sets.pop(key, None)
        self._data.pop(key, None)


class RedisStore(TTLStore):
    def __init__(self, url: str) -> None:
        import redis

        self._client = redis.Redis.from_url(url, decode_responses=True)

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        self._client.setex(key, ttl_seconds, value)

    def get(self, key: str) -> str | None:
        return self._client.get(key)

    def delete(self, key: str) -> None:
        self._client.delete(key)

    def add_to_set(self, key: str, value: str) -> None:
        self._client.sadd(key, value)

    def set_members(self, key: str) -> set[str]:
        return set(self._client.smembers(key))

    def delete_key(self, key: str) -> None:
        self._client.delete(key)


def build_store() -> TTLStore:
    """Intenta construir un store Redis; si no hay servidor, usa memoria."""
    try:
        store = RedisStore(get_settings().redis_url)
        store._client.ping()
        return store
    except Exception:
        return MemoryStore()


# Singleton de proceso; tests pueden reemplazarlo con monkeypatch
_token_store: TTLStore | None = None


def get_token_store() -> TTLStore:
    global _token_store
    if _token_store is None:
        _token_store = build_store()
    return _token_store


def reset_token_store() -> None:
    """Restablece el store (útil en pruebas)."""
    global _token_store
    _token_store = None
