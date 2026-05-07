"""
Задача 11.2 — Асинхронные тесты с pytest-asyncio

In-memory хранилище заметок.

Эндпоинты:
  POST   /notes          — создать заметку (201; 409 если title уже существует)
  GET    /notes/{title}  — получить заметку (404 если нет)
  DELETE /notes/{title}  — удалить заметку  (404 если нет)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Task 11.2 — Async Testing")

notes_db: dict[str, dict] = {}


class NoteCreate(BaseModel):
    title: str
    content: str


class NoteResponse(BaseModel):
    title: str
    content: str


@app.post("/notes", response_model=NoteResponse, status_code=201)
def create_note(note: NoteCreate):
    if note.title in notes_db:
        raise HTTPException(status_code=409, detail=f"Note '{note.title}' already exists.")
    notes_db[note.title] = note.model_dump()
    return notes_db[note.title]


@app.get("/notes/{title}", response_model=NoteResponse)
def get_note(title: str):
    if title not in notes_db:
        raise HTTPException(status_code=404, detail=f"Note '{title}' not found.")
    return notes_db[title]


@app.delete("/notes/{title}")
def delete_note(title: str):
    if title not in notes_db:
        raise HTTPException(status_code=404, detail=f"Note '{title}' not found.")
    del notes_db[title]
    return {"message": f"Note '{title}' deleted."}
