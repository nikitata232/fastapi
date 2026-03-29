from typing import Optional, Annotated
from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: Optional[Annotated[int, Field(gt=0)]] = None
    is_subscribed: Optional[bool] = False

app = FastAPI()

@app.post("/create_user")
async def create_user(user: UserCreate):
    return user