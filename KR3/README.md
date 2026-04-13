# FastAPI — Контрольная работа №3

Все задания выполнены в виде отдельных файлов, каждый запускается независимо.

## Установка зависимостей

```bash
pip install -r requirements.txt
```

Скопируй `.env.example` в `.env` и задай свои значения:

```bash
cp .env.example .env
```

---

## Задача 6.1 — Basic HTTP Authentication

```bash
uvicorn task_6_1:app --reload
```

| Метод | URL | Описание |
|-------|-----|----------|
| GET | /login | Вход с Basic Auth |

Тест:
```bash
curl -u admin:secret123 http://localhost:8000/login
```

---

## Задача 6.2 — Secure Auth с bcrypt

```bash
uvicorn task_6_2:app --reload
```

| Метод | URL | Описание |
|-------|-----|----------|
| POST | /register | Регистрация (JSON) |
| GET  | /login    | Вход с Basic Auth |

Тест:
```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"correctpass"}'

curl -u user1:correctpass http://localhost:8000/login
```

---

## Задача 6.3 — Контроль доступа к документации

```bash
MODE=DEV DOCS_USER=admin DOCS_PASSWORD=secret uvicorn task_6_3:app --reload
# или
MODE=PROD uvicorn task_6_3:app --reload
```

В режиме **DEV**: `/docs` и `/openapi.json` защищены Basic Auth, `/redoc` скрыт.
В режиме **PROD**: все маршруты документации возвращают 404.

Тест (DEV):
```bash
curl -u admin:secret http://localhost:8000/docs
```

---

## Задача 6.4 — JWT Authentication

```bash
uvicorn task_6_4:app --reload
```

| Метод | URL | Описание |
|-------|-----|----------|
| POST | /login | Получить JWT token |
| GET  | /protected_resource | Доступ по токену |

Тест:
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"alicepassword"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/protected_resource
```

---

## Задача 6.5 — JWT + Регистрация + Rate Limiting

```bash
uvicorn task_6_5:app --reload
```

| Метод | URL | Ограничение | Описание |
|-------|-----|-------------|----------|
| POST | /register | 1 req/min | Регистрация (201 / 409) |
| POST | /login    | 5 req/min | Вход, получить токен |
| GET  | /protected_resource | — | Защищённый ресурс |

Тест:
```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"nikita","password":"mypassword"}'

TOKEN=$(curl -s -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"nikita","password":"mypassword"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/protected_resource
```

---

## Задача 7.1 — Role-Based Access Control

```bash
uvicorn task_7_1:app --reload
```

Предустановленные пользователи:

| Пользователь | Пароль | Роль |
|---|---|---|
| alice | adminpass | admin |
| bob | userpass | user |
| charlie | guestpass | guest |

| Метод | URL | Минимальная роль |
|-------|-----|-----------------|
| GET | /protected_resource | guest |
| GET | /items | guest |
| GET | /items/{id} | guest |
| POST | /items | user |
| PUT | /items/{id} | user |
| DELETE | /items/{id} | admin |

Тест:
```bash
# admin — может всё
curl -u alice:adminpass -X DELETE http://localhost:8000/items/1

# guest — только чтение
curl -u charlie:guestpass http://localhost:8000/items

# guest пытается удалить — 403
curl -u charlie:guestpass -X DELETE http://localhost:8000/items/1
```

---

## Задача 8.1 — Регистрация в SQLite

```bash
uvicorn task_8_1:app --reload
```

| Метод | URL | Описание |
|-------|-----|----------|
| POST | /register | Создать пользователя |
| GET  | /users    | Список пользователей |

Тест:
```bash
curl -X POST http://127.0.0.1:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test_user","password":"12345"}'

curl http://127.0.0.1:8000/users
```

---

## Задача 8.2 — CRUD Todo

```bash
uvicorn task_8_2:app --reload
```

| Метод | URL | Описание |
|-------|-----|----------|
| POST   | /todos       | Создать todo (201) |
| GET    | /todos       | Все todos |
| GET    | /todos/{id}  | Одна запись |
| PUT    | /todos/{id}  | Обновить |
| DELETE | /todos/{id}  | Удалить |

Тест:
```bash
# Создать
curl -X POST http://localhost:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy groceries","description":"Milk, eggs, bread"}'

# Получить
curl http://localhost:8000/todos/1

# Обновить
curl -X PUT http://localhost:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed":true}'

# Удалить
curl -X DELETE http://localhost:8000/todos/1
```
