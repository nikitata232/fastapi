"""
Задача 8.2 — Полный CRUD для ресурса Todo (SQLite)

Модель Todo:
  id          INTEGER PRIMARY KEY AUTOINCREMENT
  title       TEXT    NOT NULL
  description TEXT    NOT NULL
  completed   BOOLEAN DEFAULT 0

Эндпоинты:
  POST   /todos          — создать todo (201)
  GET    /todos          — получить все todos
  GET    /todos/{id}     — получить одну запись (404 если нет)
  PUT    /todos/{id}     — обновить запись (404 если нет)
  DELETE /todos/{id}     — удалить запись (404 если нет)
"""

import sqlite3
from contextlib import contextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Task 8.2 — CRUD Todo with SQLite")

DB_PATH = "task_8_2_todos.db"


# ---------- Database init ----------

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT    NOT NULL,
                description TEXT    NOT NULL,
                completed   BOOLEAN NOT NULL DEFAULT 0
            )
            """
        )
        conn.commit()


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


init_db()


# ---------- Models ----------

class TodoCreate(BaseModel):
    title: str
    description: str
    completed: bool = False


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool


# ---------- Helpers ----------

def row_to_dict(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "completed": bool(row["completed"]),
    }


def get_todo_or_404(conn: sqlite3.Connection, todo_id: int) -> dict:
    row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"Todo with id={todo_id} not found")
    return row_to_dict(row)


# ---------- Endpoints ----------

@app.post("/todos", status_code=201, response_model=TodoResponse)
def create_todo(body: TodoCreate):
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO todos (title, description, completed) VALUES (?, ?, ?)",
            (body.title, body.description, int(body.completed)),
        )
        conn.commit()
        new_id = cursor.lastrowid
    return {"id": new_id, "title": body.title, "description": body.description, "completed": body.completed}


@app.get("/todos", response_model=list[TodoResponse])
def list_todos():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM todos").fetchall()
    return [row_to_dict(r) for r in rows]


@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int):
    with get_db() as conn:
        return get_todo_or_404(conn, todo_id)


@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, body: TodoUpdate):
    with get_db() as conn:
        existing = get_todo_or_404(conn, todo_id)

        new_title = body.title if body.title is not None else existing["title"]
        new_desc = body.description if body.description is not None else existing["description"]
        new_completed = body.completed if body.completed is not None else existing["completed"]

        conn.execute(
            "UPDATE todos SET title = ?, description = ?, completed = ? WHERE id = ?",
            (new_title, new_desc, int(new_completed), todo_id),
        )
        conn.commit()

    return {"id": todo_id, "title": new_title, "description": new_desc, "completed": new_completed}


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    with get_db() as conn:
        get_todo_or_404(conn, todo_id)  # 404 если не существует
        conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        conn.commit()
    return {"message": f"Todo {todo_id} deleted successfully"}
