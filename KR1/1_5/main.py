from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    name: str
    age: int

@app.post("/user")
async def user(user: User):
    is_adult = user.age >= 18
    return {
        "name": user.name,
        "age": user.age,
        "is_adult": is_adult 
    }

