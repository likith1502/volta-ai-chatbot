# VOLTA AI Chatbot - Relationship & Loading Strategy Guidelines

## 1. Directives & Standards
- **Explicit `back_populates`**: Every SQLAlchemy relationship **must** pair a corresponding `back_populates` directive on both ends of the relationship. Legacy `backref` is forbidden.
- **Explicit Foreign Key Cascades**: Foreign key columns must explicitly state `ondelete="CASCADE"` to synchronize database-level cascade deletions with SQLAlchemy ORM state.

---

## 2. Eager Loading Philosophy (`lazy="selectin"`)
- **Collection Relationships**: 1:N collection attributes (`User.conversations`, `Conversation.messages`, `Conversation.recommendations`, etc.) are configured with `lazy="selectin"`.
- **N+1 Query Prevention**: `selectin` loading issues a second targeted `IN (...)` query when fetching parent instances, avoiding N+1 performance bottlenecks while remaining fully compatible with Async SQLAlchemy.
- **Parent Relationships**: Reverse N:1 relationship access (e.g. `Message.conversation`) defaults to standard lazy loading unless explicitly joined in query logic.
