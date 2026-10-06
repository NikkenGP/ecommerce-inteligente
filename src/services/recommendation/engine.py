"""Motor híbrido de recomendación: CF item-based + reglas de negocio."""

from __future__ import annotations

import logging
import time

from sqlalchemy.orm import Session

from src.models.product import Product
from src.services.recommendation.collaborative import CollaborativeRecommender
from src.services.recommendation.history import interaction_count, products_bought_recently
from src.services.recommendation.rules import RuleBasedRecommender
from src.services.recommendation.schemas import ProductScore

logger = logging.getLogger("recommendation")

ALPHA = 0.7  # peso CF
BETA = 0.3  # peso reglas
COLD_START_THRESHOLD = 3


class HybridRecommendationEngine:
    """Fusiona filtrado colaborativo y reglas con `score = 0.7*CF + 0.3*rules`."""

    def __init__(
        self,
        db: Session,
        cf: CollaborativeRecommender | None = None,
        rules: RuleBasedRecommender | None = None,
        alpha: float = ALPHA,
        beta: float = BETA,
    ) -> None:
        self.db = db
        self.cf = cf or CollaborativeRecommender(db)
        self.rules = rules or RuleBasedRecommender(db)
        self.alpha = alpha
        self.beta = beta

    def recommend(self, user_id: str, context: dict | None = None, limit: int = 10) -> tuple[list[ProductScore], str]:
        started = time.perf_counter()
        interactions = interaction_count(self.db, user_id)

        # Cold start (RF-04): menos de 3 interacciones => solo reglas
        if interactions < COLD_START_THRESHOLD:
            results = self.rules.recommend(user_id, context, limit)
            strategy = "rules"
            self._log(user_id, strategy, started, results)
            return results, strategy

        # Estrategia híbrida (RF-03) con fallback a reglas (RF-05)
        try:
            cf_results = self.cf.recommend(user_id, context, limit)
        except Exception as exc:  # noqa: BLE001
            logger.warning("CF falló para %s: %s; fallback a reglas", user_id, exc)
            results = self.rules.recommend(user_id, context, limit)
            self._log(user_id, "rules(fallback)", started, results)
            return results, "rules"

        rule_results = self.rules.recommend(user_id, context, limit)
        results = self._fuse(cf_results, rule_results, user_id)
        strategy = "hybrid" if cf_results and rule_results else ("collaborative" if cf_results else "rules")
        results = results[:limit]
        self._log(user_id, strategy, started, results)
        return results, strategy

    def _fuse(self, cf_results: list[ProductScore], rule_results: list[ProductScore], user_id: str) -> list[ProductScore]:
        cf_map = {r.product_id: r.score for r in cf_results}
        rule_map = {r.product_id: r.score for r in rule_results}
        recently = products_bought_recently(self.db, user_id)

        fused: list[ProductScore] = []
        for pid in set(cf_map) | set(rule_map):
            if pid in recently:
                continue
            product = self.db.get(Product, pid)
            if not product or product.stock <= 0:
                continue
            cf_score = cf_map.get(pid, 0.0)
            rule_score = rule_map.get(pid, 0.0)
            final = round(min(max(self.alpha * cf_score + self.beta * rule_score, 0.0), 1.0), 4)
            if pid in cf_map and pid in rule_map:
                source = "hybrid"
            elif pid in cf_map:
                source = "collaborative"
            else:
                source = "rules"
            fused.append(ProductScore(product_id=pid, score=final, source=source))

        # Desempate: rating descendente, luego product_id (CL-03)
        ratings: dict[str, float] = {}
        for f in fused:
            product = self.db.get(Product, f.product_id)
            ratings[f.product_id] = product.rating if product else 0.0
        fused.sort(key=lambda f: (-f.score, -ratings.get(f.product_id, 0.0), f.product_id))
        return fused

    def _log(self, user_id: str, strategy: str, started: float, results: list[ProductScore]) -> None:
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        logger.info(
            "recommendation_decision user_id=%s strategy=%s latency_ms=%s result_count=%d",
            user_id, strategy, latency_ms, len(results),
        )
