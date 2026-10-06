"""Endpoint de checkout: pago simulado, pedido e inventario."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.config import get_settings
from src.database import get_db
from src.models.cart import Cart
from src.models.order import Order, OrderItem
from src.models.payment import Payment
from src.models.product import Product
from src.schemas.order import CheckoutRequest, CheckoutResponse, OrderItemResponse, OrderResponse, PaymentStatusResponse
from src.services.auth.dependencies import get_current_user
from src.services.cart.service import compute_totals
from src.services.payments.gateway import MockPaymentGateway, PaymentTimeoutError

router = APIRouter(prefix="/api/v1", tags=["checkout"])


def _order_response(order: Order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        status=order.status,
        total=order.total,
        created_at=order.created_at,
        items=[OrderItemResponse(product_id=i.product_id, quantity=i.quantity, unit_price=i.unit_price) for i in order.items],
    )


@router.post("/checkout", response_model=CheckoutResponse)
def checkout(
    payload: CheckoutRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    user_id = user["sub"]

    # Idempotencia: misma clave con cargo aprobado => devolver el resultado previo
    if payload.idempotency_key:
        existing = (
            db.query(Payment)
            .filter(Payment.idempotency_key == payload.idempotency_key, Payment.user_id == user_id)
            .order_by(Payment.created_at.desc())
            .first()
        )
        if existing and existing.status == "approved" and existing.order_id:
            order = db.get(Order, existing.order_id)
            return CheckoutResponse(
                order=_order_response(order),
                payment=PaymentStatusResponse(status="approved", transaction_id=existing.transaction_id),
            )

    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="El carrito está vacío")

    # Bloqueo pesimista por fila sobre los productos (CL-01 / RF-03 spec 005)
    products: dict[str, Product] = {}
    for item in cart.items:
        product = (
            db.query(Product).filter(Product.id == item.product_id).with_for_update().first()
        )
        if not product:
            raise HTTPException(status_code=404, detail=f"Producto {item.product_id} no existe")
        products[product.id] = product

    # Validar stock; si bajó desde el agregado, ajustar y notificar (RF-05 spec 003)
    insufficient = [
        {"product_id": i.product_id, "requested": i.quantity, "available": products[i.product_id].stock}
        for i in cart.items
        if products[i.product_id].stock < i.quantity
    ]
    if insufficient:
        raise HTTPException(
            status_code=409,
            detail={"code": "INSUFFICIENT_STOCK", "message": "Stock insuficiente, ajuste su carrito", "items": insufficient},
        )

    totals = compute_totals([i.subtotal for i in cart.items])
    amount = totals["total"]
    if amount <= 0:
        raise HTTPException(status_code=422, detail="Monto inválido")

    gateway = MockPaymentGateway(default_scenario=get_settings().payment_default_scenario)
    try:
        result = gateway.charge(amount=amount, currency=payload.currency, scenario=payload.scenario)
    except PaymentTimeoutError:
        db.add(
            Payment(
                user_id=user_id,
                amount=amount,
                status="timeout",
                idempotency_key=payload.idempotency_key,
            )
        )
        db.commit()
        raise HTTPException(
            status_code=504,
            detail={
                "code": "PAYMENT_TIMEOUT",
                "message": "La pasarela no respondió; reintente con la misma idempotency_key",
                "idempotency_key": payload.idempotency_key,
            },
        )

    if result.status == "declined":
        db.add(
            Payment(
                user_id=user_id,
                amount=amount,
                status="declined",
                reason=result.reason,
                idempotency_key=payload.idempotency_key,
            )
        )
        db.commit()
        return CheckoutResponse(order=None, payment=PaymentStatusResponse(status="declined", reason=result.reason))

    # Pago aprobado: crear pedido, descontar stock y vaciar carrito en la misma transacción
    order = Order(user_id=user_id, status="PAID", total=amount)
    db.add(order)
    db.flush()
    for item in cart.items:
        product = products[item.product_id]
        product.stock -= item.quantity
        db.add(OrderItem(order_id=order.id, product_id=item.product_id, quantity=item.quantity, unit_price=product.effective_price))
    for item in list(cart.items):
        cart.items.remove(item)
    db.add(
        Payment(
            order_id=order.id,
            user_id=user_id,
            amount=amount,
            status="approved",
            transaction_id=result.transaction_id,
            idempotency_key=payload.idempotency_key,
        )
    )
    db.commit()
    db.refresh(order)
    return CheckoutResponse(
        order=_order_response(order),
        payment=PaymentStatusResponse(status="approved", transaction_id=result.transaction_id),
    )
