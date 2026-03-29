from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
class numbers(BaseModel):
    num1: int
    num2: int

@app.get("/")
async def root():
    return {"message": "Добро пожаловать в мое FastAPI приложение"}

@app.post("/add")
async def calculate(numbers: numbers):
    result = numbers.num1 + numbers.num2
    return {"result": result}
