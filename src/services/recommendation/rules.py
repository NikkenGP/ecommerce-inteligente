"""Recomendaciones basadas en reglas de negocio."""

from __future__ import annotations

from sqlalchemy.orm import Session

from src.models.product import Product
from src.services.recommendation.history import last_purchased_product_ids, products_bought_recently
from src.services.recommendation.schemas import ProductScore

WEIGHT_SAME_CATEGORY = 0.5
WEIGHT_ON_SALE_SAME_BRAND = 0.3
WEIGHT_TOP_RATED = 0.2


class RuleBasedRecommender:
    def __init__(self, db: Session) -> None:
        self.db = db

    def recommend(self, user_id: str, context: dict | None = None, limit: int = 10) -> list[ProductScore]:
        recently_bought = products_bought_recently(self.db, user_id)
        scores: dict[str, float] = {}

        def add(product: Product, weight: float) -> None:
            if product.stock <= 0 or product.id in recently_bought:
                return
            scores[product.id] = min(scores.get(product.id, 0.0) + weight, 1.0)

        last_ids = last_purchased_product_ids(self.db, user_id, limit=5)
        seed_products = [self.db.get(Product, pid) for pid in last_ids]
        seed_products = [p for p in seed_products if p is not None]
        seed_categories = {p.category for p in seed_products}
        seed_brands = {p.brand for p in seed_products}

        # R1: misma categoría que lo último comprado
        if seed_categories:
            for p in self.db.query(Product).filter(Product.category.in_(seed_categories)).all():
                add(p, WEIGHT_SAME_CATEGORY)

        # R3: productos en promoción de marcas ya compradas
        if seed_brands:
            for p in (
                self.db.query(Product)
                .filter(Product.brand.in_(seed_brands), Product.on_sale.is_(True))
                .all()
            ):
                add(p, WEIGHT_ON_SALE_SAME_BRAND)

        # R4: fallback global con rating >= 4.0 y stock > 0
        for p in self.db.query(Product).filter(Product.rating >= 4.0, Product.stock > 0).all():
            add(p, WEIGHT_TOP_RATED)

        items = [
            ProductScore(product_id=pid, score=round(score, 4), source="rules")
            for pid, score in sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        ]
        return items[:limit]
