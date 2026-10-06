"""Capa de caché de recomendaciones con TTL de 5 minutos.

Clave: `reco:{user_id}`. Usa Redis si está disponible; si cae, degrada a
cálculo directo sin caché (CL-02 de la spec 006).
"""

from __future__ import annotations

import json

from src.config import get_settings
from src.services.auth.store import TTLStore, build_store


class RecommendationCache:
    def __init__(self, store: TTLStore | None = None) -> None:
        self._store = store if store is not None else build_store()
        self._ttl = get_settings().cache_ttl_seconds

    def get(self, user_id: str) -> list[dict] | None:
        try:
            raw = self._store.get(f"reco:{user_id}")
            return json.loads(raw) if raw else None
        except Exception:
            return None

    def set(self, user_id: str, results: list[dict]) -> None:
        try:
            self._store.set(f"reco:{user_id}", json.dumps(results), self._ttl)
        except Exception:
            pass

    def clear(self, user_id: str) -> None:
        try:
            self._store.delete(f"reco:{user_id}")
        except Exception:
            pass


_cache: RecommendationCache | None = None


def get_cache() -> RecommendationCache:
    global _cache
    if _cache is None:
        _cache = RecommendationCache()
    return _cache
