# VOLTA AI Chatbot - Database Design Principles & Constitution

## 1. Database Philosophy
The database is the foundational single source of truth for the VOLTA AI Chatbot platform. Data integrity, strict schema evolution, high throughput async execution, and zero data loss guide all data architecture decisions.

---

## 2. UUID Policy
- **Primary Keys**: Every database table **must** use a Universally Unique Identifier (UUID v4) as its primary key.
- **Security**: Prevents sequential ID enumeration attacks on public API endpoints.
- **Distributed Scale**: Enables multi-region data generation without primary key collisions.

---

## 3. Timestamp Policy
- **Standard Columns**: Every database table **must** include `created_at` and `updated_at` columns.
- **Timezone Standard**: All timestamps must be stored in UTC (`timezone=True`).
- **Automation**: Timestamps are managed automatically via SQLAlchemy default handlers and Mixins.

---

## 4. Naming Convention Policy
- **Table Names**: Plural snake_case (`users`, `conversations`, `rides`, `notifications`, `saved_places`).
- **Column Names**: Singular snake_case (`user_id`, `created_at`, `vehicle_type`).
- **Constraint Conventions**: All constraints must follow explicit PostgreSQL naming conventions (`pk_*`, `fk_*`, `uq_*`, `ck_*`, `ix_*`).

---

## 5. Foreign Key Policy
- **Explicit Relationships**: All relationships between entities must be declared using explicit Foreign Key constraints (`fk_*`).
- **Indexed FKs**: Every foreign key column must have a corresponding B-Tree index to optimize JOIN query performance.

---

## 6. Indexing Philosophy
- **Targeted Indexing**: Create B-Tree indexes on columns frequently used in `WHERE`, `JOIN`, and `ORDER BY` clauses.
- **Unique Constraints**: Enforce uniqueness at the database engine level via unique indexes (`uq_*`).

---

## 7. Soft Delete Policy
- **Non-Destructive Deletion**: Tables containing historical travel, conversational, or financial data must utilize soft deletion (`is_deleted`, `deleted_at`).
- **Data Preservation**: Raw records are never permanently purged from disk during normal application operation.

---

## 8. Audit Policy
- **Data Lineage**: Critical business entities track mutation lineage (`created_by`, `updated_by`).
- **Compliance**: Provides verifiable audit trails for regulatory compliance and dispute resolution.

---

## 9. Migration Policy
- **Zero Manual DDL**: Never execute manual SQL (`CREATE TABLE`, `ALTER TABLE`) in production environments.
- **100% Alembic Governance**: All database schema modifications must be executed via version-controlled Alembic migration scripts.

---

## 10. Repository Policy
- **Encapsulated Access**: All database reads, writes, updates, and deletes must pass through Repository pattern abstractions (`app/repositories/`).
- **No Direct Querying**: FastAPI route handlers and business services must never execute raw SQL or ORM queries directly.

---

## 11. Async Database Policy
- **Non-Blocking I/O**: Every database operation must use Async SQLAlchemy (`AsyncSession`) and `asyncpg` drivers.
- **Zero Synchronous Calls**: Synchronous database drivers or blocking queries are strictly forbidden in application code.

---

## 12. Performance Philosophy
- **Connection Pooling**: Managed via `AsyncEngine` using pre-ping connection checks (`pool_pre_ping=True`) and pool recycling (`pool_recycle=3600`).
- **Optimized Fetching**: Avoid `SELECT *` queries; select only required columns or use eager loading (`joinedload`/`selectinload`) to prevent N+1 query problems.

---

## 13. Security Philosophy
- **Parameterized Queries**: All queries must be executed via SQLAlchemy ORM or parameterized statements to prevent SQL injection.
- **Secret Isolation**: Database passwords and host URLs must strictly load from environment settings (`settings.py`), never hardcoded in source files.

---

## 14. Future Scaling Philosophy
- **Read Replicas**: Architecture supports splitting read-heavy queries to read-replicas via custom session routing.
- **Sharding Readiness**: UUID primary keys and decoupled modular tables ensure readiness for horizontal database sharding.

---

## 15. Database Review Checklist
- [ ] Table name is plural `snake_case`
- [ ] Uses UUID v4 primary key
- [ ] Contains `created_at` and `updated_at` in UTC
- [ ] Foreign keys explicitly declared and indexed
- [ ] Follows `POSTGRES_NAMING_CONVENTION`
- [ ] Accompanied by a versioned Alembic migration script
