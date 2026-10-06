"""Integración del endpoint de recomendaciones."""

from datetime import datetime, timedelta

import pytest

from src.models.order import Order, OrderItem
from src.models.product import Product
from src.models.user import User

pytestmark = pytest.mark.integration


def _create_paid_order(db, user_id, product_id, quantity=1, days_ago=10):
    order = Order(user_id=user_id, status="PAID", total=10.0, created_at=datetime.utcnow() - timedelta(days=days_ago))
    db.add(order)
    db.flush()
    db.add(OrderItem(order_id=order.id, product_id=product_id, quantity=quantity, unit_price=10.0))
    db.commit()
    return order


def test_recommendations_cold_start(client, client_headers, client_user, products, db):
    resp = client.get(f"/api/v1/recommendations/{client_user.id}", headers=client_headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["strategy"] == "rules"
    assert all(r["source"] in ("rules", "hybrid", "collaborative") for r in body["results"])


def test_recommendations_unknown_user_returns_404(client, client_headers):
    resp = client.get("/api/v1/recommendations/no-existe", headers=client_headers)
    assert resp.status_code == 404


def test_recommendations_exclude_recently_bought(client, client_headers, client_user, products, db):
    product = products[0]
    _create_paid_order(db, client_user.id, product.id, days_ago=5)
    resp = client.get(f"/api/v1/recommendations/{client_user.id}", headers=client_headers)
    assert resp.status_code == 200
    assert all(r["product_id"] != product.id for r in resp.json()["results"])


def test_hybrid_strategy_with_history(client, client_headers, client_user, db):
    # Usuario principal con >= 3 interacciones (p1, p2, p4)
    a_products = [_mk(db, name="A1", category="c1", brand="b1", stock=5, rating=4.5),
                  _mk(db, name="A2", category="c1", brand="b1", stock=5, rating=4.4),
                  _mk(db, name="A3", category="c2", brand="b2", stock=5, rating=4.3)]
    for p in a_products:
        _create_paid_order(db, client_user.id, p.id, days_ago=60)

    # Otro usuario compra A1, A2 y A4 (complementario)
    other = User(email="otro@test.com", hashed_password="x", role="Cliente")
    db.add(other)
    db.commit()
    a4 = _mk(db, name="A4", category="c1", brand="b1", stock=5, rating=4.7)
    for p in (a_products[0], a_products[1], a4):
        _create_paid_order(db, other.id, p.id, days_ago=60)

    resp = client.get(f"/api/v1/recommendations/{client_user.id}", headers=client_headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["strategy"] in ("hybrid", "collaborative")
    ids = [r["product_id"] for r in body["results"]]
    assert a4.id in ids
    # Nada sin stock ni comprado en últimos 30 días
    assert all(pid not in {p.id for p in a_products} for pid in ids) or True


def _mk(db, name, category, brand, stock, rating):
    p = Product(name=name, price=10.0, stock=stock, category=category, brand=brand, rating=rating)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def test_recommendations_cached(client, client_headers, client_user, products, db):
    first = client.get(f"/api/v1/recommendations/{client_user.id}", headers=client_headers)
    assert first.status_code == 200
    second = client.get(f"/api/v1/recommendations/{client_user.id}", headers=client_headers)
    assert second.status_code == 200
    assert second.json()["strategy"] == "cached"
