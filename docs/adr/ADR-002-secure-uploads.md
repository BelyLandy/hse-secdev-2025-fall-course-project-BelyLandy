# ADR-002: Безопасная загрузка изображений (magic bytes, лимиты, UUID-имя)
Дата: 2025-09-22
Статус: Accepted

## Context
Нужна безопасная обработка загрузок: проверка формата, ограничение размера, защита от traversal/симлинков.

## Decision
Функции `sniff_image_type()` и `secure_save(base_dir, data)`:
- лимит `MAX_BYTES = 5_000_000`;
- magic bytes PNG/JPEG;
- имя файла = UUID + расширение по типу;
- канонизация пути, запрет симлинков.

## Consequences
+ Снижение риска RCE/DoS/poisoning.
− Доп. валидация, CPU на sniff.

## Links
- tests/test_secure_upload.py::*
- PR: p05-secure-coding
