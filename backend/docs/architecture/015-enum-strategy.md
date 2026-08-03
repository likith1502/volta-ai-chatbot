# ADR 015: Database Enum Strategy & Schema Migration Governance

## Status
Accepted

## Date
2026-08-03

---

## Context
Multiple domain models (`Message`, `Conversation`, `Recommendation`, `Booking`, `Notification`, `Memory`) require bounded categorical values (roles, statuses, types). A design decision was required to establish the project standard for storing enums in PostgreSQL via SQLAlchemy 2.0.

---

## Options Considered

### Option A: Native PostgreSQL Enums (`native_enum=True`)
- **Description**: Uses PostgreSQL `CREATE TYPE ... AS ENUM (...)` native custom types.
- **Advantages**:
  - Strict database-engine level validation.
- **Disadvantages**:
  - Adding new enum values (e.g. `WHATSAPP_AUDIO`) requires PostgreSQL `ALTER TYPE ... ADD VALUE ...`, which cannot be executed within transactional Alembic migration blocks.
  - Complicates rollback (`downgrade`) scripts and multi-database development testing.

### Option B: String-Backed Enums (`native_enum=False, length=32`) (Selected Strategy)
- **Description**: Maps Python `(str, Enum)` objects to `VARCHAR(32)` columns at the database engine level, enforcing strict enum validation via Python type hints and Pydantic schemas.
- **Advantages**:
  - Full compatibility with transactional Alembic schema migrations.
  - Adding new enum choices requires zero database DDL lock operations.
  - Easy cross-database portability and fast automated testing.
  - Enforces 100% strict Python type-safety at the ORM and API layers.
- **Disadvantages**:
  - Values are stored as strings in PostgreSQL (offset by fast B-Tree indexing).

---

## Decision
VOLTA AI Chatbot officially adopts **Option B: String-Backed Enums (`native_enum=False, length=32`)**. All enums must inherit from Python `(str, Enum)` and map to `Enum(EnumType, native_enum=False, length=32)`.

---

## Rationale
This strategy prioritizes long-term maintainability, seamless transactional Alembic migrations, and operational safety. In a fast-evolving AI dialogue platform, new intent classifications, message types, and notification channels will be added frequently. Eliminating transactional database locks during schema migrations prevents production deployment downtime.

---

## Best Practices & Rules
1. **Inherit `(str, Enum)`**: All domain enum classes in `app/models/enums.py` must inherit from `str` and `Enum`.
2. **Explicit Column Builder**: Map columns using `Enum(EnumType, native_enum=False, length=32)`.
3. **Upper Snake Case**: Enum member keys use `UPPER_SNAKE_CASE` while values use `lower_snake_case` string representation (e.g. `ACTIVE = "active"`).
