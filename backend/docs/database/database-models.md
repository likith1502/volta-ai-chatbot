# VOLTA AI Chatbot - Domain Models Specification

## Overview
This document specifies all 10 domain models defined under `app/models/` for Chapter 2.4. Each domain model represents a core entity in the VOLTA AI Chatbot platform, leveraging SQLAlchemy 2.0 type mapping (`Mapped`, `mapped_column`) and inheriting reusable mixin primitives as mandated by ADR 013 and ADR 014.

---

## Model Inventory

### 1. `User` (`app/models/user.py`)
- **Table**: `users`
- **Inheritance**: `UUIDMixin`, `TimestampMixin`, `SoftDeleteMixin`, `AuditMixin`, `Base`
- **Fields**:
  - `id`: `UUID` (Primary Key, default `uuid.uuid4`)
  - `full_name`: `String(255)` (non-nullable)
  - `email`: `String(255)` (unique, indexed, non-nullable)
  - `phone_number`: `String(50)` (indexed, nullable)
  - `preferred_language`: `String(10)` (default `"en"`, non-nullable)
  - `profile_image_url`: `String(512)` (nullable)
  - `is_active`: `Boolean` (default `True`, non-nullable)
  - `created_at`, `updated_at`: `DateTime(timezone=True)` (UTC)
  - `is_deleted`, `deleted_at`: `Boolean`, `DateTime(timezone=True)`
- **Relationships**: `conversations` (1:N, `cascade="all, delete-orphan"`), `notifications` (1:N, `cascade="all, delete-orphan"`)

### 2. `Conversation` (`app/models/conversation.py`)
- **Table**: `conversations`
- **Inheritance**: `UUIDMixin`, `TimestampMixin`, `SoftDeleteMixin`, `AuditMixin`, `Base`
- **Fields**:
  - `user_id`: `UUID` (Foreign Key `users.id`, `ondelete="CASCADE"`, indexed, non-nullable)
  - `session_id`: `String(100)` (indexed, non-nullable)
  - `source`: `Enum(ConversationSource)` (default `WEB`, non-nullable)
  - `title`: `String(255)` (nullable)
  - `status`: `Enum(ConversationStatus)` (default `ACTIVE`, non-nullable)
  - `started_at`: `DateTime(timezone=True)` (default `func.now()`)
  - `ended_at`: `DateTime(timezone=True)` (nullable)
- **Relationships**: `user` (N:1), `messages` (1:N, `cascade="all, delete-orphan"`), `memories` (1:N, `cascade="all, delete-orphan"`), `intents` (1:N, `cascade="all, delete-orphan"`), `recommendations` (1:N, `cascade="all, delete-orphan"`)

### 3. `Message` (`app/models/message.py`)
- **Table**: `messages`
- **Inheritance**: `UUIDMixin`, `TimestampMixin`, `SoftDeleteMixin`, `AuditMixin`, `Base`
- **Fields**:
  - `conversation_id`: `UUID` (Foreign Key `conversations.id`, `ondelete="CASCADE"`, indexed, non-nullable)
  - `role`: `Enum(MessageRole)` (non-nullable: `USER`, `ASSISTANT`, `SYSTEM`, `TOOL`)
  - `content`: `Text` (non-nullable)
  - `message_type`: `String(50)` (default `"text"`, non-nullable)
  - `sequence_number`: `Integer` (default `1`, non-nullable)
  - `token_count`: `Integer` (nullable)
  - `processing_time_ms`: `Integer` (nullable)
  - `model_used`: `String(100)` (nullable)
- **Relationships**: `conversation` (N:1)

### 4. `Memory` (`app/models/memory.py`)
- **Table**: `memories`
- **Inheritance**: `UUIDMixin`, `TimestampMixin`, `SoftDeleteMixin`, `AuditMixin`, `Base`
- **Fields**:
  - `conversation_id`: `UUID` (Foreign Key `conversations.id`, `ondelete="CASCADE"`, indexed, non-nullable)
  - `memory_key`: `String(100)` (indexed, non-nullable)
  - `memory_value`: `Text` (non-nullable)
  - `memory_type`: `Enum(MemoryType)` (default `EPISODIC`, non-nullable)
  - `confidence_score`: `Float` (default `1.0`, non-nullable)
  - `expires_at`: `DateTime(timezone=True)` (nullable)
- **Relationships**: `conversation` (N:1)

