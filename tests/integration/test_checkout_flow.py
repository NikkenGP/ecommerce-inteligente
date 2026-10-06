"""Flujo de checkout con pagos simulados e idempotencia."""

import pytest

pytestmark = pytest.mark.integration


def _add_to_cart(client, headers, product_id, quantity=1):
    return client.post("/api/v1/cart/items", json={"product_id": product_id, "quantity": quantity}, headers=headers)


def test_checkout_approved_creates_order_and_decreases_stock(client, client_headers, products, client_user, db):
    product = products[0]
    original_stock = product.stock
    assert _add_to_cart(client, client_headers, product.id, 2).status_code == 201
    resp = client.post("/api/v1/checkout", json={"scenario": "approved"}, headers=client_headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["payment"]["status"] == "approved"
    assert body["order"]["status"] == "PAID"
    db.expire_all()
    assert db.get(type(product), product.id).stock == original_stock - 2


def test_checkout_declined_creates_no_order(client, client_headers, products):
    assert _add_to_cart(client, client_headers, products[0].id, 1).status_code == 201
    resp = client.post("/api/v1/checkout", json={"scenario": "declined"}, headers=client_headers)
    assert resp.status_code == 200
    assert resp.json()["payment"]["status"] == "declined"
    assert resp.json()["order"] is None


def test_checkout_timeout_returns_504_and_is_idempotent(client, client_headers, products):
    assert _add_to_cart(client, client_headers, products[0].id, 1).status_code == 201
    resp = client.post(
        "/api/v1/checkout",
        json={"scenario": "timeout", "idempotency_key": "key-1"},
        headers=client_headers,
    )
    assert resp.status_code == 504

    # Reintentar con la misma clave y escenario approved no duplica cargo y completa
    resp = client.post(
        "/api/v1/checkout",
        json={"scenario": "approved", "idempotency_key": "key-1"},
        headers=client_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["payment"]["status"] == "approved"

    # Un tercer llamado con la misma clave devuelve el mismo resultado sin crear otro pedido
    resp = client.post(
        "/api/v1/checkout",
        json={"scenario": "approved", "idempotency_key": "key-1"},
        headers=client_headers,
    )
    assert resp.status_code == 200
    orders = client.get("/api/v1/orders", headers=client_headers).json()
    assert orders["total"] == 1


def test_checkout_with_empty_cart_returns_400(client, client_headers):
    resp = client.post("/api/v1/checkout", json={"scenario": "approved"}, headers=client_headers)
    assert resp.status_code == 400


def test_add_item_with_insufficient_stock_returns_409(client, client_headers, products):
    out_of_stock = products[2]  # stock 0
    resp = _add_to_cart(client, client_headers, out_of_stock.id, 1)
    assert resp.status_code == 409
