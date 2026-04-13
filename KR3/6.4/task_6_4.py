"""
Задача 6.4 — JWT-аутентификация с PyJWT

POST /login            — принимает username/password, возвращает JWT access_token
GET  /protected_resource — требует валидный JWT в заголовке Authorization: Bearer <token>
"""

import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey_change_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(title="Task 6.4 — JWT Authentication")
bearer_scheme = HTTPBearer()

# Простая in-memory «БД» пользователей (логин: пароль)
FAKE_USERS = {
    "alice": "alicepassword",
    "bob": "bobpassword",
}


# ---------- Models ----------

class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- JWT helpers ----------

def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


# ---------- Dependency ----------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> str:
    payload = decode_token(credentials.credentials)
    username: str | None = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    return username


# ---------- Endpoints ----------

@app.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    stored = FAKE_USERS.get(body.username)
    if not stored or stored != body.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_access_token(subject=body.username)
    return TokenResponse(access_token=token)


@app.get("/protected_resource")
def protected_resource(current_user: str = Security(get_current_user)):
    return {"message": f"Hello, {current_user}! You have access to the protected resource."}
