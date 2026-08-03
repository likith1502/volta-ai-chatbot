# VOLTA AI Chatbot - Engineering Principles & Constitution

## 1. Architecture Principles
- **Clean Layered Architecture**: Strictly decouple Presentation (Routers), Business Logic (Services), Data Access (Repositories), and Infrastructure (Database/Cache).
- **Single Responsibility Principle (SRP)**: Every module, class, and function must have one, and only one, reason to change.

---

## 2. Clean Code Rules
- **Small Functions**: Keep functions focused, concise, and operating at a single level of abstraction.
- **Self-Documenting Code**: Prefer explicit variable and function names over verbose inline comments.
- **No Magic Values**: Replace hardcoded numbers and strings with application constants (`app/config/constants.py`) or settings.

---

## 3. Folder Responsibilities
- `app/api/`: Handles HTTP routing, path parameters, rate limits, and schema serialization. Contains zero business logic.
- `app/services/`: Implements domain business logic, AI orchestration, and service workflows.
- `app/repositories/`: Manages database querying and data persistence operations. Contains zero business logic.
- `app/config/`: Single source of truth for application configuration (`settings.py`) loading from environment variables.

---

## 4. Dependency Rules
- **Dependency Injection**: Use FastAPI's `Depends` for injecting database sessions, services, and repositories into endpoints.
- **Unidirectional Imports**: Dependencies flow inwards towards core domain entities. Outer layers depend on inner abstractions, never the reverse.

---

## 5. Error Handling Rules
- **Global Interception**: Catch all domain exceptions (`AppException`), HTTP errors, and validation failures via global exception handlers (`app/core/exception_handlers.py`).
- **Standard Payload**: All API errors return a uniform JSON structure (`{"success": false, "message": "...", "data": null, "errors": ...}`).
- **No Stack Trace Leaks**: Never expose raw stack traces, SQL errors, or internal diagnostics to API clients.

---

## 6. Logging Rules
- **Structured Console Logs**: Log operational messages using Python's standard `logging` library formatted with timestamps and log levels.
- **Request Tracing**: Propagate unique `X-Request-ID` headers across all log messages.
- **Privacy & Security**: Never log passwords, API keys, JWT tokens, or sensitive user PII.

---

## 7. Configuration Rules
- **Pydantic Settings**: Manage all configuration through `Settings` (`app/config/settings.py`).
- **Environment Isolation**: Dev defaults provided in `.env.example`. Secrets injected at runtime via environment variables.

---

## 8. Testing Rules
- **Automated Verification**: Every API endpoint and business module requires corresponding automated pytest test coverage.
- **Fast Execution**: Tests must run quickly without relying on external network calls or slow artificial delays.

---

## 9. Documentation Rules
- **Living Documentation**: Architectural blueprints (`docs/architecture/`), API specs, and database designs must be updated whenever system capabilities change.
- **OpenAPI Synchronization**: All public API endpoints must feature clear summaries, descriptions, and tag groupings.

---

## 10. Security Rules
- **Zero Raw Secrets**: Secrets must never be committed to source code or git history.
- **Strict Input Validation**: Validate all incoming HTTP payloads via Pydantic schemas.

---

## 11. Performance Rules
- **Non-Blocking Async Execution**: All network I/O, database queries, and cache lookups must use `async/await`.
- **Resource Cleanup**: Always release database sessions and connections using context managers.

---

## 12. Code Review Checklist
- [ ] Routers contain no business logic
- [ ] Repositories contain no business logic
- [ ] Services contain business logic
- [ ] Configuration loaded strictly from `settings.py`
- [ ] No hardcoded secrets in source code
- [ ] All new endpoints have automated tests
- [ ] All database schema changes have Alembic migrations

---

## 13. Definition of Done (DoD)
A feature or milestone is complete **only when**:
1. Code compiles and runs locally without errors.
2. All automated pytest test cases pass.
3. Code quality standards (formatting, typing) are satisfied.
4. Architectural documentation is updated.
5. Production readiness review is verified.
