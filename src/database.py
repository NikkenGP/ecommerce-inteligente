"""Conexión a la base de datos con SQLAlchemy."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from src.config import get_settings


class Base(DeclarativeBase):
    """Clase base declarativa para los modelos SQLAlchemy."""


def _build_engine():
    settings = get_settings()
    connect_args = {}
    # SQLite requiere esta bandera cuando se usa con TestClient (multihilo)
    if settings.database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    return create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)


engine = _build_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    """Dependencia FastAPI que entrega una sesión y garantiza su cierre."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Crea las tablas si no existen (uso en desarrollo/pruebas)."""
    from src import models  # noqa: F401  (importación para registrar metadatos)

    Base.metadata.create_all(bind=engine)
