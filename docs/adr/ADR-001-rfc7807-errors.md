# ADR-001: Единый формат ошибок RFC 7807
Дата: 2025-09-22
Статус: Accepted

## Context
Нужно единообразно возвращать ошибки API, маскировать детали и иметь trace (`correlation_id`).
Альтернативы: «свои JSON», plain text, HTTP-коды без тела.

## Decision
Используем формат RFC 7807 (`type`, `title`, `status`, `detail`, `correlation_id`).
Вводим helper `problem()` и регистрируем FastAPI exception handlers.

## Consequences
+ Единый контракт, проще тесты/логирование.
− Небольшие изменения эндпоинтов/handler’ов.

## Links
- tests/test_rfc7807.py::test_problem_shape
- PR: p05-secure-coding
