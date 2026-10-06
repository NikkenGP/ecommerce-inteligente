"""Fixtures globales: entorno de pruebas con SQLite y TestClient."""

import os

# Configurar entorno ANTES de importar la app
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_ecommerce.db")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("PAYMENT_DEFAULT_SCENARIO", "approved")

import pytest
from fastapi.testclient import TestClient

from src.database import Base, engine, init_db
from src.main import app


@pytest.fixture(scope="session", autouse=True)
def _setup_db():
    Base.metadata.drop_all(bind=engine)
    init_db()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(_setup_db):
    with TestClient(app) as c:
        yield c
