# ADR 017: REST API Layer Architecture & Presentation Boundaries

## Status
Accepted

## Date
2026-08-03

---

## Context
Exposing backend capabilities over HTTP requires a clean presentation layer (`app/api/`) that validates request payloads, delegates business execution to the Application Service Layer, and serializes responses using uniform JSON envelopes without embedding domain logic or database calls into API route handlers.

---

## Technical Decisions & Rationale

### 1. Thin Presentation Routers
- **Decision**: Routers under `app/api/v1/routers/` perform only 4 tasks: (1) HTTP verb & path declaration, (2) Pydantic payload validation, (3) service dependency injection via FastAPI `Depends()`, and (4) returning standard JSON response envelopes (`success_response`).
- **Rationale**: Keeps the HTTP presentation layer strictly separated from core domain business rules.

### 2. Pydantic v2 DTO Separation (`app/schemas/`)
- **Decision**: All API requests and responses utilize explicit Pydantic v2 DTOs (`UserCreate`, `UserUpdate`, `UserResponse`, `BookingCreate`, `BookingResponse`, etc.). SQLAlchemy ORM models are never directly returned or exposed in endpoint signatures.
- **Rationale**: Prevents accidental data leaks (e.g. hashed credentials or internal flags), enforces type safety, and allows ORM models to evolve without breaking API client contracts.

### 3. Versioned Route Hierarchy (`/api/v1/`)
- **Decision**: All endpoints are mounted under `/api/v1/` via an aggregate router (`app/api/v1/router.py`).
- **Rationale**: Guarantees seamless backward compatibility when future major API versions (`v2`) are introduced.

### 4. Transparent Global Exception Handling
- **Decision**: Routers do not catch domain exceptions (`UserNotFoundException`, `UserAlreadyExistsException`, `RecommendationExpiredException`). Domain exceptions propagate directly to FastAPI global exception handlers (`app/core/exception_handlers.py`).
- **Rationale**: Guarantees consistent error JSON structures (`{"success": false, "message": "...", ...}`) and correct HTTP status code mapping (404, 409, 400) without repetitive try/except blocks in endpoints.
