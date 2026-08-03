# VOLTA AI Chatbot Backend Architecture

---

## 1. Project Overview

### Purpose
VOLTA AI Chatbot is an enterprise-grade, multi-modal conversational AI ecosystem built to transform urban mobility, ride booking, and personalized travel recommendations.

### Goals
- Deliver real-time, context-aware conversational ride booking and assistance.
- Establish a decoupled backend capable of powering both messaging (text) chatbots and low-latency voice agents.
- Ensure modular extensibility for third-party transport, hospitality, and event integrations.

### Vision
To serve as the universal intelligence layer (Shared AI Brain) for urban transit, predicting user needs before explicit queries and seamlessly executing complex travel workflows.

### Scope
- Core backend service architecture using FastAPI, LangGraph, PostgreSQL, and Redis.
- Orchestration of intent recognition, entity extraction, context tracking, memory management, predictive analytics, and ride recommendation.
- Notification dispatch and external API integrations (e.g., Google Maps).

---

## 2. Project Objectives

### Business Objectives
- Reduce friction in ride discovery and booking through conversational interfaces.
- Maximize user retention via hyper-personalized, context-driven recommendations.
- Provide high platform reliability and low response latency.

### Technical Objectives
- Build a modular, decoupled Python architecture adhering to clean architecture principles.
- Maintain high test coverage with automated unit and integration tests.
- Support horizontal scaling with asynchronous I/O and cached state management.

### AI Objectives
- Maintain high intent classification and entity extraction precision.
- Maintain persistent multi-turn conversational state across sessions (Shared AI Brain).
- Dynamically adapt recommendations based on historical patterns and predictive models.

### Scalability Goals
- Handle thousands of concurrent active conversations.
- Maintain sub-second API response times for standard queries.
- Support low-latency audio stream processing for future voice agent capabilities.

---

## 3. High-Level Backend Architecture

```
+-----------------------------------------------------------------------+
|                              Testing UI                               |
+-----------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                            FastAPI Backend                            |
+-----------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                         Conversation Manager                          |
+-----------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                             Intent Engine                             |
+-----------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                             Entity Engine                             |
+-----------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                            Context Engine                             |
+-----------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                             Memory Engine                             |
+-----------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                           Prediction Engine                           |
+-----------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                         Recommendation Engine                         |
+-----------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                             Ride Booking                              |
+-----------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                             Notifications                             |
+-----------------------------------------------------------------------+
                                    |
                 +------------------+------------------+
                 |                                     |
                 v                                     v
+---------------------------------+   +---------------------------------+
|            Database             |   |              Redis              |
|          (PostgreSQL)           |   |       (Cache & State Store)     |
+---------------------------------+   +---------------------------------+
```

---

## 4. Folder Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   ├── booking/
│   ├── cache/
│   ├── config/
│   ├── context/
│   ├── conversation/
│   ├── core/
│   ├── database/
│   ├── entities/
│   ├── intent/
│   ├── llm/
│   ├── memory/
│   ├── middleware/
│   ├── models/
│   ├── notifications/
│   ├── prediction/
│   ├── profile/
│   ├── prompts/
│   ├── recommendation/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   ├── main.py
│   └── __init__.py
├── logs/
├── migrations/
├── requirements/
├── scripts/
├── tests/
├── .env
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

### Folder Responsibilities

#### `backend/app/api/`
- **Purpose**: Entry points for HTTP endpoints and API routing.
- **Responsibilities**: Route definition, request/response validation mapping, rate limiting hooks.
- **Future Contents**: API router modules (v1/chat, v1/booking, v1/profile, v1/health).

#### `backend/app/booking/`
- **Purpose**: Ride booking logic and ride state transitions.
- **Responsibilities**: Managing booking lifecycle (quote, match, active, completed, cancelled).
- **Future Contents**: Booking domain handlers, ride dispatch logic, partner API abstractions.

#### `backend/app/cache/`
- **Purpose**: Low-latency caching layer interface.
- **Responsibilities**: Session caching, temporary token storage, rate limit counters.
- **Future Contents**: Redis client initialization, key generators, TTL strategies.

#### `backend/app/config/`
- **Purpose**: Environment configuration management.
- **Responsibilities**: Loading `.env` variables, setting default application parameters.
- **Future Contents**: Pydantic BaseSettings objects, environment validation schema.

#### `backend/app/context/`
- **Purpose**: Short-term dialogue context tracking.
- **Responsibilities**: Maintaining active conversation topic, turn count, slot filling status.
- **Future Contents**: Context window managers, slot state machines.

