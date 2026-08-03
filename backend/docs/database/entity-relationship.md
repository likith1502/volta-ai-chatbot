# VOLTA AI Chatbot - Entity Relationship (ER) Blueprint

## 1. High-Level Entity Relationship Diagram

```
                             +-------------------+
                             |       User        |
                             +-------------------+
                               │               │
                      1:N      │               │ 1:N
             ┌─────────────────┘               └─────────────────┐
             ▼                                                   ▼
   +-------------------+                               +-------------------+
   |   Conversation    |                               |   Notification    |
   +-------------------+                               +-------------------+
     │    │    │    │
 1:N │ 1:N│ 1:N│ 1:N│
  ┌──┘    │    │    └──┐
  ▼       ▼    ▼       ▼
+---+   +---+ +---+  +-------------------+
|Msg|   |Mem| |Int|  |  Recommendation   |
+---+   +---+ +---+  +-------------------+
                │              │
             1:N│           1:N│
                ▼              ▼
              +---+          +---+
              |Ent|          |Bkg|
              +---+          +---+
```

---

## 2. Comprehensive Cardinality Table

| Parent Entity | Relationship | Child Entity | Foreign Key Column | OnDelete Directive | Loading Strategy |
| :--- | :---: | :--- | :--- | :---: | :---: |
| `User` | **1 : N** | `Conversation` | `conversations.user_id` | `CASCADE` | `lazy="selectin"` |
| `User` | **1 : N** | `Notification` | `notifications.user_id` | `CASCADE` | `lazy="selectin"` |
| `Conversation` | **1 : N** | `Message` | `messages.conversation_id` | `CASCADE` | `lazy="selectin"` |
| `Conversation` | **1 : N** | `Memory` | `memories.conversation_id` | `CASCADE` | `lazy="selectin"` |
| `Conversation` | **1 : N** | `Intent` | `intents.conversation_id` | `CASCADE` | `lazy="selectin"` |
| `Conversation` | **1 : N** | `Recommendation` | `recommendations.conversation_id` | `CASCADE` | `lazy="selectin"` |
| `Intent` | **1 : N** | `Entity` | `entities.intent_id` | `CASCADE` | `lazy="selectin"` |
| `Recommendation` | **1 : N** | `Booking` | `bookings.recommendation_id` | `CASCADE` | `lazy="selectin"` |

---

## 3. Schema Normalization & Constraint Design
- **First Normal Form (1NF)**: Every column contains atomic scalar or structured JSON values.
- **Second Normal Form (2NF)**: All non-key attributes fully depend on the primary key UUID v4 (`id`).
- **Third Normal Form (3NF)**: Transitive dependencies are eliminated. Child tables hold explicit Foreign Key references to their parent tables.
- **Constraint Governance**: Foreign keys (`fk_*`), primary keys (`pk_*`), unique constraints (`uq_*`), and indexes (`ix_*`) adhere to `POSTGRES_NAMING_CONVENTION` declared in `app/database/base.py`.
