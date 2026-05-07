"""
Асинхронные тесты для task_11_2.py

Используется:
  - pytest-asyncio       — запуск async-тестов
  - httpx.AsyncClient    — HTTP-клиент с ASGITransport
  - Faker                — генерация реалистичных тестовых данных

Покрытие:
  POST   /notes          — успех, дубликат
  GET    /notes/{title}  — успех, не найден
  DELETE /notes/{title}  — успех, удалённая недоступна, не найдена
"""

import pytest
import pytest_asyncio
from faker import Faker
from httpx import ASGITransport, AsyncClient

from task_11_2 import app, notes_db

fake = Faker()


@pytest.fixture(autouse=True)
def clear_storage():
    notes_db.clear()
    yield
    notes_db.clear()


@pytest_asyncio.fixture
async def ac():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


# ---------- POST /notes ----------

@pytest.mark.asyncio
async def test_create_note_success(ac: AsyncClient):
    title = fake.sentence(nb_words=4).rstrip(".")
    content = fake.paragraph()
    resp = await ac.post("/notes", json={"title": title, "content": content})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == title
    assert data["content"] == content


@pytest.mark.asyncio
async def test_create_note_duplicate_returns_409(ac: AsyncClient):
    title = fake.word()
    content = fake.sentence()
    await ac.post("/notes", json={"title": title, "content": content})
    resp = await ac.post("/notes", json={"title": title, "content": fake.sentence()})
    assert resp.status_code == 409
    assert "already exists" in resp.json()["detail"]


# ---------- GET /notes/{title} ----------

@pytest.mark.asyncio
async def test_get_existing_note(ac: AsyncClient):
    title = fake.word() + "_get"
    content = fake.sentence()
    await ac.post("/notes", json={"title": title, "content": content})
    resp = await ac.get(f"/notes/{title}")
    assert resp.status_code == 200
    assert resp.json()["content"] == content


@pytest.mark.asyncio
async def test_get_nonexistent_note_returns_404(ac: AsyncClient):
    resp = await ac.get(f"/notes/{fake.word()}_missing")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"]


# ---------- DELETE /notes/{title} ----------

@pytest.mark.asyncio
async def test_delete_existing_note(ac: AsyncClient):
    title = fake.word() + "_del"
    await ac.post("/notes", json={"title": title, "content": fake.sentence()})
    resp = await ac.delete(f"/notes/{title}")
    assert resp.status_code == 200
    assert "deleted" in resp.json()["message"]


@pytest.mark.asyncio
async def test_deleted_note_returns_404_on_get(ac: AsyncClient):
    title = fake.word() + "_gone"
    await ac.post("/notes", json={"title": title, "content": fake.sentence()})
    await ac.delete(f"/notes/{title}")
    resp = await ac.get(f"/notes/{title}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_note_returns_404(ac: AsyncClient):
    resp = await ac.delete(f"/notes/{fake.word()}_nonexistent")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"]
