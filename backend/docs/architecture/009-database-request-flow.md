# Database Request Flow Architecture

## High-Level Architecture Diagram

```
+-----------------------------------------------------------------------+
|                             FastAPI Route                             |
+-----------------------------------------------------------------------+
                                    │
                                    v
+-----------------------------------------------------------------------+
|             Dependency Injection (`get_db_session`)                   |
+-----------------------------------------------------------------------+
                                    │
                                    v
+-----------------------------------------------------------------------+
|                     AsyncSession (Unit of Work)                       |
+-----------------------------------------------------------------------+
                                    │
                                    v
+-----------------------------------------------------------------------+
|                    SQLAlchemy ORM (`AsyncEngine`)                     |
+-----------------------------------------------------------------------+
                                    │
                                    v
+-----------------------------------------------------------------------+
|               Async PostgreSQL Driver (`asyncpg`)                     |
+-----------------------------------------------------------------------+
                                    │
                                    v
+-----------------------------------------------------------------------+
|                          PostgreSQL Server                            |
+-----------------------------------------------------------------------+
```

---

## Detailed Layer Explanation

### 1. FastAPI Route Layer
- **Responsibility**: Receives incoming HTTP requests, validates Pydantic input schemas, and delegates processing to services.

### 2. Dependency Injection Layer (`get_db_session`)
- **Responsibility**: Injects an isolated `AsyncSession` into route handlers. Manages session scope, guaranteeing automatic `commit()` on success, `rollback()` on exceptions, and closing the connection upon request completion.

### 3. AsyncSession Layer (Unit of Work)
- **Responsibility**: Manages in-memory object state, tracks changes, and coordinates database transaction boundaries for the current operation.

### 4. SQLAlchemy ORM Layer (`AsyncEngine`)
- **Responsibility**: Translates high-level Python ORM model queries into dialect-specific SQL statements. Controls connection pooling (`pool_size`, `max_overflow`, `pool_recycle`).

### 5. Async PostgreSQL Driver Layer (`asyncpg`)
- **Responsibility**: Handles non-blocking asynchronous socket communication with PostgreSQL using binary protocol for maximum performance.

### 6. PostgreSQL Server Layer
- **Responsibility**: Relational database engine responsible for persistent storage, ACID transaction execution, indexing, and data safety.
