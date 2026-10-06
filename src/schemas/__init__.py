"""Esquemas Pydantic de la API."""

from src.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)
from src.schemas.cart import CartItemCreate, CartItemResponse, CartItemUpdate, CartResponse
from src.schemas.order import CheckoutRequest, OrderResponse, PaymentStatusResponse
from src.schemas.product import ProductCreate, ProductResponse, ProductUpdate, StockUpdate
from src.schemas.recommendation import RecommendationResponse, ProductScoreResponse

__all__ = [
    "LoginRequest",
    "RefreshRequest",
    "TokenResponse",
    "UserCreate",
    "UserResponse",
    "CartItemCreate",
    "CartItemResponse",
    "CartItemUpdate",
    "CartResponse",
    "CheckoutRequest",
    "OrderResponse",
    "PaymentStatusResponse",
    "ProductCreate",
    "ProductResponse",
    "ProductUpdate",
    "StockUpdate",
    "RecommendationResponse",
    "ProductScoreResponse",
]
