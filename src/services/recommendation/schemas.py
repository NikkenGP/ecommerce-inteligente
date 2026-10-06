"""Esquemas internos del motor de recomendación."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ProductScore:
    """Puntuación de un producto recomendado."""

    product_id: str
    score: float  # normalizado [0.0, 1.0]
    source: str  # collaborative | rules | hybrid
