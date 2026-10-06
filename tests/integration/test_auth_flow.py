"""Flujo de autenticación: register → login → refresh → logout."""

import pytest

pytestmark = pytest.mark.integration


def test_register_login_refresh_logout_flow(client):
    resp = client.post("/api/v1/auth/register", json={"email": "nuevo@test.com", "password": "Secret123!"})
    assert resp.status_code == 201, resp.text
    assert resp.json()["role"] == "Cliente"

    resp = client.post("/api/v1/auth/login", json={"email": "nuevo@test.com", "password": "Secret123!"})
    assert resp.status_code == 200
    tokens = resp.json()

    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert resp.status_code == 200
    new_tokens = resp.json()
    assert new_tokens["refresh_token"] != tokens["refresh_token"]

    # El refresh token anterior ya no es válido (rotación)
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert resp.status_code == 401

    resp = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": new_tokens["refresh_token"]},
        headers={"Authorization": f"Bearer {new_tokens['access_token']}"},
    )
    assert resp.status_code == 204

    # El access token revocado ya no autoriza
    resp = client.get("/api/v1/cart", headers={"Authorization": f"Bearer {new_tokens['access_token']}"})
    assert resp.status_code == 401


def test_login_wrong_password_returns_401(client, client_user):
    resp = client.post("/api/v1/auth/login", json={"email": "cliente@test.com", "password": "mala-clave"})
    assert resp.status_code == 401


def test_protected_route_requires_token(client):
    resp = client.get("/api/v1/cart")
    assert resp.status_code in (401, 403)


def test_cliente_forbidden_on_admin_route(client, client_headers, products):
    resp = client.post(
        "/api/v1/products",
        json={"name": "X", "price": 10, "stock": 1, "category": "c", "brand": "b"},
        headers=client_headers,
    )
    assert resp.status_code == 403


def test_admin_can_create_product(client, admin_headers):
    resp = client.post(
        "/api/v1/products",
        json={"name": "Monitor", "price": 200, "stock": 3, "category": "electronics", "brand": "Acme"},
        headers=admin_headers,
    )
    assert resp.status_code == 201


def test_invalid_product_payload_returns_422(client, admin_headers):
    resp = client.post(
        "/api/v1/products",
        json={"name": "Monitor", "price": -5, "stock": 3, "category": "c", "brand": "b"},
        headers=admin_headers,
    )
    assert resp.status_code == 422
