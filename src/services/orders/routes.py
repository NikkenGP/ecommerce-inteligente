"""Endpoints de pedidos: historial y cancelación."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.order import Order
from src.models.product import Product
from src.schemas.order import OrderItemResponse, OrderResponse
from src.services.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])


def _to_response(order: Order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        status=order.status,
        total=order.total,
        created_at=order.created_at,
        items=[
            OrderItemResponse(product_id=i.product_id, quantity=i.quantity, unit_price=i.unit_price)
            for i in order.items
        ],
    )


@router.get("", response_model=dict)
def list_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    query = db.query(Order).filter(Order.user_id == user["sub"]).order_by(Order.created_at.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [_to_response(o) for o in items], "page": page, "page_size": page_size, "total": total}


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    order = db.get(Order, order_id)
    if not order or (order.user_id != user["sub"] and user.get("role") != "Administrador"):
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return _to_response(order)


@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(order_id: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    order = db.get(Order, order_id)
    if not order or order.user_id != user["sub"]:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if order.status != "PENDING":
        raise HTTPException(status_code=409, detail="Solo pedidos PENDING pueden cancelarse")
    order.status = "CANCELLED"
    # Restituir stock reservado
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).with_for_update().first()
        if product:
            product.stock += item.quantity
    db.commit()
    db.refresh(order)
    return _to_response(order)
