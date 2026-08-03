# Architectural Guideline 012: Domain Modeling Guidelines

## Overview
This document specifies the mandatory domain modeling rules and patterns for all future database ORM entities created in **Chapter 2.4 (Domain Models)** and beyond (`User`, `Ride`, `Conversation`, `Notification`, `SavedPlace`).

---

## 1. Class & Table Naming Conventions
- **Class Names**: Use singular `PascalCase` (e.g. `User`, `Ride`, `Conversation`, `Notification`, `SavedPlace`).
- **Table Names**: Use plural `snake_case` explicitly declared via `__tablename__` (e.g. `users`, `rides`, `conversations`, `notifications`, `saved_places`).

---

## 2. Relationship Conventions
- **Explicit Relationships**: Always use `relationship(..., back_populates="...")`. Never use deprecated `backref`.
- **Lazy Loading Strategy**: Use default lazy loading (`select`) or explicit `selectinload` / `joinedload` in queries. Avoid implicit aggressive eager loading across large object graphs.

---

## 3. Foreign Key Conventions
- **Naming Pattern**: All foreign key columns must use singular target table reference with `_id` suffix (e.g. `user_id`, `ride_id`).
- **Explicit Constraint Names**: Foreign keys inherit automatic explicit naming (`fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s`) from `POSTGRES_NAMING_CONVENTION`.
- **Indexing**: Every foreign key column **must** feature an index (`index=True`) to optimize JOIN performance.

---

## 4. Nullable Philosophy
- **Explicit Constraints**: Columns must explicitly declare `nullable=False` or `nullable=True`.
- **Default Non-Null**: Default to `nullable=False` unless the field is strictly optional domain data.

---

## 5. Enum Philosophy
- **Python Enums**: Store enumerations using Python `enum.Enum` mapped to PostgreSQL `Enum` or string fields (`NativeEnum(create_type=False)` or `String(32)`).
- **String Enums**: Prefer string-backed enums to simplify future schema migration additions without requiring complex PostgreSQL `ALTER TYPE` DDL operations.

---

## 6. Indexing Guidelines
- **Targeted Columns**: Add indexes (`index=True`) on foreign key columns, unique search parameters (email, phone), and soft deletion flags (`is_deleted`).
- **Composite Indexes**: Use `__table_args__ = (Index("ix_...", "col_a", "col_b"),)` for frequent multi-column filtering patterns.

---

## 7. Cascade Delete Policy
- **Soft Delete Alignment**: Prefer soft deletion over physical cascade deletion.
- **Physical Cascade**: If physical child cleanup is required, configure explicit `cascade="all, delete-orphan"` on relationships and `ondelete="CASCADE"` on foreign keys.

---

## 8. Layer Responsibility Matrix

| Layer | Responsibility | Forbidden Actions |
| :--- | :--- | :--- |
| **ORM Models (`app/models/`)** | Entity schema definition, column data types, relationships | No business logic, no HTTP validation, no database queries |
| **Repositories (`app/repositories/`)** | Database CRUD execution, query building, transaction handling | No HTTP parameter parsing, no domain business decisions |
| **Services (`app/services/`)** | Business logic, AI orchestration, state transition rules | No raw SQL queries, no direct HTTP response formatting |

---

## 9. Validation Philosophy
- **Database Level**: Enforce structural constraints (data types, nullability, uniqueness, foreign keys) at the database layer.
- **API Level**: Enforce business validation, string formatting, and range checks at the Pydantic schema layer (`app/schemas/`).

---

## 10. Standard Model Template (Reference Only)

```python
# Example Reference Model Template for Chapter 2.4
from typing import Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import AuditMixin, SoftDeleteMixin, TimestampMixin, UUIDMixin


class User(UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
```
