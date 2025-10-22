````markdown
# Idea Backlog

Небольшой сервис для ведения каталога идей: CRUD, сортировка по `score = impact / effort`, доступ только владельцу (или роли `admin`).  
Стек: FastAPI + SQLite.

---

## Быстрый старт (локально)

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows (Git Bash):
source .venv/Scripts/activate
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

# Для разработки:
pip install -U ruff black isort pre-commit pytest
pre-commit install

# Запуск
uvicorn app.main:app --reload
# Swagger: http://127.0.0.1:8000/docs
````

База: файл `app.db` в корне проекта.

---

## Аутентификация (заголовки)

* `X-User-Id: <user>` - обязателен
* `X-User-Role: admin|user` - опционально (по умолчанию `user`)

Доступ к item: владелец (`owner_id == X-User-Id`) или роль `admin`.

---

## Эндпойнты

Доменные:

* `POST   /api/v1/items` - создать
* `GET    /api/v1/items/{id}` - получить (владелец или `admin`)
* `PATCH  /api/v1/items/{id}` - обновить (владелец или `admin`)
* `DELETE /api/v1/items/{id}` - удалить (владелец или `admin`)
* `GET    /api/v1/items?limit=&offset=&sort=&label=` - список
  где `sort ∈ {score,-score,created_at,-created_at,impact,-impact,effort,-effort}`
  `label` - необязательный фильтр; длина метки ≤ 24 символов.

Служебные:

* `GET  /items/{id}` - всегда `404` в RFC7807 (для проверок)
* `POST /items?name=...` - echo-проверка валидации query

Здоровье:

* `GET /health` -> `{"status":"ok"}`

---

## Примеры (curl)

Создание:

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/items \
  -H "Content-Type: application/json" \
  -H "X-User-Id: u1" \
  -d '{"title":"Idea A","impact":8,"effort":2,"labels":["ux","quick"]}'
```

Список с сортировкой по score (убывание):

```bash
curl -s -H "X-User-Id: u1" \
  "http://127.0.0.1:8000/api/v1/items?sort=-score&limit=10&offset=0"
