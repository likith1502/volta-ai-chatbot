# Database Base Mixins Architecture & Design

## Overview
Database Base Mixins provide reusable, standardized column definitions and behavior for all SQLAlchemy ORM models across the VOLTA AI Chatbot backend. Rather than manually redefining identifiers, creation timestamps, and deletion flags in every entity model, domain models compose these generic mixin classes.

---

## 1. Architectural Philosophy: Composition Over Duplication
- **DRY (Don't Repeat Yourself)**: Eliminates code duplication across future domain entities (`User`, `Ride`, `Conversation`, `Notification`, `SavedPlace`).
- **Standardized Schema**: Enforces uniform column names (`id`, `created_at`, `updated_at`, `is_deleted`) across the PostgreSQL database.
- **Single Responsibility**: Each mixin class handles a single, well-defined database concern.

---

## 2. High-Level Inheritance Diagram

```
                                DeclarativeBase (Base)
                                          ▲
                                          │
                  ┌───────────────────────┼───────────────────────┐
                  │                       │                       │
              UUIDMixin            TimestampMixin            AuditMixin
                  │                       │                       │
                  └───────────────────────┼───────────────────────┘
                                          │
                                          ▼
                                     User Model
                                (app/models/user.py)
```

---

## 3. Implemented Mixins Specification

### A. `UUIDMixin`
- **Purpose**: Provides a primary key UUID v4 identifier.
- **Columns**: `id: Mapped[uuid.UUID]` (Primary Key, default `uuid.uuid4`, indexed, non-nullable).
- **Advantage**: Prevents sequential primary key enumeration attacks on public API endpoints.

### B. `TimestampMixin`
- **Purpose**: Provides automatic creation and modification timestamps in UTC.
- **Columns**:
  - `created_at: Mapped[datetime]` (UTC timezone-aware, server default `func.now()`, non-nullable).
  - `updated_at: Mapped[datetime]` (UTC timezone-aware, server default `func.now()`, `onupdate=func.now()`, non-nullable).

### C. `SoftDeleteMixin`
- **Purpose**: Provides logical non-destructive record deletion.
- **Columns**:
  - `is_deleted: Mapped[bool]` (default `False`, indexed, non-nullable).
  - `deleted_at: Mapped[Optional[datetime]]` (UTC timezone-aware, default `None`, nullable).
- **Methods**:
  - `soft_delete()`: Sets `is_deleted = True` and records current UTC timestamp in `deleted_at`.
  - `restore()`: Sets `is_deleted = False` and resets `deleted_at = None`.

### D. `AuditMixin`
- **Purpose**: Tracks user or component lineage for entity mutations.
- **Columns**:
  - `created_by: Mapped[Optional[uuid.UUID]]` (nullable).
  - `updated_by: Mapped[Optional[uuid.UUID]]` (nullable).

---

## 4. Usage Example for Future Domain Models

When domain models are defined in Chapter 2.4, they will compose mixins alongside `Base`:

```python
# Future User Model Example (Chapter 2.4)
from app.database.base import Base
from app.database.mixins import AuditMixin, SoftDeleteMixin, TimestampMixin, UUIDMixin


class User(UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(nullable=False)
```
