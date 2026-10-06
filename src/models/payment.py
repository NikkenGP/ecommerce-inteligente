"""Modelo de pago asociado a un pedido."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id: Mapped[str | None] = mapped_column(ForeignKey("orders.id"), nullable=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    # Estados: approved, declined, timeout
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    transaction_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    order: Mapped["Order | None"] = relationship(back_populates="payment")
