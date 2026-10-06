"""Endpoints del catálogo de productos."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.product import Product, StockAudit
from src.schemas.product import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
    StockUpdate,
)
from src.services.auth.dependencies import get_current_user, require_role

router = APIRouter(prefix="/api/v1/products", tags=["catalog"])


@router.get("", response_model=ProductListResponse)
def list_products(
    category: str | None = None,
    brand: str | None = None,
    on_sale: bool | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Product)
    if category:
        query = query.filter(Product.category == category)
    if brand:
        query = query.filter(Product.brand == brand)
    if on_sale is not None:
        query = query.filter(Product.on_sale == on_sale)
    total = query.count()
    items = (
        query.order_by(Product.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return ProductListResponse(items=items, page=page, page_size=page_size, total=total)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: str, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail={"code": "PRODUCT_NOT_FOUND", "message": "Producto no encontrado"})
    return product


@router.post("", response_model=ProductResponse, status_code=201)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_role("Administrador")),
):
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: str,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_role("Administrador")),
):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail={"code": "PRODUCT_NOT_FOUND", "message": "Producto no encontrado"})
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@router.patch("/{product_id}/stock", response_model=ProductResponse)
def update_stock(
    product_id: str,
    payload: StockUpdate,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_role("Administrador")),
):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail={"code": "PRODUCT_NOT_FOUND", "message": "Producto no encontrado"})
    new_stock = product.stock + payload.delta
    if new_stock < 0:
        raise HTTPException(status_code=422, detail="El stock no puede ser negativo")
    product.stock = new_stock
    db.add(StockAudit(product_id=product.id, delta=payload.delta, admin_id=admin["sub"]))
    db.commit()
    db.refresh(product)
    return product
