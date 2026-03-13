from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Feedback(BaseModel):
    name: str
    message: str

feedback_list: List[Feedback] = []

@app.get("/feedbacks", response_model=List[Feedback])
async def get_feedbacks():
    return feedback_list

@app.post("/feedback")
async def feedback(feedback: Feedback):
    feedback_list.append(feedback)
    return {"message": f"Feedback received. Thank you, {feedback.name}!"}