#### `backend/app/conversation/`
- **Purpose**: Main conversation workflow orchestration.
- **Responsibilities**: Managing pipeline execution flow between intent, entity, context, and memory.
- **Future Contents**: LangGraph state graph definitions, conversation orchestrators.

#### `backend/app/core/`
- **Purpose**: Core application security and global utilities.
- **Responsibilities**: Security primitives, authentication policies, global error handling.
- **Future Contents**: JWT utilities, password hashing, custom exceptions.

#### `backend/app/database/`
- **Purpose**: Relational database persistence setup.
- **Responsibilities**: Database engine creation, session factory management, base model definitions.
- **Future Contents**: SQLAlchemy session setup, DB transaction managers.

#### `backend/app/entities/`
- **Purpose**: Entity extraction logic.
- **Responsibilities**: Extracting origin, destination, time, ride type, passenger count from input.
- **Future Contents**: Entity parsing pipelines, regex validators, LLM entity extractors.

#### `backend/app/intent/`
- **Purpose**: Intent classification engine.
- **Responsibilities**: Categorizing user input into actionable intents (e.g., book_ride, check_fare, cancel).
- **Future Contents**: Intent classifiers, confidence scoring utilities.

#### `backend/app/llm/`
- **Purpose**: Integration with Large Language Models and AI frameworks.
- **Responsibilities**: Abstracting LLM calls, managing provider fallbacks, output parsing.
- **Future Contents**: Provider clients (OpenAI, Anthropic), LangChain/LangGraph abstractions.

#### `backend/app/memory/`
- **Purpose**: Long-term conversational and user history memory.
- **Responsibilities**: Persisting and retrieving past interactions, preference memory.
- **Future Contents**: Vector store connectors, conversation summary generators.

#### `backend/app/middleware/`
- **Purpose**: FastAPI request/response interceptors.
- **Responsibilities**: Request ID generation, logging, CORS, security headers, performance timing.
- **Future Contents**: Custom middleware classes.

#### `backend/app/models/`
- **Purpose**: Database domain models (ORM).
- **Responsibilities**: Defining PostgreSQL table schemas, relationships, indexes.
- **Future Contents**: SQLAlchemy ORM models (User, Conversation, Booking, Preference).

#### `backend/app/notifications/`
- **Purpose**: Dispatching user notifications.
- **Responsibilities**: Generating SMS, push notifications, webhooks for booking updates.
- **Future Contents**: FCM integration, Twilio/SMS drivers, notification templates.

#### `backend/app/prediction/`
- **Purpose**: Predictive analytics for user intent and travel needs.
- **Responsibilities**: Predicting destination preferences, routine ride timing, demand estimation.
- **Future Contents**: Predictive heuristics, user routine evaluation algorithms.

#### `backend/app/profile/`
- **Purpose**: User profile and preference management.
- **Responsibilities**: Storing home/work locations, ride tier preferences, payment profiles.
- **Future Contents**: Profile domain logic, user preference resolvers.

#### `backend/app/prompts/`
- **Purpose**: Centralized prompt templates directory.
- **Responsibilities**: Managing versioned system prompts, formatting template variables.
- **Future Contents**: Text prompt files, prompt version registry.

#### `backend/app/recommendation/`
- **Purpose**: Smart recommendation engine.
- **Responsibilities**: Suggesting optimal ride types, alternative departure times, cost-saving options.
- **Future Contents**: Recommendation scoring algorithms, route options rankers.

#### `backend/app/schemas/`
- **Purpose**: Data transfer objects (DTO) and API payload validation.
- **Responsibilities**: Validating incoming JSON requests, serializing API response models.
- **Future Contents**: Pydantic validation schemas.

#### `backend/app/services/`
- **Purpose**: External integrations and business service abstractions.
- **Responsibilities**: Third-party API communication (e.g., Google Maps API, payment gateways).
- **Future Contents**: Distance/Matrix service wrappers, Geocoding service wrappers.

#### `backend/app/utils/`
- **Purpose**: General-purpose helper functions.
- **Responsibilities**: Date/time formatting, string manipulation, math helpers.
- **Future Contents**: Helper utility functions.

#### `backend/logs/`
- **Purpose**: Local storage for application execution logs.
- **Responsibilities**: Storing runtime log outputs.
- **Future Contents**: `app.log`, `error.log`, `requests.log`.

#### `backend/migrations/`
- **Purpose**: Database schema migration tracking.
- **Responsibilities**: Storing Alembic migration scripts.
- **Future Contents**: Alembic version files and environment configuration.

