"""Pruebas de integración del catálogo."""

import pytest

pytestmark = pytest.mark.integration


def test_list_products_with_filters(client, products):
    resp = client.get("/api/v1/products", params={"category": "electronics"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert all(p["category"] == "electronics" for p in data["items"])


def test_on_sale_filter(client, products):
    resp = client.get("/api/v1/products", params={"on_sale": True})
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


def test_pagination_out_of_range_returns_empty(client, products):
    resp = client.get("/api/v1/products", params={"page": 99})
    assert resp.status_code == 200
    assert resp.json()["items"] == []


def test_get_product_detail(client, products):
    product = products[0]
    resp = client.get(f"/api/v1/products/{product.id}")
    assert resp.status_code == 200
    body = resp.json()
    assert {"id", "name", "price", "stock", "category", "brand", "rating"} <= set(body)


def test_get_missing_product_returns_404(client, products):
    resp = client.get("/api/v1/products/no-existe")
    assert resp.status_code == 404