### 5. `Intent` (`app/models/intent.py`)
- **Table**: `intents`
- **Inheritance**: `UUIDMixin`, `TimestampMixin`, `SoftDeleteMixin`, `AuditMixin`, `Base`
- **Fields**:
  - `conversation_id`: `UUID` (Foreign Key `conversations.id`, `ondelete="CASCADE"`, indexed, non-nullable)
  - `intent_name`: `String(100)` (indexed, non-nullable)
  - `confidence_score`: `Float` (default `1.0`, non-nullable)
  - `model_version`: `String(50)` (nullable)
- **Relationships**: `conversation` (N:1), `entities` (1:N, `cascade="all, delete-orphan"`)

### 6. `Entity` (`app/models/entity.py`)
- **Table**: `entities`
- **Inheritance**: `UUIDMixin`, `TimestampMixin`, `SoftDeleteMixin`, `AuditMixin`, `Base`
- **Fields**:
  - `intent_id`: `UUID` (Foreign Key `intents.id`, `ondelete="CASCADE"`, indexed, non-nullable)
  - `entity_type`: `String(100)` (indexed, non-nullable)
  - `entity_value`: `Text` (non-nullable)
  - `confidence_score`: `Float` (default `1.0`, non-nullable)
- **Relationships**: `intent` (N:1)

### 7. `Recommendation` (`app/models/recommendation.py`)
- **Table**: `recommendations`
- **Inheritance**: `UUIDMixin`, `TimestampMixin`, `SoftDeleteMixin`, `AuditMixin`, `Base`
- **Fields**:
  - `conversation_id`: `UUID` (Foreign Key `conversations.id`, `ondelete="CASCADE"`, indexed, non-nullable)
  - `recommendation_type`: `String(50)` (non-nullable)
  - `recommendation_data`: `JSON` (non-nullable)
  - `status`: `Enum(RecommendationStatus)` (default `PENDING`, non-nullable)
  - `confidence_score`: `Float` (default `1.0`, non-nullable)
  - `ranking`: `Integer` (default `1`, non-nullable)
- **Relationships**: `conversation` (N:1), `bookings` (1:N, `cascade="all, delete-orphan"`)

### 8. `Booking` (`app/models/booking.py`)
- **Table**: `bookings`
- **Inheritance**: `UUIDMixin`, `TimestampMixin`, `SoftDeleteMixin`, `AuditMixin`, `Base`
- **Fields**:
  - `recommendation_id`: `UUID` (Foreign Key `recommendations.id`, `ondelete="CASCADE"`, indexed, non-nullable)
  - `booking_reference`: `String(100)` (unique, indexed, non-nullable)
  - `booking_status`: `Enum(BookingStatus)` (default `PENDING`, non-nullable)
  - `provider`: `String(100)` (default `"volta_fleet"`, non-nullable)
  - `external_booking_id`: `String(100)` (indexed, nullable)
  - `booked_at`: `DateTime(timezone=True)` (default `func.now()`)
- **Relationships**: `recommendation` (N:1)

### 9. `Notification` (`app/models/notification.py`)
- **Table**: `notifications`
- **Inheritance**: `UUIDMixin`, `TimestampMixin`, `SoftDeleteMixin`, `AuditMixin`, `Base`
- **Fields**:
  - `user_id`: `UUID` (Foreign Key `users.id`, `ondelete="CASCADE"`, indexed, non-nullable)
  - `notification_type`: `Enum(NotificationType)` (non-nullable)
  - `title`: `String(255)` (non-nullable)
  - `body`: `Text` (non-nullable)
  - `is_read`: `Boolean` (default `False`, non-nullable)
  - `delivery_status`: `String(50)` (default `"sent"`, non-nullable)
  - `sent_at`: `DateTime(timezone=True)` (default `func.now()`)
  - `read_at`: `DateTime(timezone=True)` (nullable)
- **Relationships**: `user` (N:1)

### 10. `AuditLog` (`app/models/audit_log.py`)
- **Table**: `audit_logs`
- **Inheritance**: `UUIDMixin`, `TimestampMixin`, `Base` *(No SoftDeleteMixin, No AuditMixin)*
- **Fields**:
  - `event_type`: `String(100)` (indexed, non-nullable)
  - `actor_id`: `UUID` (indexed, nullable)
  - `resource_type`: `String(100)` (indexed, non-nullable)
  - `resource_id`: `String(255)` (indexed, nullable)
  - `event_metadata`: `JSON` (column name `"event_metadata"`, nullable)
  - `ip_address`: `String(45)` (nullable)
