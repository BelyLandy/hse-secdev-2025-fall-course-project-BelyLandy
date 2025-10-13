````markdown
# Idea Backlog

Небольшой сервис для ведения каталога идей: CRUD, сортировка по `score = impact / effort`, доступ только владельцу (или роли `admin`). Стек: FastAPI + SQLite.

## Запуск локально

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows (Git Bash):
source .venv/Scripts/activate

pip install -r requirements.txt
# при необходимости для разработки:
pip install -U ruff black isort pre-commit pytest

pre-commit install
uvicorn app.main:app --reload
````

Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
База: файл `app.db` в корне проекта.

## Эндпойнты

Доменные:

* `POST   /api/v1/items` - создать
  Заголовки: `X-User-Id: <user>` (обязателен), опционально `X-User-Role: admin`
* `GET    /api/v1/items/{id}` - получить (владелец или `admin`)
* `PATCH  /api/v1/items/{id}` - обновить (владелец или `admin`)
* `DELETE /api/v1/items/{id}` - удалить (владелец или `admin`)
* `GET    /api/v1/items?limit=&offset=&sort=&label=` - список
  `sort ∈ {score,-score,created_at,-created_at,impact,-impact,effort,-effort}`

Служебные (для базовых проверок шаблона):

* `GET  /items/{id}` - возвращает `404` в нужном формате
* `POST /items?name=...` - проверка валидации query

Здоровье:

* `GET /health` -> `{"status":"ok"}`

## Примеры

```bash
# создать
curl -s -X POST http://127.0.0.1:8000/api/v1/items \
  -H "Content-Type: application/json" \
  -H "X-User-Id: demo-user" \
  -d '{"title":"Idea A","impact":8,"effort":3,"labels":["ux","quick"]}'

# список с сортировкой по score (убывание)
curl -s -H "X-User-Id: demo-user" \
  "http://127.0.0.1:8000/api/v1/items?sort=-score&limit=10&offset=0"

# чтение чужим пользователем -> 403
curl -i -H "X-User-Id: other" http://127.0.0.1:8000/api/v1/items/<id>

# админ читает любой item
curl -s -H "X-User-Id: admin" -H "X-User-Role: admin" \
  http://127.0.0.1:8000/api/v1/items/<id>
```

## Формат ошибок

```json
// 404
{ "error": { "code": "not_found" } }
```

```json
// 422
{
  "error": {
    "code": "validation_error",
    "details": [
      { "loc": ["body","field"], "msg": "...", "type": "..." }
    ]
  }
}
```

```json
// 500
{ "code": "INTERNAL_ERROR", "message": "Unexpected error", "details": {} }
```

## Проверки перед PR

```bash
ruff check --fix .
black .
isort .
pytest -q
pre-commit run --all-files
```

## Тесты

```bash
pytest -q
```

## CI

GitHub Actions: установка зависимостей -> ruff/black/isort (check) -> pytest -> pre-commit.
Проверки обязательны для ветки `main`.

## Контейнер

```bash
docker build -t idea-backlog .
docker run --rm -p 8000:8000 idea-backlog
# либо
docker compose up --build
```

## Процессы

* Для ревью используется чек-лист: [docs/REVIEW_CHECKLIST.md](docs/REVIEW_CHECKLIST.md)
* В проекте настроен `.github/CODEOWNERS` - ревьюеры добавляются автоматически при изменениях в коде.

---

## Примечания

* Заголовки аутентификации: `X-User-Id`, `X-User-Role: admin|user` (по умолчанию `user`).
* Поля item: `title (1..120)`, `impact (1..10)`, `effort (1..10)`, `notes?`, `labels[]` (≤10, ≤24).
* Для очистки БД достаточно удалить `app.db`.

См. также: `SECURITY.md`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml`.

```
```
