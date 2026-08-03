# ADR 016: Service Layer Architecture & Transaction Governance

## Status
Accepted

## Date
2026-08-03

---

## Context
As the Volta AI Chatbot platform expands beyond static persistence, business logic, multi-repository orchestration, domain validation, and transaction management must be cleanly decoupled from HTTP presentation routers and lower-level SQL/ORM repositories.

---

## Technical Decisions & Rationale

### 1. Strict Layer Separation
- **Decision**: The Application Service Layer (`app/services/`) acts as the application's business engine. Services contain zero HTTP references (`Request`, `Response`, `APIRouter`) and zero database query statements (`select()`, `update()`, `delete()`).
- **Rationale**: Keeps business rules reusable across multiple interfaces (REST APIs, WebSockets, background Celery workers, CLI commands).

### 2. Transaction Ownership & Boundaries
- **Decision**: Services own transaction boundaries (`await self.commit()`, `await self.rollback()`). Repositories use `flush()` and `refresh()` only.
- **Rationale**: Enables atomic multi-repository workflows (e.g. creating a booking, marking a recommendation as accepted, and issuing a notification in a single database transaction).

### 3. Constructor Dependency Injection
- **Decision**: Services receive `AsyncSession` via constructor injection (`__init__(self, session: AsyncSession)`), instantiating necessary domain repositories internally.
- **Rationale**: Simplifies FastAPI dependency injection (`Depends(get_db_session)`) while providing clean transaction boundaries over all underlying repositories.

### 4. Domain Exception Pattern
- **Decision**: Services communicate business rule violations by raising strongly-typed domain exceptions (`UserAlreadyExistsException`, `RecommendationExpiredException`, `BookingNotFoundException`).
- **Rationale**: Eliminates ambiguous return types (`None` vs `False`). Global exception handlers (`app/core/exception_handlers.py`) automatically map these domain exceptions to standard HTTP JSON error envelopes.
