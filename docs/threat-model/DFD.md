# DFD - Data Flow Diagram (Idea Backlog)

## Диаграмма (Mermaid)

```mermaid
flowchart LR
  U[User/Client] -->|F1: HTTPS /api/v1/items (POST)| API[FastAPI App]
  U -->|F2: HTTPS /api/v1/items?… (GET)| API
  U -->|F3: HTTPS /api/v1/items/{id} (GET)| API
  U -->|F4: HTTPS /api/v1/items/{id} (PATCH)| API
  U -->|F5: HTTPS /api/v1/items/{id} (DELETE)| API

  subgraph Edge[Trust Boundary: Edge]
    API
  end

  subgraph Core[Trust Boundary: Core]
    DB[(SQLite file: app.db)]
  end

  API -->|F6: SQL (tx)| DB

  %% Контекст аутентификации
  %% X-User-Id, X-User-Role: admin|user в заголовках

  classDef boundary fill:#222,stroke:#999,stroke-width:2px,color:#fff;
  class Edge,Core boundary;
