# ADR 013: Model Inheritance Strategy & Composable Mixins

## Status
Accepted

## Date
2026-08-03

## Context
Every database domain model in the VOLTA AI Chatbot platform requires core operational capabilities such as primary key identification, creation/update timestamp tracking, non-destructive soft deletion, and audit tracking. A foundational architectural decision was required to determine how shared database capabilities should be inherited across ORM models (`User`, `Ride`, `Conversation`, `Notification`, `SavedPlace`).

---

## Options Considered

### Option A: Monolithic Single `BaseModel`

In this approach, a single parent class inherits from `DeclarativeBase` and hardcodes all primary keys, timestamps, soft delete flags, and audit columns into one base class.

```python
# Anti-Pattern Concept
class BaseModel(DeclarativeBase):
    id = Column(UUID, primary_key=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    is_deleted = Column(Boolean)
    deleted_at = Column(DateTime)
    created_by = Column(UUID)
    updated_by = Column(UUID)
```

- **Advantages**:
  - Simple single inheritance line (`class User(BaseModel)`).
- **Disadvantages**:
  - Violates Single Responsibility Principle (SRP).
  - Rigid and un-customizable.
  - Forces every entity (including immutable logs, lookup tables, and join tables) to inherit unnecessary columns.
  - Results in a large monolithic base class that is difficult to maintain and test.

---

### Option B: Composable Mixins (Selected Strategy)

In this approach, each database concern (`UUIDMixin`, `TimestampMixin`, `SoftDeleteMixin`, `AuditMixin`) is isolated into an independent, reusable mixin class in `app/database/mixins.py`. Domain models inherit `Base` alongside only the specific mixins they require.

```python
# Selected Pattern Concept
class User(UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "users"
```

- **Advantages**:
  - Enforces Composition Over Inheritance and Single Responsibility Principle (SRP).
  - Maximum flexibility: Models inherit strictly what they need.
  - High testability: Mixin behaviors can be tested in isolation.
  - Clean separation of concerns and maintainable class boundaries.
- **Disadvantages**:
  - Slightly longer inheritance lists on class declarations.
  - Requires developers to understand mixin composition.

---

## Decision
VOLTA AI Chatbot officially adopts **Option B: Composable Mixins**. Every database capability is modularized into an independent mixin class in `app/database/mixins.py`. Future ORM models compose only the functionality they require.

---

## Rationale
This decision directly advances key engineering goals:
- **SOLID Principles**: Each mixin has a single responsibility. Models are open for extension through composition without modifying core base classes.
- **Clean Architecture**: Decouples cross-cutting database concerns from domain attributes.
- **Code Reuse & Maintainability**: Modifying mixin implementation (e.g. updating timestamp timezone handling) instantly propagates across all consuming models without code duplication.
- **Testability**: Allows unit testing mixin behaviors (`soft_delete()`, `restore()`) on generic dummy models independently of domain business rules.

---

## Code Examples

### Example 1: Standard Mutable Domain Entity (`User`)
Consumes all mixins because it requires primary key identification, timestamp tracking, soft deletion, and user mutation auditing:

```python
class User(UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "users"
    # Domain attributes...
```

### Example 2: Immutable Event Log Entity (`AuditLog`)
Consumes only `UUIDMixin` and `TimestampMixin` because soft deletion and mutation auditing are irrelevant for append-only audit records:

```python
class AuditLog(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "audit_logs"
    # Immutable log attributes...
```

---

## Architecture Diagram

```
                                DeclarativeBase (Base)
                                          ▲
                                          │
                  ┌───────────────────────┼───────────────────────┐
                  │                       │                       │
              UUIDMixin            TimestampMixin          SoftDeleteMixin
                  │                       │                       │
                  └───────────────────────┼───────────────────────┘
                                          │
                                     AuditMixin
                                          │
                                          ▼
                                Future Domain Models
                           (app/models/user.py, etc.)
```

---

## Consequences

### Positive
- Small, isolated, reusable database components.
- Zero column duplication across models.
- Targeted unit test coverage per mixin.
- Flexible inheritance tailored per entity requirement.

### Negative
- Developers must understand mixin composition order (`UUIDMixin`, `TimestampMixin`, ..., `Base`).

---

## Project Rule
The preferred project standard is to compose models from reusable mixins rather than introducing a monolithic BaseModel. Any deviation from this standard should be justified through a new Architecture Decision Record.
