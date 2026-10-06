"""Endpoint del motor de recomendación."""

from __future__ import annotations

import time

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.user import User
from src.schemas.recommendation import ProductScoreResponse, RecommendationResponse
from src.services.auth.dependencies import get_current_user
from src.services.recommendation.cache import get_cache
from src.services.recommendation.engine import HybridRecommendationEngine

router = APIRouter(prefix="/api/v1/recommendations", tags=["recommendations"])


@router.get("/{user_id}", response_model=RecommendationResponse)
def get_recommendations(
    user_id: str,
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if not db.get(User, user_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    # Un cliente solo puede ver sus propias recomendaciones (R2)
    if current_user["sub"] != user_id and current_user.get("role") != "Administrador":
        raise HTTPException(status_code=403, detail="No autorizado para este recurso")

    started = time.perf_counter()
    cache = get_cache()
    cached = cache.get(user_id)
    if cached is not None:
        results = cached[:limit]
        return RecommendationResponse(
            user_id=user_id,
            strategy="cached",
            latency_ms=round((time.perf_counter() - started) * 1000, 2),
            results=[ProductScoreResponse(**r) for r in results],
        )

    engine = HybridRecommendationEngine(db)
    scores, strategy = engine.recommend(user_id, limit=limit)
    latency_ms = round((time.perf_counter() - started) * 1000, 2)
    payload = [{"product_id": s.product_id, "score": s.score, "source": s.source} for s in scores]
    cache.set(user_id, payload)
    return RecommendationResponse(
        user_id=user_id,
        strategy=strategy,
        latency_ms=latency_ms,
        results=[ProductScoreResponse(**p) for p in payload],
    )
