"""Punto de entrada de la aplicación FastAPI."""

from __future__ import annotations

import logging

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.database import init_db
from src.services.auth.routes import router as auth_router
from src.services.cart.routes import router as cart_router
from src.services.catalog.routes import router as catalog_router
from src.services.orders.routes import router as orders_router
from src.services.payments.routes import router as checkout_router
from src.services.recommendation.routes import router as recommendations_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

app = FastAPI(title="E-Commerce Intelligent Platform", version="1.0.0")

app.include_router(auth_router)
app.include_router(catalog_router)
app.include_router(cart_router)
app.include_router(checkout_router)
app.include_router(orders_router)
app.include_router(recommendations_router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


# Vistas estáticas (Tailwind + JS vanilla) servidas desde el mismo origen para evitar CORS.
_views_dir = Path(__file__).parent / "views"
if _views_dir.exists():
    app.mount("/", StaticFiles(directory=str(_views_dir), html=True), name="views")
