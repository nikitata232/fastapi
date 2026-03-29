from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from typing import List

app = FastAPI()

feedbacks: List["Feedback"] = []

class Feedback(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    message: str = Field(..., min_length=10, max_length=500)

    @validator("message")
    def no_bad_words(cls, v):
        forbidden_words = ["кринж", "рофл", "вайб"]
        # проверяем в нижнем регистре
        if any(word in v.lower() for word in forbidden_words):
            raise ValueError("Использование недопустимых слов")
        return v

@app.post("/feedback")
async def create_feedback(feedback: Feedback):
    feedbacks.append(feedback)
    return {"message": f"Спасибо, {feedback.name}! Ваш отзыв сохранён."}

@app.get("/feedbacks", response_model=List[Feedback])
async def get_feedbacks():
    return feedbacks