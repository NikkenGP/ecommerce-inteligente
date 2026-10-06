"""Esquemas del catálogo de productos."""

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    category: str
    brand: str
    rating: float = Field(default=0.0, ge=0, le=5)
    on_sale: bool = False
    sale_price: float | None = Field(default=None, gt=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = None
    price: float | None = Field(default=None, gt=0)
    stock: int | None = Field(default=None, ge=0)
    category: str | None = None
    brand: str | None = None
    rating: float | None = Field(default=None, ge=0, le=5)
    on_sale: bool | None = None
    sale_price: float | None = Field(default=None, gt=0)


class StockUpdate(BaseModel):
    delta: int


class ProductResponse(ProductBase):
    id: str

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    page: int
    page_size: int
    total: int
