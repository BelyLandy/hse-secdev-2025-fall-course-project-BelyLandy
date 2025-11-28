# Idea Backlog

Небольшой сервис для ведения каталога идей: CRUD, сортировка по `score = impact / effort`, доступ только владельцу (или роли `admin`).
Стек: FastAPI + SQLite.

---

Бейдж - [![CI](https://github.com/BelyLandy/Devyatov-hse-secdev-2025-course-project/actions/workflows/ci.yml/badge.svg)](https://github.com/BelyLandy/Devyatov-hse-secdev-2025-course-project/actions/workflows/ci.yml)

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
```

База локально: файл `app.db` в корне проекта.
В контейнере: файл БД монтируется в volume по пути `/data/app.db`.

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
  где `sort ∈ {score,-score,created_at,-created_at,impact,-impact,effort,-effort}`,
  `label` - необязательный фильтр; длина метки <= 24 символов.

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

PowerShell-версия получения ID:

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

## Контейнеризация (P07)

В проекте настроены безопасные образы и запуск:

### Что сделано
- **Multi-stage Dockerfile** на `python:3.12-slim`; финальный образ без dev-утилит.
- Приложение работает под **непривилегированным пользователем** `app` (uid/gid 999).
- **read_only** root-FS; запись разрешена только в:
  - volume `/data` (для БД),
  - tmpfs `/tmp`, `/run`.
- **HEALTHCHECK** опрашивает `GET /health`.
- Усиление: `cap_drop: [ALL]`, `security_opt: ["no-new-privileges:true"]`, `ulimits: { nofile: 4096 }`.

### Переменные окружения
- `DB_PATH` - путь к базе (по умолчанию `/data/app.db` внутри контейнера).
  В compose это уже задано: `APP_DB_PATH=/data/app.db` или `DB_PATH=/data/app.db` (в зависимости от кода).

### Сборка и запуск
```bash
docker compose build
docker compose up -d

# здоровье должно стать healthy
docker inspect -f '{{.State.Health.Status}}' idea
```

### Быстрые проверки харднинга
```bash
# 1) health
curl -s http://127.0.0.1:8000/health

# 2) процесс не под root
docker exec idea sh -lc 'id'            # uid=999(app) gid=999(app)

# 3) root-FS read-only, но /data writable
docker exec idea sh -lc 'test -w / && echo rw || echo ro'         # ro
docker exec idea sh -lc 'test -w /data && echo data-writable'     # data-writable

# 4) security опции и capabilities
docker inspect idea --format '{{json .HostConfig.SecurityOpt}}' | python -m json.tool
docker inspect idea --format '{{json .HostConfig.CapDrop}}' | python -m json.tool
```

### Проверка сохранности данных (volume `/data`)
```bash
# создать
curl -s -X POST http://127.0.0.1:8000/api/v1/items \
  -H "Content-Type: application/json" -H "X-User-Id: demo" \
  -d '{"title":"VOL","impact":8,"effort":2}'

# убедиться, что создалось
curl -s -H "X-User-Id: demo" "http://127.0.0.1:8000/api/v1/items?sort=-created_at"

# перезапуск и повторная проверка - запись должна сохраниться
docker compose restart
curl -s -H "X-User-Id: demo" "http://127.0.0.1:8000/api/v1/items?sort=-created_at"
```

---

## Линтер Dockerfile и скан уязвимостей

### hadolint (Dockerfile)
```bash
docker run --rm -i hadolint/hadolint < Dockerfile
# если замечаний нет то пустой вывод
```

### Trivy (образ)

```bash
docker save idea-backlog:local -o idea-backlog.tar

# Git Bash:
docker run --rm -v "$(pwd)":/work -w /work \
  aquasec/trivy:0.56.2 \
  image --input /work/idea-backlog.tar \
  --severity HIGH,CRITICAL --ignore-unfixed \
  --format table --output trivy.txt

# PowerShell:
docker run --rm -v ${PWD}:/work -w /work `
  aquasec/trivy:0.56.2 `
  image --input /work/idea-backlog.tar `
  --severity HIGH,CRITICAL --ignore-unfixed `
  --format table --output trivy.txt
```

---

## Мини-smoke для контейнера

```bash
# здоровье
curl -s http://127.0.0.1:8000/health

# CRUD под непривилегированным пользователем
curl -s -X POST http://127.0.0.1:8000/api/v1/items \
  -H "Content-Type: application/json" -H "X-User-Id: demo" \
  -d '{"title":"A","impact":5,"effort":2}'
curl -s -H "X-User-Id: demo" "http://127.0.0.1:8000/api/v1/items?sort=-score"

# owner-only и роль admin - см. раздел «Примеры (curl)»
```

---

## Короткий пример CI (GitHub Actions)

`.github/workflows/ci.yml` - добавленные шаги для hadolint и Trivy:

```yaml
name: CI
on: [push, pull_request]

jobs:
  build-test-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install deps
        run: |
          python -m pip install -U pip
          pip install -r requirements.txt
          pip install ruff black isort pytest

      - name: Lint & Test
        run: |
          ruff check .
          black --check .
          isort --check-only .
          pytest -q

      - name: Hadolint
        uses: hadolint/hadolint-action@v3.1.0
        with:
          dockerfile: ./Dockerfile

  image-security:
    runs-on: ubuntu-latest
    needs: build-test-lint
    steps:
      - uses: actions/checkout@v4

      - name: Build image
        run: docker build -t idea-backlog:local .

      - name: Trivy scan (HIGH,CRITICAL, ignore-unfixed)
        uses: aquasecurity/trivy-action@0.24.0
        with:
          image-ref: "idea-backlog:local"
          format: "table"
          severity: "HIGH,CRITICAL"
          ignore-unfixed: true
          exit-code: "0"
```

---

## Процессы

* Чек-лист ревью: `docs/REVIEW_CHECKLIST.md`
* Автоподписанты: `.github/CODEOWNERS`
* CI-workflow: `.github/workflows/ci.yml`

---

## Примечания

* Поля item: `title (1..120)`, `impact (1..10)`, `effort (1..10)`, `notes?`, `labels[]` (<= 10 штук, длина каждой <= 24).
* Для очистки локальной БД - удалите файл `app.db`.
* В контейнере данные хранятся в Docker volume `appdb` (путь `/data/app.db`), рестарты не стирают данные.

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

---

## P09

### Что делает workflow

* Генерирует **SBOM** (Syft, формат CycloneDX JSON) из исходников репозитория.
* Запускает **SCA** (Grype) по SBOM.
* Применяет **waivers** из `policy/waivers.yml` и формирует сводку.
* Сохраняет артефакты в GitHub Actions:
  `EVIDENCE/P09/sbom.json`, `EVIDENCE/P09/sca_report.json`, `EVIDENCE/P09/sca_report.filtered.json`, `EVIDENCE/P09/sca_summary.md`, `EVIDENCE/P09/waivers.json`.

Триггеры -`push`, `pull_request` по релевантным путям и `workflow_dispatch`.

---

### Структура артефактов

```
EVIDENCE/
  P09/
    sbom.json
    sca_report.json
    sca_report.filtered.json
    sca_summary.md
    waivers.json # policy/waivers.yml, сконвертированный в JSON
```

---

### waivers

Файл `policy/waivers.yml`.

Пример:

```yaml
policy:
  owner: "BelyLandy"
  updated_at: "2025-11-28T21:00:00Z"
  rationale: "Waivers используются точечно, с дедлайном пересмотра и ссылкой на Issue/PR."

severity_guidelines:
  critical: "фикс или waiver <= 7 дней"
  high: "фикс или waiver <= 7 дней"
  medium: "план фикса или waiver <= 14 дней"
  low: "best-effort"

waivers:
  - cve: "CVE-2025-7709"
    package: "libsqlite3-0"
    reason: >
      Medium в базовом образе; библиотека используется транзитивно (через Python sqlite3).
      Риск для сервиса низкий. Ждём апдейт базового образа.
    issue: "https://github.com/BelyLandy/Devyatov-hse-secdev-2025-course-project/issues/123"
    until: "2025-12-31T23:59:59Z"
    envs: ["dev", "stage"]
```

---

### Как запустить локально

#### Linux/macOS

```bash
mkdir -p EVIDENCE/P09

export SYFT_VERSION="0.104.0"
export GRYPE_VERSION="0.79.0"

# SBOM
docker run --rm -v "$PWD:/work" -w /work anchore/syft:v${SYFT_VERSION} \
  . -o cyclonedx-json=EVIDENCE/P09/sbom.json

# SCA
docker run --rm -v "$PWD:/work" -w /work anchore/grype:v${GRYPE_VERSION} \
  sbom:/work/EVIDENCE/P09/sbom.json -o json > EVIDENCE/P09/sca_report.json || true
```

#### Windows (Git Bash)

```bash
mkdir -p EVIDENCE/P09

export SYFT_VERSION="0.104.0"
export GRYPE_VERSION="0.79.0"
PWD_WIN="$(pwd -W)"

# SBOM
MSYS_NO_PATHCONV=1 docker run --rm \
  -v "$PWD_WIN:/work" -w /work anchore/syft:v${SYFT_VERSION} \
  . -o cyclonedx-json=EVIDENCE/P09/sbom.json

# SCA
MSYS_NO_PATHCONV=1 docker run --rm \
  -v "$PWD_WIN:/work" -w /work anchore/grype:v${GRYPE_VERSION} \
  sbom:/work/EVIDENCE/P09/sbom.json -o json > EVIDENCE/P09/sca_report.json || true
```

---

### Как посмотреть результаты в CI

1. Откройте вкладку **Actions**, ищем последний успешный запуск по ветке.
2. Внизу страницы в блоке **Artifacts**. Скачать `P09_EVIDENCE-<>`.
3. Внутри файлы из `EVIDENCE/P09/`

---
