"""Загружает тестовые данные в таблицу products.

Запускать после применения миграций:
  alembic upgrade head
  python seed_data.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models import Product

SAMPLE_PRODUCTS = [
    Product(title="Laptop", price=999.99, count=10, description="High-performance laptop"),
    Product(title="Mouse", price=29.99, count=50, description="Wireless optical mouse"),
    Product(title="Keyboard", price=59.99, count=30, description="Mechanical keyboard"),
    Product(title="Monitor", price=399.99, count=15, description="4K UHD monitor"),
    Product(title="Headphones", price=149.99, count=20, description="Noise-cancelling headphones"),
]


def seed() -> None:
    db = SessionLocal()
    try:
        for product in SAMPLE_PRODUCTS:
            db.add(product)
        db.commit()
        print(f"Seeded {len(SAMPLE_PRODUCTS)} products successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
