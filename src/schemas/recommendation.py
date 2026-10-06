"""Esquemas del motor de recomendación."""

from pydantic import BaseModel, Field


class ProductScoreResponse(BaseModel):
    product_id: str
    score: float = Field(ge=0.0, le=1.0)
    source: str  # collaborative | rules | hybrid


class RecommendationResponse(BaseModel):
    user_id: str
    strategy: str
    latency_ms: float
    results: list[ProductScoreResponse]
