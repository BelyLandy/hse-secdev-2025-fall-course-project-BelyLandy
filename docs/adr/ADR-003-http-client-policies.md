# ADR-003: Политики исходящих HTTP (timeouts, retries)
Дата: 2025-09-22
Статус: Accepted

## Context
Исходящие вызовы должны быть ограничены по времени, с управляемыми ретраями.

## Decision
Клиент по умолчанию: timeout <= 3s connect / 5s read, retries <= 2 с backoff, circuit-breaker (примитивный).

## Consequences
+ Контролируемая деградация.
− Возможные задержки на ретраях.

## Links
- tests/test_http_policies.py
- PR: p05-secure-coding
