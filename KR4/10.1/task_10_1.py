"""
Задача 10.1 — Кастомная обработка ошибок

Два кастомных исключения:
  - ItemNotFoundException  → 404
  - OutOfStockException    → 409

Обработчики возвращают стандартизированную Pydantic-модель ErrorResponse.

Эндпоинты:
  GET  /items/{item_id}      — получить товар (ItemNotFoundException если нет)
  POST /items/{item_id}/buy  — купить товар   (ItemNotFoundException если нет,
                                               OutOfStockException если count = 0)
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="Task 10.1 — Custom Error Handling")


# ---------- Custom Exceptions ----------

class ItemNotFoundException(Exception):
    def __init__(self, item_id: int) -> None:
        self.item_id = item_id


class OutOfStockException(Exception):
    def __init__(self, item_id: int) -> None:
        self.item_id = item_id


# ---------- Error Response Model ----------

class ErrorResponse(BaseModel):
    error: str
    detail: str
    status_code: int


# ---------- Exception Handlers ----------

@app.exception_handler(ItemNotFoundException)
async def item_not_found_handler(request: Request, exc: ItemNotFoundException) -> JSONResponse:
    body = ErrorResponse(
        error="ItemNotFound",
        detail=f"Item with id={exc.item_id} does not exist.",
        status_code=404,
    )
    return JSONResponse(status_code=404, content=body.model_dump())


@app.exception_handler(OutOfStockException)
async def out_of_stock_handler(request: Request, exc: OutOfStockException) -> JSONResponse:
    body = ErrorResponse(
        error="OutOfStock",
        detail=f"Item with id={exc.item_id} is out of stock.",
        status_code=409,
    )
    return JSONResponse(status_code=409, content=body.model_dump())


# ---------- In-memory Storage ----------

items: dict[int, dict] = {
    1: {"id": 1, "title": "Laptop",   "price": 999.99, "count": 5},
    2: {"id": 2, "title": "Mouse",    "price": 29.99,  "count": 0},
    3: {"id": 3, "title": "Keyboard", "price": 59.99,  "count": 12},
}


# ---------- Response Model ----------

class ItemResponse(BaseModel):
    id: int
    title: str
    price: float
    count: int


# ---------- Endpoints ----------

@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int):
    if item_id not in items:
        raise ItemNotFoundException(item_id)
    return items[item_id]


@app.post("/items/{item_id}/buy", response_model=ItemResponse)
def buy_item(item_id: int):
    if item_id not in items:
        raise ItemNotFoundException(item_id)
    item = items[item_id]
    if item["count"] == 0:
        raise OutOfStockException(item_id)
    item["count"] -= 1
    return item
