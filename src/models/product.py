"""Modelos de producto y auditoría de stock."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    category: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    brand: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    on_sale: Mapped[bool] = mapped_column(default=False)
    sale_price: Mapped[float | None] = mapped_column(Float, nullable=True)

    @property
    def effective_price(self) -> float:
        """Precio vigente considerando promoción."""
        if self.on_sale and self.sale_price is not None:
            return self.sale_price
        return self.price


class StockAudit(Base):
    """Registro de auditoría para ajustes de stock hechos por administradores."""

    __tablename__ = "stock_audits"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    delta: Mapped[int] = mapped_column(Integer, nullable=False)
    admin_id: Mapped[str] = mapped_column(String(36), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
