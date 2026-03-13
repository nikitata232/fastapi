# обновляем код в main.py
from fastapi import FastAPI
from starlette.responses import HTMLResponse

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Добро пожаловать в мое приложение FASTAPI!"}