"""
Задача 10.2 — Валидация запросов с кастомными ошибками

POST /users принимает тело:
  username : str   (3–50 символов)
  age      : int   (> 18)
  email    : str   (корректный email)
  password : str   (8–16 символов)
  phone    : str   (формат +7XXXXXXXXXX — 10 цифр после +7)

Кастомный обработчик RequestValidationError возвращает читаемый JSON.
"""

import re

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field, field_validator

app = FastAPI(title="Task 10.2 — Request Validation")


# ---------- Custom Validation Error Handler ----------

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = []
    for err in exc.errors():
        field = ".".join(str(loc) for loc in err["loc"] if loc != "body")
        errors.append({"field": field, "message": err["msg"]})
    return JSONResponse(
        status_code=422,
        content={"error": "ValidationError", "detail": errors},
    )


# ---------- Models ----------

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    age: int = Field(gt=18, description="Возраст строго больше 18")
    email: EmailStr
    password: str = Field(min_length=8, max_length=16)
    phone: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.fullmatch(r"\+7\d{10}", v):
            raise ValueError("Phone must be in format +7XXXXXXXXXX (10 digits after +7)")
        return v


class UserResponse(BaseModel):
    username: str
    age: int
    email: str
    phone: str


# ---------- Endpoint ----------

@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate):
    return UserResponse(
        username=user.username,
        age=user.age,
        email=user.email,
        phone=user.phone,
    )
