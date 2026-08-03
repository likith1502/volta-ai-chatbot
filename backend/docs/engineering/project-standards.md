# VOLTA AI Chatbot - Official Project Standards

## 1. Python Version
- **Target Version**: Python 3.11+
- **Syntax Standards**: Standard library type hints (`list[str]`, `dict[str, Any]`, `str | None`).

---

## 2. Formatting Standard
- **Code Formatter**: Black standard (88-character line limit).
- **Indentation**: 4 spaces per indentation level.
- **Encoding & Line Endings**: UTF-8 encoding with LF (`\n`) line endings.

---

## 3. Typing Rules
- **Type Annotations**: All function signatures (arguments and return types) must feature explicit type annotations.
- **Type Checking**: Static analysis compatibility with `mypy` strict mode.

---

## 4. Async Rules
- **Non-Blocking I/O**: All network, database, and cache operations must use `async/await`.
- **Event Loop Protection**: Never invoke blocking synchronous functions (`time.sleep()`, synchronous `requests`, or blocking DB calls) inside async context.

---

## 5. Naming Conventions
- **Files & Modules**: Lowercase `snake_case` (`main.py`, `ride_service.py`).
- **Classes**: `PascalCase` (`ConversationManager`, `BaseRepository`).
- **Functions & Methods**: Lowercase `snake_case` (`get_user_by_id()`, `check_health()`).
- **Constants**: Uppercase `SNAKE_CASE` (`DEFAULT_DATETIME_FORMAT`).

---

## 6. Directory Convention
- `app/api/`: Endpoint definitions and routers.
- `app/services/`: Domain business logic and service implementations.
- `app/repositories/`: Database persistence and querying modules.
- `app/models/`: SQLAlchemy ORM database models.
- `app/schemas/`: Pydantic data transfer objects (DTOs).

---

## 7. Import Convention
Group imports in order separated by an empty line:
1. Standard library imports
2. Third-party package imports
3. Local application imports (`app.*`)

---

## 8. Git, Commit & Branch Conventions
- **Branch Naming**: `feature/*`, `bugfix/*`, `hotfix/*`, `release/*`.
- **Commit Messages**: Conventional Commits format (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).

---

## 9. Testing & Dependency Conventions
- **Testing**: Automated pytest coverage for all endpoints and business logic.
- **Dependencies**: Minimal dependency additions using SemVer range constraints in `requirements.txt`.
