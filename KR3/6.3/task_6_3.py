"""
Задача 6.3 — Контроль доступа к документации через переменную окружения MODE.

DEV  — /docs и /openapi.json защищены Basic Auth, /redoc скрыт.
PROD — /docs, /openapi.json, /redoc полностью скрыты (404).

Запуск:
  MODE=DEV  DOCS_USER=admin DOCS_PASSWORD=secret uvicorn task_6_3:app --reload
  MODE=PROD uvicorn task_6_3:app --reload
"""

import os
import secrets

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

load_dotenv()

MODE = os.getenv("MODE", "DEV").upper()
DOCS_USER = os.getenv("DOCS_USER", "admin")
DOCS_PASSWORD = os.getenv("DOCS_PASSWORD", "secret")

# В PROD режиме полностью отключаем встроенные /docs и /openapi.json
if MODE == "PROD":
    app = FastAPI(
        title="Task 6.3 — Docs Access Control",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
else:
    # В DEV встроенные маршруты тоже отключаем — управляем сами
    app = FastAPI(
        title="Task 6.3 — Docs Access Control",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )

security = HTTPBasic()


def check_docs_auth(credentials: HTTPBasicCredentials = Depends(security)):
    """Проверка Basic Auth для доступа к документации."""
    correct_user = secrets.compare_digest(
        credentials.username.encode("utf-8"),
        DOCS_USER.encode("utf-8"),
    )
    correct_pass = secrets.compare_digest(
        credentials.password.encode("utf-8"),
        DOCS_PASSWORD.encode("utf-8"),
    )
    if not (correct_user and correct_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access denied",
            headers={"WWW-Authenticate": "Basic"},
        )


# ---------- Маршруты документации ----------

if MODE == "DEV":

    @app.get("/docs", include_in_schema=False)
    def get_docs(credentials: HTTPBasicCredentials = Depends(check_docs_auth)):
        return get_swagger_ui_html(openapi_url="/openapi.json", title="API Docs")

    @app.get("/openapi.json", include_in_schema=False)
    def get_openapi_schema(credentials: HTTPBasicCredentials = Depends(check_docs_auth)):
        return JSONResponse(
            get_openapi(title=app.title, version="1.0.0", routes=app.routes)
        )

    # /redoc — скрыт (не добавляем маршрут вообще)

else:  # PROD

    @app.get("/docs", include_in_schema=False)
    def docs_404():
        raise HTTPException(status_code=404, detail="Not found")

    @app.get("/openapi.json", include_in_schema=False)
    def openapi_404():
        raise HTTPException(status_code=404, detail="Not found")

    @app.get("/redoc", include_in_schema=False)
    def redoc_404():
        raise HTTPException(status_code=404, detail="Not found")


# ---------- Бизнес-эндпоинты ----------

@app.get("/")
def root():
    return {"message": "App is running", "mode": MODE}


@app.get("/items/{item_id}")
def get_item(item_id: int):
    return {"item_id": item_id, "name": f"Item #{item_id}"}
