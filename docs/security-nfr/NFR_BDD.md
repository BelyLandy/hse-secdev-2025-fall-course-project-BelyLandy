# NFR_BDD.md

Feature: Обязательный X-User-Id (NFR-01)
  Scenario: Запрос без заголовка отклоняется
    Given API запущено
    When клиент делает POST /api/v1/items без заголовка X-User-Id
    Then статус ответа 401 или 403
    And тело ответа содержит "error"

Feature: Авторизация owner/admin (NFR-02)
  Scenario: Пользователь не видит чужие объекты
    Given есть item, созданный пользователем "alice"
    When пользователь "bob" делает GET /api/v1/items/{id} без роли admin
    Then статус ответа 403

  Scenario: Администратор видит всё
    Given есть два item от разных пользователей
    When admin делает GET /api/v1/items?limit=100
    Then в ответе >= 2 записи

Feature: Структурированные ошибки (NFR-04)
  Scenario: 404 в едином формате
    Given отсутствующий item_id
    When клиент делает GET /api/v1/items/{id}
    Then статус 404
    And тело {"error":{"code":"not_found", ...}}

Feature: Валидация полей (NFR-03)
  Scenario: Нарушение диапазона даёт 422
    When клиент отправляет impact=0 или effort=11
    Then статус 422
    And тело содержит error.code = "validation_error"

Feature: Политики исходящих HTTP (NFR-11)
  Scenario: Таймаут маппится в RFC7807
    Given зависание внешнего API
    When сервис вызывает external endpoint
    Then клиент получает JSON RFC7807 с title="Upstream timeout"
