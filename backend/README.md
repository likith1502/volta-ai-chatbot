# VOLTA AI Chatbot - Backend Platform

A production-grade, asynchronous AI-powered messaging chatbot and voice agent backend for the VOLTA urban mobility platform. Built with Python 3.11+, FastAPI, Async PostgreSQL, SQLAlchemy 2.0, Alembic, and Redis.

---

## Architecture Overview

The backend follows a **Modular Clean Architecture** designed for high concurrency, loose coupling, and strict domain isolation:

```
FastAPI Presentation Layer (app/api/v1/)
       │
       ▼
Business Services Layer (app/services/)
       │
       ▼
Data Repositories Layer (app/repositories/)
       │
       ▼
Infrastructure & Persistence (app/database/, app/cache/)
```

All application configuration is centrally managed via Pydantic `Settings` (`app/config/settings.py`). Database operations execute asynchronously through SQLAlchemy `AsyncSession` and `asyncpg`.

---

## Technology Stack

- **Framework**: FastAPI (ASGI)
- **Language**: Python 3.11+
- **Database**: PostgreSQL 15+
- **Async ORM**: SQLAlchemy 2.0 (`asyncpg` driver)
- **Migrations**: Alembic
- **Settings**: Pydantic BaseSettings (`pydantic-settings`)
- **Testing**: pytest & `httpx` (`TestClient`)

---

## Directory Structure

```
backend/
├── app/
│   ├── api/          # Route handlers & API routers (v1)
│   ├── booking/      # Ride booking domain logic
│   ├── cache/        # Redis caching layer
│   ├── config/       # Settings & constants
│   ├── context/      # Short-term dialogue context tracking
│   ├── conversation/ # LangGraph AI workflow graphs
│   ├── core/         # Exception handlers & logging setup
│   ├── database/     # AsyncEngine, AsyncSession, Base metadata
│   ├── entities/     # Entity extraction module
│   ├── intent/       # Intent classification engine
│   ├── llm/          # LLM integrations
│   ├── memory/       # Episodic & user long-term memory
│   ├── middleware/   # Custom FastAPI middleware
│   ├── models/       # SQLAlchemy ORM models
│   ├── notifications/ # Transactional notification service
│   ├── prediction/   # Travel intent prediction engine
│   ├── profile/      # User profile management
│   ├── prompts/      # Prompt templates directory
│   ├── recommendation/ # Ride recommendation engine
│   ├── schemas/      # Pydantic DTO validation schemas
│   ├── services/     # Third-party integrations & domain services
│   ├── utils/        # Response helpers & utility functions
│   └── main.py       # FastAPI application entry point
├── docs/             # Technical architecture & engineering docs
├── logs/             # Local runtime execution logs
├── migrations/       # Alembic versioned migration environment
├── requirements/     # Environment-specific dependency files
├── scripts/          # Operations and seed scripts
├── tests/            # Automated pytest test suites
├── .editorconfig
├── .env
├── .env.example
├── .gitignore
├── alembic.ini
├── ARCHITECTURE.md
├── README.md
└── requirements.txt
```

---

## Setup Instructions

### 1. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 2. Install Dependencies
Install base dependencies:
```bash
pip install -r requirements.txt
```

---

## Run Commands

Start the local FastAPI development server with live reload:
```bash
python -m uvicorn app.main:app --reload
```

The application will be accessible at:
- **Root**: http://127.0.0.1:8000/
- **Top-Level Health**: http://127.0.0.1:8000/health
- **V1 Health Check**: http://127.0.0.1:8000/api/v1/health
- **Swagger Documentation**: http://127.0.0.1:8000/docs
- **ReDoc Documentation**: http://127.0.0.1:8000/redoc
- **OpenAPI Schema**: http://127.0.0.1:8000/openapi.json

---

## Testing Commands

Run the complete automated test suite:
```bash
pytest
```

Run tests with verbose output:
```bash
pytest -v
```

---

## Alembic Migration Commands

- **Autogenerate Migration Script**:
  ```bash
  alembic revision --autogenerate -m "description_of_changes"
  ```
- **Apply All Migrations**:
  ```bash
  alembic upgrade head
  ```
- **Rollback Last Migration**:
  ```bash
  alembic downgrade -1
  ```
- **View Current Revision**:
  ```bash
  alembic current
  ```
- **Generate Offline SQL**:
  ```bash
  alembic upgrade head --sql
  ```

---

## Documentation Links

- [Master Architecture Blueprint](ARCHITECTURE.md)
- [Database Design Principles](docs/database/database-design-principles.md)
- [Database Request Flow Architecture](docs/database/database-architecture.md)
- [Engineering Principles & Constitution](docs/engineering/engineering-principles.md)
- [Project Coding Standards](docs/engineering/project-standards.md)
- [Alembic Migration Strategy](docs/architecture/010-alembic-migration-strategy.md)
- [Infrastructure Foundation Lock Record](docs/architecture/011-infrastructure-lock.md)

---

## Development Workflow & Roadmap

1. **Milestone 1**: FastAPI Core Platform Scaffolding *(Completed)*
2. **Milestone 2**: Infrastructure Layer *(PostgreSQL & Alembic Frozen, Mixins & Models Next)*
3. **Milestone 3**: Authentication & User Profile Management *(Planned)*
4. **Milestone 4**: Shared AI Brain & Conversational Pipeline *(Planned)*

---

## Contribution Notes

- Strictly follow guidelines in `CONTRIBUTING.md`.
- All database schema changes **must** go through Alembic migration scripts.
- Never write business logic inside route handlers or repository abstractions.
- All new endpoints and service modules require accompanying pytest coverage.
