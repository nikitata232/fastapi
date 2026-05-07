"""
Задача 9.1 — Миграции базы данных с Alembic

Модель Product (после применения обеих миграций):
  id          INTEGER PRIMARY KEY AUTOINCREMENT
  title       VARCHAR(255) NOT NULL
  price       FLOAT       NOT NULL
  count       INTEGER     NOT NULL  DEFAULT 0
  description TEXT        NOT NULL  DEFAULT ''   ← добавлено миграцией 002

Запуск:
  alembic upgrade head          # применить обе миграции
  python seed_data.py           # загрузить тестовые данные
  uvicorn app.main:app --reload
"""

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .database import SessionLocal
from . import models

app = FastAPI(title="Task 9.1 — Alembic Migrations")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ProductCreate(BaseModel):
    title: str
    price: float
    count: int = 0
    description: str = ""


class ProductResponse(BaseModel):
    id: int
    title: str
    price: float
    count: int
    description: str

    model_config = {"from_attributes": True}


@app.post("/products", response_model=ProductResponse, status_code=201)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@app.get("/products", response_model=list[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()


@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    return product
