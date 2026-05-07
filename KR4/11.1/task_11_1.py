"""
Задача 11.1 — Unit-тесты с pytest

In-memory хранилище пользователей.

Эндпоинты:
  POST   /users              — регистрация (201; 409 если username занят)
  GET    /users/{username}   — получить пользователя (404 если нет)
  DELETE /users/{username}   — удалить пользователя  (404 если нет)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Task 11.1 — Unit Testing")

users_db: dict[str, dict] = {}


class UserCreate(BaseModel):
    username: str
    email: str


class UserResponse(BaseModel):
    username: str
    email: str


@app.post("/users", response_model=UserResponse, status_code=201)
def register_user(user: UserCreate):
    if user.username in users_db:
        raise HTTPException(status_code=409, detail=f"User '{user.username}' already exists.")
    users_db[user.username] = user.model_dump()
    return users_db[user.username]


@app.get("/users/{username}", response_model=UserResponse)
def get_user(username: str):
    if username not in users_db:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found.")
    return users_db[username]


@app.delete("/users/{username}")
def delete_user(username: str):
    if username not in users_db:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found.")
    del users_db[username]
    return {"message": f"User '{username}' deleted."}
