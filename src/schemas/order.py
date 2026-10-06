"""Esquemas de pedidos y checkout."""

from datetime import datetime

from pydantic import BaseModel, Field


class CheckoutRequest(BaseModel):
    scenario: str | None = Field(default=None, pattern="^(approved|declined|timeout)$")
    idempotency_key: str | None = None
    currency: str = "USD"


class OrderItemResponse(BaseModel):
    product_id: str
    quantity: int
    unit_price: float


class OrderResponse(BaseModel):
    id: str
    user_id: str
    status: str
    total: float
    created_at: datetime
    items: list[OrderItemResponse] = []

    model_config = {"from_attributes": True}


class PaymentStatusResponse(BaseModel):
    status: str
    transaction_id: str | None = None
    reason: str | None = None


class CheckoutResponse(BaseModel):
    order: OrderResponse | None = None
    payment: PaymentStatusResponse
