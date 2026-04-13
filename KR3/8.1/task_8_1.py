"""
Задача 8.1 — Регистрация пользователей с сохранением в SQLite

Таблица users:
  id       INTEGER PRIMARY KEY AUTOINCREMENT
  username TEXT
  password TEXT

POST /register — создаёт нового пользователя в БД.
GET  /users    — список всех пользователей (без паролей).
"""

import sqlite3
from contextlib import contextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Task 8.1 — SQLite User Registration")

DB_PATH = "task_8_1.db"


# ---------- database.py (inline) ----------

def init_db():
    """Создаём таблицу users при старте приложения."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT    NOT NULL,
                password TEXT    NOT NULL
            )
            """
        )
        conn.commit()


@contextmanager
def get_db_connection():
    """Контекстный менеджер для соединения с БД."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# Инициализируем БД при загрузке модуля
init_db()


# ---------- Models ----------

class User(BaseModel):
    username: str
    password: str


# ---------- Endpoints ----------

@app.post("/register", status_code=201)
def register(user: User):
    with get_db_connection() as conn:
        # Проверяем, не существует ли уже такой пользователь
        existing = conn.execute(
            "SELECT id FROM users WHERE username = ?", (user.username,)
        ).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="User already exists")

        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (user.username, user.password),
        )
        conn.commit()

    return {"message": "User registered successfully!"}


@app.get("/users")
def list_users():
    """Возвращает список пользователей (без паролей)."""
    with get_db_connection() as conn:
        rows = conn.execute("SELECT id, username FROM users").fetchall()
    return [{"id": row["id"], "username": row["username"]} for row in rows]