#### `backend/requirements/`
- **Purpose**: Environment-specific dependency definitions.
- **Responsibilities**: Separating base, development, testing, and production requirements.
- **Future Contents**: `base.txt`, `dev.txt`, `prod.txt`.

#### `backend/scripts/`
- **Purpose**: Maintenance and operations scripts.
- **Responsibilities**: Database seed scripts, health checks, background task utilities.
- **Future Contents**: `seed_db.py`, `run_migrations.py`.

#### `backend/tests/`
- **Purpose**: Automated test suites.
- **Responsibilities**: Unit tests, integration tests, API route tests.
- **Future Contents**: `conftest.py`, `test_api/`, `test_services/`.

---

## 5. Module Responsibilities

### Conversation Manager
- **Purpose**: Orchestrates the multi-turn conversational flow.
- **Input**: User message text, session identifier, user credentials.
- **Output**: Structured response object containing assistant reply, suggested actions, and updated state.
- **Dependencies**: Intent Engine, Entity Engine, Context Engine, Memory Engine, LLM.

### Intent Detection
- **Purpose**: Identifies user goals from textual inputs.
- **Input**: User message string, current conversation state.
- **Output**: Primary intent, secondary intents, confidence score.
- **Dependencies**: LLM, Prompts module.

### Entity Extraction
- **Purpose**: Extracts structured attributes from unstructured text.
- **Input**: User message string, active intent context.
- **Output**: Extracted entity dictionary (e.g., origin, destination, time, vehicle_type).
- **Dependencies**: Services (Geocoding), LLM.

### Context Engine
- **Purpose**: Tracks transient dialogue state across consecutive turns.
- **Input**: Extracted entities, previous turn context, active intent.
- **Output**: Consolidated active dialogue context, missing required slots list.
- **Dependencies**: Redis Cache.

### Memory Engine
- **Purpose**: Retains long-term interaction history and episodic memory.
- **Input**: User ID, conversation transcripts, finalized ride details.
- **Output**: Historical conversation summaries, user habit profile data.
- **Dependencies**: Database (PostgreSQL), Vector Store / Redis.

### Prediction Engine
- **Purpose**: Forecasts travel needs based on temporal and historical patterns.
- **Input**: User ID, current timestamp, location context.
- **Output**: Predicted destination candidates, suggested departure windows.
- **Dependencies**: Memory Engine, Profile Module.

### Recommendation Engine
- **Purpose**: Generates tailored ride options and alternatives.
- **Input**: Origin/destination pair, predicted intent, user preferences.
- **Output**: Ranked list of ride options with estimated pricing and time.
- **Dependencies**: Services (Google Maps), Profile Module.

### Booking
- **Purpose**: Manages the lifecycle of a ride booking.
- **Input**: Selected recommendation option, user ID, payment token.
- **Output**: Booking confirmation record, status updates.
- **Dependencies**: Database, Notifications Module.

### Notifications
- **Purpose**: Dispatches transactional updates across communication channels.
- **Input**: Recipient ID, channel preference, notification payload.
- **Output**: Delivery confirmation receipt.
- **Dependencies**: External Push/SMS Services.

### Profile
- **Purpose**: Manages persistent user preferences and saved data.
- **Input**: User ID, updated preference attributes.
- **Output**: User profile object.
- **Dependencies**: Database.

### Database
- **Purpose**: Persistent relational store.
- **Input**: Structured domain models, SQL queries.
- **Output**: Persisted records, transaction status.
- **Dependencies**: PostgreSQL engine, SQLAlchemy.

### Redis
- **Purpose**: High-speed in-memory store for session caching and state.
- **Input**: Key-value pairs, expiration TTLs.
- **Output**: Cached state objects, rate limit status.
- **Dependencies**: Redis Server.

### LLM
- **Purpose**: Interface for generative AI models.
- **Input**: Formatted prompt templates, context parameters.
- **Output**: Raw generated response text, structured JSON outputs.
- **Dependencies**: Third-party LLM API providers.

---

## 6. Technology Stack

