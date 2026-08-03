# VOLTA AI Chatbot - Database Architecture & Request Flow

## 1. Database Request Flow Architecture

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

### Layer Descriptions

1. **FastAPI Route**: Receives incoming HTTP requests, validates Pydantic input schemas, and passes request parameters to service components.
2. **Dependency Injection (`get_db_session`)**: Injects an isolated `AsyncSession` per HTTP request. Manages automatic `commit()` on success, `rollback()` on exceptions, and closing the connection upon response completion.
3. **AsyncSession (Unit of Work)**: Manages in-memory object tracking, transaction boundaries, and state synchronization for the request context.
4. **SQLAlchemy ORM (`AsyncEngine`)**: Translates high-level Python ORM queries into PostgreSQL dialect SQL statements using non-blocking connection pools.
5. **Async PostgreSQL Driver (`asyncpg`)**: Provides high-performance binary protocol non-blocking network I/O with PostgreSQL.
6. **PostgreSQL Server**: Relational database engine enforcing ACID compliance, constraints, indexes, and physical persistence.

---

## 2. Database Migration Flow Architecture

```
+-----------------------------------------------------------------------+
|                               Developer                               |
+-----------------------------------------------------------------------+
                                    │
                                    v
+-----------------------------------------------------------------------+
|             SQLAlchemy ORM Models (`Base.metadata`)                   |
+-----------------------------------------------------------------------+
                                    │
                                    v
+-----------------------------------------------------------------------+
|             `alembic revision --autogenerate -m "..."`                |
+-----------------------------------------------------------------------+
                                    │
                                    v
+-----------------------------------------------------------------------+
|               Migration Script (`migrations/versions/`)                |
+-----------------------------------------------------------------------+
                                    │
                                    v
+-----------------------------------------------------------------------+
|                        `alembic upgrade head`                         |
+-----------------------------------------------------------------------+
                                    │
                                    v
+-----------------------------------------------------------------------+
|                          PostgreSQL Server                            |
+-----------------------------------------------------------------------+
```

### Stage Descriptions

1. **Developer**: Declares or updates ORM models in code.
2. **SQLAlchemy Models (`Base.metadata`)**: Models inherit from `Base` with explicit PostgreSQL constraint naming conventions.
3. **`alembic revision --autogenerate`**: Alembic compares `Base.metadata` against active database tables and generates Python migration DDL.
4. **Migration Script (`migrations/versions/`)**: Version-controlled migration script containing `upgrade()` and `downgrade()` functions.
5. **`alembic upgrade head`**: Applies pending migrations transactionally to the target PostgreSQL environment.
6. **PostgreSQL Server**: Schema changes are applied, and `alembic_version` table is updated.
