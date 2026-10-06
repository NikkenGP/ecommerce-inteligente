"""Utilidades compartidas del motor: historial de compras por usuario."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from src.models.order import Order, OrderItem


def user_purchase_counts(db: Session) -> dict[str, dict[str, int]]:
    """Matriz usuario -> {producto: cantidad_comprada} a partir de pedidos PAID."""
    matrix: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    rows = (
        db.query(Order.user_id, OrderItem.product_id, OrderItem.quantity)
        .join(OrderItem, OrderItem.order_id == Order.id)
        .filter(Order.status == "PAID")
        .all()
    )
    for user_id, product_id, quantity in rows:
        matrix[user_id][product_id] += quantity
    return {u: dict(items) for u, items in matrix.items()}


def products_bought_recently(db: Session, user_id: str, days: int = 30) -> set[str]:
    """Productos comprados por el usuario en los últimos `days` días."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    rows = (
        db.query(OrderItem.product_id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.user_id == user_id, Order.status == "PAID", Order.created_at >= cutoff)
        .all()
    )
    return {r[0] for r in rows}


def interaction_count(db: Session, user_id: str) -> int:
    """Número total de líneas de pedido del usuario (interacciones)."""
    return (
        db.query(OrderItem)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.user_id == user_id, Order.status == "PAID")
        .count()
    )


def last_purchased_product_ids(db: Session, user_id: str, limit: int = 5) -> list[str]:
    rows = (
        db.query(OrderItem.product_id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.user_id == user_id, Order.status == "PAID")
        .order_by(Order.created_at.desc())
        .limit(limit)
        .all()
    )
    return [r[0] for r in rows]