| Technology | Purpose | Reason | Alternative | Recommendation |
| :--- | :--- | :--- | :--- | :--- |
| **Python** | Primary Programming Language | Excellent AI ecosystem, clean syntax, async support | Node.js, Go | **Python 3.11+** |
| **FastAPI** | Web Framework | High performance, native async support, automatic OpenAPI docs | Django, Flask | **FastAPI** |
| **PostgreSQL** | Primary Relational Database | ACIDS compliance, strong JSON support, spatial extension (PostGIS) | MySQL, MongoDB | **PostgreSQL 15+** |
| **Redis** | In-Memory Cache & Session Store | Ultra-low latency, native data structure support, Pub/Sub | Memcached | **Redis 7+** |
| **SQLAlchemy** | Python ORM | Enterprise-grade query builder, robust unit of work pattern | Tortoise ORM, Peewee | **SQLAlchemy 2.0+** |
| **Alembic** | Database Migration Tool | Seamless integration with SQLAlchemy schema tracking | Flyway | **Alembic** |
| **JWT** | Authentication Mechanism | Stateless, secure bearer token protocol | Session Cookies | **PyJWT** |
| **LangGraph** | AI Orchestration & State Graphs | Built for cyclic agentic flows, multi-turn state persistence | LangChain Sequential | **LangGraph** |
| **Docker** | Containerization | Consistent development and production environment execution | Bare Metal, VMs | **Docker** |
| **Nginx** | Reverse Proxy & SSL Termination | High concurrency handling, static asset serving, load balancing | Traefik, Caddy | **Nginx** |
| **Celery** | Distributed Task Queue | Asynchronous background task execution (SMS, email sending) | ARQ, RQ | **Celery** |
| **Pydantic** | Data Validation & Settings | Strict type verification, seamless FastAPI integration | Marshmallow, Cerberus | **Pydantic v2** |
| **Google Maps** | Maps, Routes, & Geocoding | Best-in-class location data, route matrix calculation | Mapbox, OpenStreetMap | **Google Maps API** |

---

## 7. Coding Standards

### Naming Conventions
- **Folders**: Lowercase with hyphens or underscores where applicable (`conversation`, `v1`).
- **Files**: Lowercase snake_case (`main.py`, `ride_service.py`).
- **Classes**: PascalCase (`ConversationManager`, `BookingRepository`).
- **Functions/Methods**: Lowercase snake_case (`extract_entities()`, `get_user_by_id()`).
- **Variables**: Lowercase snake_case (`active_session_id`, `destination_address`).
- **Constants**: Uppercase SNAKE_CASE (`MAX_RETRY_ATTEMPTS`, `DEFAULT_PAGE_SIZE`).

### Import Order
Group imports in the following order separated by an empty line:
1. Standard library imports (e.g., `os`, `sys`, `typing`).
2. Third-party package imports (e.g., `fastapi`, `pydantic`, `sqlalchemy`).
3. Local application imports (e.g., `app.core.config`, `app.models`).

### Formatting Rules
- Follow **PEP 8** guidelines.
- Use explicit type annotations on all function signatures.
- Maximum line length of **88 characters** (Black standard).

### Documentation Rules
- Every public class and function must include a descriptive docstring (Google docstring style).
- Avoid obvious comments; document the *why*, not the *how*.

---

## 8. API Standards

### Standard JSON Response
All API endpoints must return a uniform envelope structure:

```json
{
  "success": true,
  "data": {},
  "error": null,
  "meta": {
    "timestamp": "2026-08-03T15:42:36Z",
    "request_id": "req-12345-67890"
  }
}
```

### HTTP Status Codes
- `200 OK`: Successful operation.
- `201 Created`: Resource successfully created.
- `400 Bad Request`: Client validation error or malformed payload.
- `401 Unauthorized`: Missing or invalid authentication token.
- `403 Forbidden`: Authenticated user lacks required permission.
- `404 Not Found`: Requested resource does not exist.
- `422 Unprocessable Entity`: Data schema validation failure.
- `500 Internal Server Error`: Unhandled server-side failure.

### Error Handling Philosophy
- Never leak raw stack traces or internal exception details to the user.
- Intercept application exceptions with global FastAPI middleware and transform them into standardized error responses.

### Versioning
- All public endpoints must be scoped under URI versioning: `/api/v1/`.

### Authentication
- Authentication is enforced via Bearer JWT tokens passed in the HTTP `Authorization` header.

---

## 9. Logging Standards

### Purpose
Provide observability, fast debugging capability, and performance monitoring without compromising sensitive user privacy data.

### Log Levels
- `DEBUG`: Fine-grained diagnostic information for local development.
- `INFO`: Standard operational messages (e.g., service startup, user login).
- `WARNING`: Exceptional events that do not halt operation.
- `ERROR`: Runtime errors or exception conditions requiring developer attention.
- `CRITICAL`: System-wide failure requiring immediate intervention.

### Request IDs
- Every HTTP request is assigned a unique `X-Request-ID` UUID by middleware.
- Request IDs are propagated through all log outputs across all internal modules.

### Log Storage
- Logs are formatted in structured JSON for machine parsing.
- Written to stdout in containers and persisted locally under `backend/logs/` during development.

