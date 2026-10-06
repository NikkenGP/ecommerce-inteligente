"""Factories de datos de prueba."""

from src.models.product import Product


def sample_products() -> list[Product]:
    return [
        Product(name="Laptop Pro", price=1500.0, stock=10, category="electronics", brand="Acme", rating=4.5, on_sale=True, sale_price=1299.0),
        Product(name="Mouse Inalámbrico", price=25.0, stock=50, category="electronics", brand="Acme", rating=4.2),
        Product(name="Teclado Mecánico", price=80.0, stock=0, category="electronics", brand="Keyz", rating=4.6),
        Product(name="Silla Ergonómica", price=300.0, stock=5, category="furniture", brand="Comfy", rating=3.9),
        Product(name="Escritorio", price=450.0, stock=8, category="furniture", brand="Comfy", rating=4.1),
    ]


def seed_products(db) -> list[Product]:
    products = sample_products()
    for p in products:
        db.add(p)
    db.commit()
    for p in products:
        db.refresh(p)
    return products
