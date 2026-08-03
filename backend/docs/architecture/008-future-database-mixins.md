# Architectural Plan: Future Database Mixins

## Overview
To prevent boilerplate repetition across domain entities (Users, Conversations, Bookings, Recommendations), common columns and behaviors will be modularized using SQLAlchemy 2.0 Mixins under `app/database/mixins.py`.

---

## 1. TimestampMixin

### Purpose
Automatically populates and updates record creation and modification timestamps in UTC.

### Future Use
- `created_at`: `Mapped[datetime]` set to `datetime.now(timezone.utc)` on `INSERT`.
- `updated_at`: `Mapped[datetime]` updated to `datetime.now(timezone.utc)` on `UPDATE`.

### Advantages
- Eliminates manual timestamp assignment across business services.
- Ensures timezone-aware consistent storage across PostgreSQL databases.

---

## 2. UUIDMixin

### Purpose
Provides universally unique identifier (UUID v4) primary keys rather than auto-incrementing integers.

### Future Use
- `id`: `Mapped[UUID]` generated via `uuid.uuid4()` default.

### Advantages
- Prevents ID enumeration attacks on public API endpoints.
- Simplifies distributed database sharding and cross-system data sync without primary key collisions.

---

## 3. SoftDeleteMixin

### Purpose
Supports logical record deletion without physically purging rows from disk.

### Future Use
- `is_deleted`: `Mapped[bool]` defaulted to `False`.
- `deleted_at`: `Mapped[Optional[datetime]]` set when a soft delete action occurs.

### Advantages
- Preserves historical travel and transaction data for AI model training and compliance.
- Enables record restoration in recovery scenarios.

---

## 4. AuditMixin

### Purpose
Tracks entity lineage by recording the user or system component responsible for mutations.

### Future Use
- `created_by`: `Mapped[Optional[UUID]]` user ID of the creator.
- `updated_by`: `Mapped[Optional[UUID]]` user ID of the last modifier.

### Advantages
- Full compliance and security traceability for auditing data changes across ride bookings and profile updates.
