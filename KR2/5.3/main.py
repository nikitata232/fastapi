from fastapi import FastAPI, Response, Request, HTTPException, status
from pydantic import BaseModel
from itsdangerous import Signer, BadSignature
import uuid
import time

app = FastAPI()

SECRET_KEY = "super-secret-key"
signer = Signer(SECRET_KEY)

SESSION_MAX_AGE = 300  # 5 минут в секундах
SESSION_RENEW_THRESHOLD_MIN = 180  # 3 минуты

fake_users_db = {
    "user123": {
        "id": str(uuid.uuid4()),
        "username": "user123",
        "password": "password123",
        "email": "user123@example.com"
    }
}

class LoginRequest(BaseModel):
    username: str
    password: str

def create_session_cookie(user_id: str):
    timestamp = int(time.time())
    data = f"{user_id}.{timestamp}"
    signed = signer.sign(data.encode()).decode()
    return signed

def parse_session_cookie(cookie_value: str):
    try:
        unsigned = signer.unsign(cookie_value.encode()).decode()
        user_id_str, timestamp_str = unsigned.split(".")
        return user_id_str, int(timestamp_str)
    except (BadSignature, ValueError):
        return None, None

@app.post("/login")
def login(data: LoginRequest, response: Response):
    user = fake_users_db.get(data.username)
    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    signed_cookie = create_session_cookie(user["id"])
    response.set_cookie(
        key="session_token",
        value=signed_cookie,
        httponly=True,
        secure=False,
        max_age=SESSION_MAX_AGE
    )
    return {"message": "Logged in"}

@app.get("/profile")
def profile(request: Request, response: Response):
    cookie = request.cookies.get("session_token")
    if not cookie:
        response.status_code = 401
        return {"message": "Session expired"}

    user_id, last_activity = parse_session_cookie(cookie)
    if not user_id or not last_activity:
        response.status_code = 401
        return {"message": "Invalid session"}

    now = int(time.time())
    elapsed = now - last_activity

    if elapsed >= SESSION_MAX_AGE:
        response.status_code = 401
        return {"message": "Session expired"}

    if SESSION_RENEW_THRESHOLD_MIN <= elapsed < SESSION_MAX_AGE:
        new_cookie = create_session_cookie(user_id)
        response.set_cookie(
            key="session_token",
            value=new_cookie,
            httponly=True,
            secure=False,
            max_age=SESSION_MAX_AGE
        )

    user = None
    for u in fake_users_db.values():
        if u["id"] == user_id:
            user = u
            break

    if not user:
        response.status_code = 401
        return {"message": "Invalid session"}

    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"]
    }