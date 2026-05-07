"""
Unit-тесты для task_11_1.py

Покрытие:
  POST   /users              — успех, дубликат
  GET    /users/{username}   — успех, не найден
  DELETE /users/{username}   — успех, удалённый недоступен, не найден
"""

import pytest
from fastapi.testclient import TestClient

from task_11_1 import app, users_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_storage():
    users_db.clear()
    yield
    users_db.clear()


class TestRegisterUser:
    def test_register_success(self):
        resp = client.post("/users", json={"username": "alice", "email": "alice@example.com"})
        assert resp.status_code == 201
        assert resp.json() == {"username": "alice", "email": "alice@example.com"}

    def test_register_stores_user(self):
        client.post("/users", json={"username": "bob", "email": "bob@example.com"})
        assert "bob" in users_db

    def test_register_duplicate_returns_409(self):
        client.post("/users", json={"username": "carol", "email": "carol@example.com"})
        resp = client.post("/users", json={"username": "carol", "email": "carol2@example.com"})
        assert resp.status_code == 409
        assert "already exists" in resp.json()["detail"]


class TestGetUser:
    def test_get_existing_user(self):
        client.post("/users", json={"username": "dave", "email": "dave@example.com"})
        resp = client.get("/users/dave")
        assert resp.status_code == 200
        assert resp.json()["username"] == "dave"
        assert resp.json()["email"] == "dave@example.com"

    def test_get_nonexistent_returns_404(self):
        resp = client.get("/users/nobody")
        assert resp.status_code == 404
        assert "not found" in resp.json()["detail"]


class TestDeleteUser:
    def test_delete_existing_user(self):
        client.post("/users", json={"username": "eve", "email": "eve@example.com"})
        resp = client.delete("/users/eve")
        assert resp.status_code == 200
        assert "deleted" in resp.json()["message"]

    def test_delete_removes_from_storage(self):
        client.post("/users", json={"username": "frank", "email": "frank@example.com"})
        client.delete("/users/frank")
        assert "frank" not in users_db

    def test_deleted_user_returns_404_on_get(self):
        client.post("/users", json={"username": "grace", "email": "grace@example.com"})
        client.delete("/users/grace")
        resp = client.get("/users/grace")
        assert resp.status_code == 404

    def test_delete_nonexistent_returns_404(self):
        resp = client.delete("/users/ghost")
        assert resp.status_code == 404
        assert "not found" in resp.json()["detail"]
