from fastapi import FastAPI
from models import User

app = FastAPI()

user = User(
    name="Nikita Limonov",
    id=1
)
@app.get("/users")
async def users():
    return user
@app.get("/")
async def root():
    return{"message": "Добро пожаловать в мое приложение"}