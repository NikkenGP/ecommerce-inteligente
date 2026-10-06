"""Endpoints del carrito de compras."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.cart import Cart, CartItem
from src.models.product import Product
from src.schemas.cart import CartItemCreate, CartItemResponse, CartItemUpdate, CartResponse
from src.services.auth.dependencies import get_current_user
from src.services.cart.service import compute_totals

router = APIRouter(prefix="/api/v1/cart", tags=["cart"])


def _get_or_create_cart(db: Session, user_id: str) -> Cart:
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def _cart_response(cart: Cart) -> CartResponse:
    items = [
        CartItemResponse(
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.product.effective_price,
            subtotal=item.subtotal,
        )
        for item in cart.items
    ]
    totals = compute_totals([i.subtotal for i in items])
    return CartResponse(user_id=cart.user_id, items=items, **totals)


@router.get("", response_model=CartResponse)
def get_cart(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    cart = _get_or_create_cart(db, user["sub"])
    return _cart_response(cart)


@router.post("/items", response_model=CartResponse, status_code=201)
def add_item(
    payload: CartItemCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    product = db.get(Product, payload.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    cart = _get_or_create_cart(db, user["sub"])
    existing = next((i for i in cart.items if i.product_id == payload.product_id), None)
    new_qty = (existing.quantity if existing else 0) + payload.quantity
    if product.stock == 0:
        raise HTTPException(status_code=409, detail="Producto sin stock")
    if new_qty > product.stock:
        raise HTTPException(status_code=409, detail="Stock insuficiente")
    if existing:
        existing.quantity = new_qty
    else:
        cart.items.append(CartItem(product_id=product.id, quantity=payload.quantity))
    db.commit()
    db.refresh(cart)
    return _cart_response(cart)


@router.patch("/items/{product_id}", response_model=CartResponse)
def update_item(
    product_id: str,
    payload: CartItemUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    cart = _get_or_create_cart(db, user["sub"])
    item = next((i for i in cart.items if i.product_id == product_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Ítem no encontrado en el carrito")
    if payload.quantity == 0:
        cart.items.remove(item)
    else:
        product = db.get(Product, product_id)
        if product and payload.quantity > product.stock:
            raise HTTPException(status_code=409, detail="Stock insuficiente")
        item.quantity = payload.quantity
    db.commit()
    db.refresh(cart)
    return _cart_response(cart)


@router.delete("/items/{product_id}", response_model=CartResponse)
def remove_item(
    product_id: str,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    cart = _get_or_create_cart(db, user["sub"])
    item = next((i for i in cart.items if i.product_id == product_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Ítem no encontrado en el carrito")
    cart.items.remove(item)
    db.commit()
    db.refresh(cart)
    return _cart_response(cart)
