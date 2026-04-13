"""
Задача 6.1 — Базовая HTTP-аутентификация
GET /login защищён через HTTP Basic Auth.
"""

import secrets
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI(title="Task 6.1 — Basic HTTP Auth")

security = HTTPBasic()

# Хранилище пользователей (для демонстрации)
USERS = {
    "admin": "secret123",
    "user1": "password",
}


def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    stored_password = USERS.get(credentials.username)
    if not stored_password or not secrets.compare_digest(
        credentials.password.encode("utf-8"),
        stored_password.encode("utf-8"),
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/login")
def login(username: str = Depends(authenticate)):
    return {"message": "You got my secret, welcome", "user": username}
