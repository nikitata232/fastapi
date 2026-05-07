# KR4 — FastAPI: Миграции, Ошибки, Тесты

## Установка зависимостей

```bash
pip install -r requirements.txt
```

---

## Задача 9.1 — Миграции с Alembic

### Структура
```
9.1/
├── app/
│   ├── database.py          # SQLAlchemy engine + Base
│   ├── models.py            # Модель Product
│   └── main.py              # FastAPI приложение
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 001_create_products.py   # Создание таблицы (id, title, price, count)
│       └── 002_add_description.py  # Добавление поля description
├── alembic.ini
└── seed_data.py
```

### Запуск
```bash
cd 9.1

# Применить первую миграцию (создать таблицу)
alembic upgrade 001

# Применить вторую миграцию (добавить description)
alembic upgrade 002
# или сразу все:
alembic upgrade head

# Откат до первой миграции
alembic downgrade 001

# Загрузить тестовые данные
python seed_data.py

# Запустить сервер
uvicorn app.main:app --reload
```

**Эндпоинты:** `POST /products` | `GET /products` | `GET /products/{id}`

---

## Задача 10.1 — Кастомная обработка ошибок

```bash
cd 10.1
uvicorn task_10_1:app --reload
```

**Исключения:**
- `ItemNotFoundException` → 404
- `OutOfStockException`   → 409

**Эндпоинты:**
- `GET  /items/{item_id}`      — получить товар
- `POST /items/{item_id}/buy`  — купить товар

**Тест:**
```bash
# Товар не найден
curl http://localhost:8000/items/99

# Товар не в наличии (id=2, count=0)
curl -X POST http://localhost:8000/items/2/buy

# Успешная покупка (id=1)
curl -X POST http://localhost:8000/items/1/buy
```

---

## Задача 10.2 — Валидация запросов

```bash
cd 10.2
uvicorn task_10_2:app --reload
```

**Эндпоинт:** `POST /users`

**Тест валидных данных:**
```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"username":"ivan","age":25,"email":"ivan@mail.ru","password":"secret123","phone":"+79161234567"}'
```

**Тест невалидных данных (422):**
```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"username":"ab","age":15,"email":"not-email","password":"12","phone":"89161234567"}'
```

---

## Задача 11.1 — Unit-тесты с pytest

```bash
cd 11.1
pytest test_task_11_1.py -v
```

Тесты покрывают регистрацию, получение и удаление пользователей через `TestClient`.

---

## Задача 11.2 — Асинхронные тесты с pytest-asyncio

```bash
cd 11.2
pytest test_task_11_2.py -v
```

Тесты используют `httpx.AsyncClient` + `ASGITransport` и `Faker` для генерации данных.
