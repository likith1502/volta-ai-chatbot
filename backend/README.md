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
Infrastructure & Persistence (app/db/, app/cache/)
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
│   ├── config/       # Settings & constants
│   ├── core/         # Exception handlers & logging setup
│   ├── db/           # AsyncEngine, AsyncSession, Base metadata, Mixins
│   ├── dependencies/ # FastAPI dependency injection utilities
│   ├── exceptions/   # Application exceptions
│   ├── models/       # SQLAlchemy ORM models
│   ├── repositories/ # Data access repository layer
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
- [Official Project Standards](docs/engineering/project-standards.md)
- [Alembic Migration Strategy](docs/architecture/010-alembic-migration-strategy.md)
- [Infrastructure Foundation Lock Record](docs/architecture/011-infrastructure-lock.md)

---

## Development Roadmap & Releases

- **Release v1.0**: Infrastructure Foundation *(Completed & Locked)*
- **Release v1.1**: Database Base Mixins *(Completed & Locked)*
- **Release v2.0**: Domain Models *(Completed & Locked)*
- **Release v2.5**: Repository Pattern *(Completed & Locked)*
- **Chapter 3.0**: Application Services & Pydantic Schemas *(Next)*
