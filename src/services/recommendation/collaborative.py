"""Filtrado colaborativo item-based con similitud de coseno."""

from __future__ import annotations

import math
from collections import defaultdict

from sqlalchemy.orm import Session

from src.models.product import Product
from src.services.recommendation.history import products_bought_recently, user_purchase_counts
from src.services.recommendation.schemas import ProductScore


class CollaborativeRecommender:
    def __init__(self, db: Session) -> None:
        self.db = db

    def recommend(self, user_id: str, context: dict | None = None, limit: int = 10) -> list[ProductScore]:
        matrix = user_purchase_counts(self.db)
        user_items = matrix.get(user_id, {})
        if not user_items:
            return []

        # Similitud coseno entre cada producto del usuario y los candidatos
        item_users: dict[str, dict[str, int]] = defaultdict(dict)
        for uid, items in matrix.items():
            for pid, qty in items.items():
                item_users[pid][uid] = qty

        recently_bought = products_bought_recently(self.db, user_id)
        candidate_scores: dict[str, float] = defaultdict(float)
        candidate_sim_sum: dict[str, float] = defaultdict(float)

        for owned_pid, owned_qty in user_items.items():
            owned_vec = item_users.get(owned_pid, {})
            if not owned_vec:
                continue
            for candidate_pid, candidate_users in item_users.items():
                if candidate_pid == owned_pid or candidate_pid in user_items:
                    continue
                sim = _cosine(owned_vec, candidate_users)
                if sim <= 0:
                    continue
                candidate_scores[candidate_pid] += sim * owned_qty
                candidate_sim_sum[candidate_pid] += sim

        raw: dict[str, float] = {}
        for pid, total in candidate_scores.items():
            denom = candidate_sim_sum[pid]
            if denom > 0:
                raw[pid] = total / denom

        # Filtrar stock > 0 y no comprados en últimos 30 días
        candidates: list[ProductScore] = []
        for pid, score in sorted(raw.items(), key=lambda kv: kv[1], reverse=True):
            product = self.db.get(Product, pid)
            if not product or product.stock <= 0 or pid in recently_bought:
                continue
            candidates.append(ProductScore(product_id=pid, score=score, source="collaborative"))
            if len(candidates) >= limit:
                break

        return _normalize(candidates)


def _cosine(a: dict[str, int], b: dict[str, int]) -> float:
    shared = set(a) & set(b)
    if not shared:
        return 0.0
    dot = sum(a[k] * b[k] for k in shared)
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _normalize(items: list[ProductScore]) -> list[ProductScore]:
    if not items:
        return items
    max_score = max(i.score for i in items) or 1.0
    for item in items:
        item.score = round(min(max(item.score / max_score, 0.0), 1.0), 4)
    return items
