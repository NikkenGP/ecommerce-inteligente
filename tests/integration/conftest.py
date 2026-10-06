"""Fixtures de integración: DB limpia por prueba, usuarios y catálogo semilla."""

import pytest

from src.database import Base, engine, SessionLocal
from src.models.user import User
from src.services.auth.security import hash_password
from tests.mocks.factories import seed_products


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture()
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def admin_user(db):
    user = User(email="admin@test.com", hashed_password=hash_password("Admin123!"), role="Administrador")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def client_user(db):
    user = User(email="cliente@test.com", hashed_password=hash_password("Secret123!"), role="Cliente")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def products(db):
    return seed_products(db)


def _login_headers(client, email: str, password: str) -> dict:
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def client_headers(client, client_user):
    return _login_headers(client, "cliente@test.com", "Secret123!")


@pytest.fixture()
def admin_headers(client, admin_user):
    return _login_headers(client, "admin@test.com", "Admin123!")
