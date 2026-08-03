# Milestone 2 Implementation Plan: Infrastructure Layer (Updated Roadmap)

## Overview
This document details the refined architectural sequence, implementation steps, file deliverables, and testing strategy for **Milestone 2 (Infrastructure Layer)** of the VOLTA AI Chatbot backend.

---

## Refined Infrastructure Roadmap Flow

```
1. Infrastructure (PostgreSQL + Async SQLAlchemy)  <-- COMPLETED
        │
        v
2. Alembic (Database Migration Engine)
        │
        v
3. Base Mixins (TimestampMixin, UUIDMixin, SoftDeleteMixin, AuditMixin)
        │
        v
4. Domain Models (User, Ride, Conversation, Notification, SavedPlace)
        │
        v
5. Repository Pattern (Generic Base & Concrete Repositories)
        │
        v
6. Redis (In-Memory Cache & Session Layer)
        │
        v
7. Infrastructure Complete & Integrated Validation
```

---

## Architectural Rationale

### Why Base Mixins Before Domain Models?
Entities such as `User`, `Ride`, `Conversation`, `Notification`, and `SavedPlace` require uniform system columns (`id`, `created_at`, `updated_at`, `is_deleted`). Implementing mixins first guarantees 100% field consistency across all models without DRY code duplication.

### Why Domain Models Before Repository Pattern?
Concrete repositories (e.g. `UserRepository`, `BookingRepository`) depend on concrete SQLAlchemy ORM models. Defining ORM models prior to repositories prevents writing empty generic abstractions and ensures type-safe CRUD operations.

---

## Execution Order Breakdown

### Step 1: PostgreSQL & Async SQLAlchemy Foundation *(Completed)*
- **Files**: `app/database/connection.py`, `app/database/session.py`, `app/database/base.py`, `app/database/health.py`
- **Output**: Async engine singleton (`get_engine()`), `AsyncSessionLocal`, `DeclarativeBase`, and `check_database_health()`.

### Step 2: Alembic Database Migration Engine
- **Files**: `alembic.ini`, `migrations/env.py`, `migrations/versions/`
- **Output**: Fully configured async migration environment.

### Step 3: Base Database Mixins
- **Files**: `app/database/mixins.py`
- **Output**: `UUIDMixin`, `TimestampMixin`, `SoftDeleteMixin`, `AuditMixin`.

### Step 4: Core Domain Models
- **Files**: `app/models/user.py`, `app/models/ride.py`, `app/models/conversation.py`, `app/models/notification.py`, `app/models/saved_place.py`
- **Output**: Concrete ORM models inheriting from `Base` and `Mixins`.

### Step 5: Repository Pattern
- **Files**: `app/database/repository.py`, `app/repositories/user_repository.py`, etc.
- **Output**: `BaseRepository[T]` interface and concrete data access repositories.

### Step 6: Redis Caching & Session Layer
- **Files**: `app/cache/redis.py`, `app/cache/service.py`
- **Output**: Asynchronous Redis connection client and cache service.

### Step 7: Final Infrastructure Integration & Validation
- **Files**: `app/api/v1/health.py` (upgraded), `tests/`
- **Output**: Full end-to-end integration tests verifying DB, migrations, repositories, and Redis.
