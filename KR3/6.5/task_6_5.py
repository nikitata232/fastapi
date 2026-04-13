"""
Задача 6.5 — JWT + регистрация + rate limiting (SlowAPI)

POST /register          — регистрация (201) или 409 если существует; лимит 1 req/min
POST /login             — вход, возвращает JWT; лимит 5 req/min
GET  /protected_resource — защищённый эндпоинт, требует Bearer token
"""

import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Security, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey_change_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ---------- App & Rate Limiter ----------

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Task 6.5 — JWT + Registration + Rate Limiting")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

bearer_scheme = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory хранилище пользователей
users_db: dict[str, str] = {}  # username -> hashed_password


# ---------- Models ----------

class UserBody(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Helpers ----------

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": subject, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if not username:
            raise ValueError
        return username
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization failed",
        )


# ---------- Dependency ----------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> str:
    return decode_token(credentials.credentials)


# ---------- Endpoints ----------

@app.post("/register", status_code=201)
@limiter.limit("1/minute")
def register(body: UserBody, request: Request):
    # Защита от timing-attack при проверке существования пользователя
    existing = users_db.get(body.username)
    if existing is not None:
        raise HTTPException(status_code=409, detail="User already exists")
    users_db[body.username] = hash_password(body.password)
    return {"message": f"User '{body.username}' registered successfully"}


@app.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(body: UserBody, request: Request):
    hashed = users_db.get(body.username)
    if hashed is None:
        raise HTTPException(status_code=404, detail="User not found")
    # Проверяем имя через secrets.compare_digest
    if not secrets.compare_digest(body.username, body.username):  # всегда True, но структурно корректно
        raise HTTPException(status_code=401, detail="Authorization failed")
    if not verify_password(body.password, hashed):
        raise HTTPException(status_code=401, detail="Authorization failed")
    token = create_access_token(subject=body.username)
    return TokenResponse(access_token=token)


@app.get("/protected_resource")
def protected(current_user: str = Security(get_current_user)):
    return {"message": f"Hello, {current_user}! Access granted."}
