# VOLTA AI Chatbot - Repository Pattern Architecture

## Overview
The Repository Pattern serves as the data access abstraction layer for the VOLTA AI Chatbot backend platform. It encapsulates all database query construction, pagination, and persistence operations behind generic and domain-specific repository interfaces.

```
FastAPI Presentation Layer (app/api/v1/)
       │
       ▼
Business Services Layer (app/services/)  ◄── [Transaction Ownership: commit() / rollback()]
       │
       ▼
Repositories Layer (app/repositories/)   ◄── [Data Operations: flush(), refresh(), add()]
       │
       ▼
SQLAlchemy ORM Models (app/models/)
       │
       ▼
Async PostgreSQL Database Engine
```

---

## 1. Core Responsibilities & Boundaries

### Included Responsibilities
- Constructing type-safe SQLAlchemy 2.0 `select()`, `update()`, and `delete()` statements.
- Executing queries asynchronously via `AsyncSession`.
- Managing default soft deletion filters (`is_deleted == False`).
- Providing pagination (`offset`, `limit`), count (`count()`), and existence (`exists()`) utilities.

### Excluded Responsibilities (Strict Boundaries)
- **Zero Business Logic**: Repositories contain no domain validation, price calculations, intent detection, or AI decision rules.
- **Zero Transaction Management**: Repositories **never** call `session.commit()` or `session.rollback()`. Transaction boundaries belong strictly to the Application Services layer.

---

## 2. Generic Inheritance Strategy (`BaseRepository[T]`)

Every domain repository inherits from `BaseRepository[T]` (`app/repositories/base.py`), where `T` is bound to a SQLAlchemy model inheriting `Base`:

```python
class BaseRepository(Generic[T]):
    def __init__(self, model_class: Type[T], session: AsyncSession) -> None:
        self.model_class = model_class
        self.session = session
```

### Generic Methods Provided
- `get_by_id(id: UUID, include_deleted: bool = False) -> T | None`
- `list(offset: int = 0, limit: int = 100, include_deleted: bool = False) -> list[T]`
- `create(attributes: dict[str, Any]) -> T`
- `update(id: UUID, attributes: dict[str, Any]) -> T | None`
- `delete(id: UUID, hard: bool = False) -> bool`
- `exists(id: UUID, include_deleted: bool = False) -> bool`
- `count(include_deleted: bool = False) -> int`

---

## 3. Soft Delete Mechanics
Models inheriting `SoftDeleteMixin` feature logical soft deletion:

1. **Default Deletion (`hard=False`)**: Calling `repository.delete(id, hard=False)` executes `instance.soft_delete()`, setting `is_deleted = True` and recording the UTC timestamp `deleted_at`.
2. **Hard Deletion (`hard=True`)**: Calling `repository.delete(id, hard=True)` issues `session.delete(instance)` for physical PostgreSQL row deletion.
3. **Query Filtering**: All read operations (`get_by_id`, `list`, `count`, `exists`) automatically filter out soft-deleted records (`is_deleted == False`) unless explicitly overridden with `include_deleted=True`.

---

## 4. Domain Repositories Overview

### `UserRepository` (`app/repositories/user.py`)
- `get_by_email(email: str) -> User | None`
- `get_by_phone(phone_number: str) -> User | None`

### `ConversationRepository` (`app/repositories/conversation.py`)
- `get_latest_active(user_id: UUID) -> Conversation | None`
- `get_by_session_id(session_id: str) -> Conversation | None`

### `RecommendationRepository` (`app/repositories/recommendation.py`)
- `get_active_recommendations(conversation_id: UUID) -> list[Recommendation]`

### `BookingRepository` (`app/repositories/booking.py`)
- `get_by_reference(booking_reference: str) -> Booking | None`
- `get_by_status(status: BookingStatus, offset: int, limit: int) -> list[Booking]`
