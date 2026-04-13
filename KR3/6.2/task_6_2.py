"""
Задача 6.2 — Аутентификация с хешированием паролей (bcrypt)
Модели: UserBase, User, UserInDB.
POST /register — регистрация пользователя
GET  /login    — вход с проверкой хеша
"""

import secrets
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from pydantic import BaseModel

app = FastAPI(title="Task 6.2 — Secure Auth with Hashing")

security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory хранилище пользователей
db: dict[str, dict] = {}


# ---------- Pydantic Models ----------

class UserBase(BaseModel):
    username: str


class User(UserBase):
    password: str


class UserInDB(UserBase):
    hashed_password: str


# ---------- Helpers ----------

def get_user(username: str) -> UserInDB | None:
    entry = db.get(username)
    if entry:
        return UserInDB(**entry)
    return None


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


# ---------- Dependency ----------

def auth_user(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    user = get_user(credentials.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    # secrets.compare_digest защищает от timing-attack
    plain_bytes = credentials.password.encode("utf-8")
    # Используем bcrypt verify через passlib — он сам защищён от timing-attack
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    # Дополнительная проверка имени через secrets.compare_digest
    if not secrets.compare_digest(
        credentials.username.encode("utf-8"),
        user.username.encode("utf-8"),
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user.username


# ---------- Endpoints ----------

@app.post("/register", status_code=201)
def register(user: User):
    if user.username in db:
        raise HTTPException(status_code=409, detail="User already exists")
    db[user.username] = {
        "username": user.username,
        "hashed_password": hash_password(user.password),
    }
    return {"message": f"User '{user.username}' registered successfully"}


@app.get("/login")
def login(username: str = Depends(auth_user)):
    return {"message": f"You got my secret, welcome {username}"}