### Future Monitoring
- Preparation for aggregation into centralized tools (ELK Stack, Datadog, or Grafana Loki).

---

## 10. Development Phases

```
Phase 1: Project Setup ------------> Base directory & configuration scaffold
Phase 2: Backend Foundation ------> Core FastAPI, logging, middleware setup
Phase 3: Database -----------------> PostgreSQL & SQLAlchemy ORM integration
Phase 4: Redis --------------------> Redis client & caching layer setup
Phase 5: Authentication -----------> JWT token issuance & authorization guards
Phase 6: Conversation -------------> LangGraph workflow graph initialization
Phase 7: Intent -------------------> Intent detection engine implementation
Phase 8: Entity -------------------> Entity extraction & validation pipeline
Phase 9: Context ------------------> Short-term turn state tracking
Phase 10: Memory ------------------> Long-term memory & history persistence
Phase 11: Prediction --------------> User behavior prediction heuristics
Phase 12: Recommendation -----------> Dynamic ride option generation & ranking
Phase 13: Booking -----------------> Ride booking engine & state machine
Phase 14: Notifications -----------> Transactional notification dispatches
Phase 15: Testing -----------------> Comprehensive unit & integration testing
Phase 16: Deployment --------------> Containerized CI/CD release pipeline
```

---

## 11. Engineering Principles

### Single Responsibility Principle (SRP)
Each module, class, and function must have one, and only one, reason to change.

### Modular Design
Build independent, pluggable components that can be tested, updated, or replaced in isolation.

### Dependency Injection
Pass dependencies explicitly (e.g., via FastAPI dependency system) rather than hardcoding concrete instances inside classes.

### Loose Coupling
Modules interact through abstract interfaces without relying on internal implementation details of sibling components.

### High Cohesion
Keep related functions and domain logic logically grouped together within their designated folder modules.

### Scalability
Design stateless application tiers so backend nodes can scale horizontally behind a load balancer.

### Maintainability
Prioritize readable, explicit code with thorough type safety over clever or obscure shortcuts.

### Readability
Self-documenting code with clear variable names and consistent structure takes precedence over micro-optimizations.

### Security
Validate all input boundaries strictly, apply principle of least privilege, and sanitize inputs to prevent injection vectors.

---

## 12. Git Workflow

```
               main (Production Ready)
                 ^
                 |  (Release Branch Merge)
              release/*
                 ^
                 |  (Integration)
              develop (Active Development)
               ^   ^
              /     \
    feature/*         bugfix/*
```

### Branching Strategy
- **`main`**: Production-ready code only. Tagged with semantic versions (e.g., `v1.0.0`).
- **`develop`**: Integration branch for upcoming feature releases.
- **`feature/*`**: Feature branches branched off `develop` (e.g., `feature/intent-engine`).
- **`bugfix/*`**: Fixes branched off `develop` for resolving development issues.
- **`release/*`**: Staging release preparation branches before merging to `main`.

---

## 13. Future Roadmap

- **Messaging Chatbot**: Complete text-based multi-channel integration (Web, WhatsApp, Telegram).
- **Voice Agent**: Low-latency bidirectional WebSockets for real-time audio streaming.
- **Shared AI Brain**: Cross-channel context synchronization across voice and text interactions.
- **Corporate Features**: Enterprise accounts, split billing, team travel management.
- **Hotel Integration**: Contextual ride suggestions tied to hotel check-in/out schedules.
- **Airport Integration**: Real-time flight tracking triggers for automated airport pick-up scheduling.
- **Railway Integration**: Transit connections synchronized with train arrival schedules.
- **Calendar Integration**: Automatic travel time buffering based on Google/Outlook calendar events.
- **Multi-language Support**: Real-time multilingual translation layer for global users.
- **Analytics**: Real-time dashboard for intent performance, booking conversion, and system latency.
- **AI Learning**: Continuous reinforcement learning from user feedback and booking choices.

---

## 14. Final Notes

### Development Rules

#### What Should Always Be Followed
- Always validate request payloads using Pydantic schemas.
- Always use async database operations where available.
- Always include standard error handling on external third-party service calls.
- Always add corresponding tests when building a new feature module.

#### What Should Never Be Done
- Never commit credentials, secrets, or `.env` files to source control.
- Never write business logic directly inside route handler functions; delegate to services/engine modules.
- Never execute raw blocking synchronous calls inside async route handlers.
- Never mutate state directly across module boundaries without passing through the module interface.

#### General Engineering Guidelines
Quality code is predictable, testable, and clean. Always write code with the expectation that another engineer will maintain it tomorrow.
