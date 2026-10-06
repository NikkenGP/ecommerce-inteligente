"""Esquemas del carrito."""

from pydantic import BaseModel, Field


class CartItemCreate(BaseModel):
    product_id: str
    quantity: int = Field(ge=1)


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=0)


class CartItemResponse(BaseModel):
    product_id: str
    quantity: int
    unit_price: float
    subtotal: float


class CartResponse(BaseModel):
    user_id: str
    items: list[CartItemResponse]
    subtotal: float
    tax: float
    total: float