```

Проверка доступа «owner-only» (Git Bash):

```bash
# создаём item и вытаскиваем его id (без jq)
ID=$(curl -s -X POST http://127.0.0.1:8000/api/v1/items \
  -H "Content-Type: application/json" -H "X-User-Id: u1" \
  -d '{"title":"OWN","impact":7,"effort":2}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['id'])")

# чужой пользователь - 403
curl -i -H "X-User-Id: other" "http://127.0.0.1:8000/api/v1/items/$ID"

# админ читает любой - 200
curl -i -H "X-User-Id: admin" -H "X-User-Role: admin" \
  "http://127.0.0.1:8000/api/v1/items/$ID"
```

PowerShell версия получения ID:

```powershell
$ID = (curl -s -Method POST http://127.0.0.1:8000/api/v1/items `
  -H "Content-Type: application/json" -H "X-User-Id: u1" `
  -Body '{"title":"OWN","impact":7,"effort":2}' | `
  python -c "import sys,json; print(json.load(sys.stdin)['id'])").Content.Trim()
```

Фильтр по метке:

```bash
curl -s -H "X-User-Id: u1" "http://127.0.0.1:8000/api/v1/items?label=ux"
```

Слишком длинная метка (25 символов) -> 422:

```bash
curl -i -H "X-User-Id: u1" \
  "http://127.0.0.1:8000/api/v1/items?label=xxxxxxxxxxxxxxxxxxxxxxxxx"
```

---

## Формат ошибок (RFC 7807)

404 (Not Found):

```json
{
  "type": "about:blank#not-found",
  "title": "Not Found",
  "status": 404,
  "detail": "Resource not found",
  "correlation_id": "..."
}
```

422 при ошибках тела запроса (строгая схема, extra запреты):

```json
{
  "type": "about:blank#validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "Request validation failed",
  "correlation_id": "...",
  "errors": [
    { "type":"extra_forbidden", "loc":["body","hacker"], "msg":"Extra inputs are not permitted", "input":"oops" }
  ]
}
```

422 при ошибках query (пример: слишком длинный `label`):

```json
{
  "type": "about:blank#http-error",
  "title": "HTTP Error",
  "status": 422,
  "detail": "{'code': 'VALIDATION_ERROR', 'message': 'label too long', 'details': {'label': 'max length is 24'}}",
  "correlation_id": "..."
}
```

> Примечание: мы намеренно не раскрываем внутренние детали; есть `correlation_id` для трассировки в логах.

---

## Тесты и качество

Локальные проверки перед PR:

```bash
ruff check --fix .
black .
isort .
pytest -q
pre-commit run --all-files
```

Запуск тестов:

```bash
pytest -q
```

CI (GitHub Actions): установка зависимостей -> ruff/black/isort (check) -> pytest -> pre-commit.
Проверки обязательны для ветки `main`.

---

## Контейнеризация

```bash
docker build -t idea-backlog .
docker run --rm -p 8000:8000 idea-backlog
# или
docker compose up --build
```

---

## Security-контроли

В проекте реализованы и тестами покрыты ключевые практики безопасного кодирования:

* **Строгая валидация входа**: запрет лишних полей (`extra="forbid"`), длины, типы, в т.ч. для query.
* **RFC 7807**: структурированные ошибки с `correlation_id`, без утечек внутренностей.
* **Безопасная работа с файлами**: magic bytes, лимиты размера, канонизация пути, UUID-имя, запрет симлинков (тесты включены).
* **Безопасный HTTP-клиент**: таймауты по умолчанию, ретраи с экспоненциальной паузой, ограничение попыток.
* **SQL**: доступ через ORM, без ручной конкатенации.

---

## Процессы

* Чек-лист ревью: [docs/REVIEW_CHECKLIST.md](docs/REVIEW_CHECKLIST.md)
* Автоподписанты: `.github/CODEOWNERS`
* CI-workflow: `.github/workflows/ci.yml`

---

## Примечания

* Поля item: `title (1..120)`, `impact (1..10)`, `effort (1..10)`, `notes?`, `labels[]` (≤ 10 штук, длина каждой ≤ 24).
* Для очистки БД - удалите файл `app.db`.

См. также: `SECURITY.md`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml`.

---

## Быстрая ручная проверка

```bash
# 1) здоровье
curl -s http://127.0.0.1:8000/health

# 2) создать 2 идеи
curl -s -X POST http://127.0.0.1:8000/api/v1/items -H "Content-Type: application/json" -H "X-User-Id: u1" \
  -d '{"title":"A","impact":8,"effort":2,"labels":["ux"]}'
curl -s -X POST http://127.0.0.1:8000/api/v1/items -H "Content-Type: application/json" -H "X-User-Id: u1" \
  -d '{"title":"B","impact":9,"effort":9,"labels":["slow"]}'

# 3) сортировка по -score: A должна быть впереди B
curl -s -H "X-User-Id: u1" "http://127.0.0.1:8000/api/v1/items?sort=-score&limit=10&offset=0"

# 4) owner-only: 403 чужим и 200 админом
ID=$(curl -s -X POST http://127.0.0.1:8000/api/v1/items -H "Content-Type: application/json" -H "X-User-Id: u1" \
  -d '{"title":"OWN","impact":7,"effort":2}' | python -c "import sys,json; print(json.load(sys.stdin)['id'])")
curl -i -H "X-User-Id: other" "http://127.0.0.1:8000/api/v1/items/$ID"     # 403
curl -i -H "X-User-Id: admin" -H "X-User-Role: admin" \
  "http://127.0.0.1:8000/api/v1/items/$ID"                                  # 200

# 5) strict-схема: лишнее поле -> 422 (RFC7807)
curl -i -X POST http://127.0.0.1:8000/api/v1/items -H "Content-Type: application/json" -H "X-User-Id: u1" \
  -d '{"title":"H","impact":5,"effort":5,"hacker":"oops"}'

# 6) длинный label -> 422
curl -i -H "X-User-Id: u1" "http://127.0.0.1:8000/api/v1/items?label=xxxxxxxxxxxxxxxxxxxxxxxxx"

# 7) совместимые эндпойнты шаблона
curl -i http://127.0.0.1:8000/items/123
curl -s -X POST "http://127.0.0.1:8000/items?name=test"
```
