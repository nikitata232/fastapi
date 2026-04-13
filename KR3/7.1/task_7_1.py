"""
Задача 7.1 — Role-Based Access Control (RBAC)

Роли: admin, user, guest.
- admin  → полный CRUD (читать, создавать, обновлять, удалять)
- user   → чтение и обновление
- guest  → только чтение

Эндпоинты:
  GET    /protected_resource  — доступен всем аутентифицированным
  POST   /items               — только admin и user (создание)
  PUT    /items/{item_id}     — только admin и user (обновление)
  DELETE /items/{item_id}     — только admin (удаление)

Аутентификация: HTTP Basic Auth.
Пользователи и роли хранятся в словарях (in-memory).
"""

import secrets
from functools import wraps
from typing import Callable

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

app = FastAPI(title="Task 7.1 — Role-Based Access Control")
security = HTTPBasic()

# ---------- In-memory хранилища ----------

USERS: dict[str, str] = {
    "alice": "adminpass",
    "bob": "userpass",
    "charlie": "guestpass",
}

ROLES: dict[str, str] = {
    "alice": "admin",
    "bob": "user",
    "charlie": "guest",
}

ITEMS: dict[int, dict] = {
    1: {"id": 1, "name": "Item One"},
    2: {"id": 2, "name": "Item Two"},
}
_next_id = 3


# ---------- Pydantic Models ----------

class ItemCreate(BaseModel):
    name: str


class ItemUpdate(BaseModel):
    name: str


# ---------- Auth dependency ----------

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    stored_password = USERS.get(credentials.username)
    if not stored_password or not secrets.compare_digest(
        credentials.password.encode(), stored_password.encode()
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def get_current_role(username: str = Depends(get_current_user)) -> tuple[str, str]:
    role = ROLES.get(username, "guest")
    return username, role


# ---------- Role checker ----------

ROLE_HIERARCHY = {"admin": 3, "user": 2, "guest": 1}

PERMISSIONS: dict[str, list[str]] = {
    "admin": ["read", "create", "update", "delete"],
    "user": ["read", "create", "update"],
    "guest": ["read"],
}


def require_permission(permission: str):
    """Фабрика зависимостей — проверяет, есть ли у пользователя нужное право."""
    def dependency(user_role: tuple[str, str] = Depends(get_current_role)):
        username, role = user_role
        if permission not in PERMISSIONS.get(role, []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' does not have permission: {permission}",
            )
        return username, role
    return dependency


# ---------- Endpoints ----------

@app.get("/protected_resource")
def protected_resource(user_role: tuple[str, str] = Depends(get_current_role)):
    username, role = user_role
    return {
        "message": f"Hello, {username}!",
        "role": role,
        "permissions": PERMISSIONS[role],
    }


@app.get("/items")
def list_items(user_role: tuple[str, str] = Depends(require_permission("read"))):
    return list(ITEMS.values())


@app.get("/items/{item_id}")
def get_item(
    item_id: int,
    user_role: tuple[str, str] = Depends(require_permission("read")),
):
    item = ITEMS.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.post("/items", status_code=201)
def create_item(
    body: ItemCreate,
    user_role: tuple[str, str] = Depends(require_permission("create")),
):
    global _next_id
    item = {"id": _next_id, "name": body.name}
    ITEMS[_next_id] = item
    _next_id += 1
    return item


@app.put("/items/{item_id}")
def update_item(
    item_id: int,
    body: ItemUpdate,
    user_role: tuple[str, str] = Depends(require_permission("update")),
):
    if item_id not in ITEMS:
        raise HTTPException(status_code=404, detail="Item not found")
    ITEMS[item_id]["name"] = body.name
    return ITEMS[item_id]


@app.delete("/items/{item_id}")
def delete_item(
    item_id: int,
    user_role: tuple[str, str] = Depends(require_permission("delete")),
):
    if item_id not in ITEMS:
        raise HTTPException(status_code=404, detail="Item not found")
    del ITEMS[item_id]
    return {"message": f"Item {item_id} deleted successfully"}
