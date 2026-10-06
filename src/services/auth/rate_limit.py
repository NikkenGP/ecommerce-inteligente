"""Rate limiting simple para el endpoint de login (máx. 5 fallos/IP por minuto)."""

from __future__ import annotations

import time

from src.services.auth.store import get_token_store

MAX_ATTEMPTS = 5
WINDOW_SECONDS = 60


def register_failed_attempt(ip: str) -> int:
    store = get_token_store()
    key = f"loginfail:{ip}:{int(time.time() // WINDOW_SECONDS)}"
    count_raw = store.get(key)
    count = int(count_raw) + 1 if count_raw else 1
    store.set(key, str(count), WINDOW_SECONDS * 2)
    return count


def is_rate_limited(ip: str) -> bool:
    store = get_token_store()
    key = f"loginfail:{ip}:{int(time.time() // WINDOW_SECONDS)}"
    count_raw = store.get(key)
    return bool(count_raw and int(count_raw) >= MAX_ATTEMPTS)
