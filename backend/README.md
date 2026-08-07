# VOLTA AI Chatbot - Backend Platform

A production-grade, asynchronous AI-powered messaging chatbot backend for the VOLTA urban mobility platform. Built with Python 3.11+, FastAPI, Async PostgreSQL, SQLAlchemy 2.0, Alembic, Google Gemini SDK, and Provider-Agnostic Conversational AI.

[![Release](https://img.shields.io/badge/Release-v7.2-blue.svg)](https://github.com/likith1502/volta-ai-chatbot/releases/tag/v7.2)
[![Tests](https://img.shields.io/badge/Tests-156%20Passing-success.svg)](tests/)

---

## Architecture Overview

The backend follows a **Modular Clean Architecture** designed for high concurrency, loose coupling, and strict domain isolation:

```
FastAPI Presentation Layer (app/api/v1/)
       │
       ▼
Application Services & AI Orchestrator (app/services/chat.py)
       │
       ├─────────────────────────────────────────┐
       ▼                                         ▼
Enterprise Memory Runtime (app/memory/ v7.2)  Domain Repositories (app/repositories/)
       │                                         │
       ▼                                         ▼
Prompt Execution Engine (app/prompt/ v7.1)   Infrastructure & Persistence (app/db/)
       │
       ▼
Enterprise LLM Runtime Engine (app/runtime/ v7.0)
       │
       ▼
Google Gemini SDK / Mock Provider
```

All application configuration is centrally managed via Pydantic `Settings` (`app/config/settings.py`). Database operations execute asynchronously through SQLAlchemy `AsyncSession` and `asyncpg`.

---

## Technology Stack

- **Framework**: FastAPI (ASGI)
- **Language**: Python 3.11+
- **Database**: PostgreSQL 15+
- **Async ORM**: SQLAlchemy 2.0 (`asyncpg` driver)
- **Migrations**: Alembic
- **Runtime Engine**: Official `google-genai` SDK (`gemini-2.5-flash`, `gemini-2.5-pro`) & Provider-Independent Runtime Layer
- **Prompt Engine**: PromptManager, PromptProfiles, PromptCompiler, PromptLinter, PromptPipeline, PromptRepository
- **Memory Engine**: MemoryManager, MemoryLifecycleManager, ContextAssemblyStrategy, MemoryScorer, MemoryCompactor, ContextWindowBudget
- **Settings**: Pydantic BaseSettings (`pydantic-settings`)
- **Testing**: pytest & `httpx` (`TestClient`) — **156 Tests Passing**

---

## Directory Structure

```
backend/
├── app/
│   ├── ai/           # Provider-agnostic AI engine (base, factory, prompts, providers)
│   ├── api/          # Route handlers & API routers (v1)
│   ├── checkpoints/  # Checkpoint & Replay Foundation (v6.6)
│   ├── config/       # Settings & constants
│   ├── context/      # Conversation State Foundation (v6.1)
│   ├── core/         # Exception handlers & logging setup
│   ├── db/           # AsyncEngine, AsyncSession, Base metadata, Mixins
│   ├── dependencies/ # FastAPI dependency injection utilities
│   ├── events/       # Workflow Event & Observability Foundation (v6.5)
│   ├── exceptions/   # Application & AI exceptions
│   ├── execution/    # Graph Execution Engine (v6.4)
│   ├── graph/        # Graph Orchestration Foundation (v6.2)
│   ├── hitl/         # Human-in-the-Loop & Governance Foundation (v6.8)
│   ├── memory/       # Enterprise Memory Runtime (v7.2)
│   ├── models/       # SQLAlchemy ORM models
│   ├── prompt/       # Prompt Execution Engine (v7.1)
│   ├── repositories/ # Data access repository layer
│   ├── runtime/      # Enterprise LLM Runtime Engine (v7.0)
│   ├── schemas/      # Pydantic DTO validation schemas
│   ├── services/     # Domain services & ChatService orchestrator
│   ├── streaming/    # Streaming & Real-Time Foundation (v6.7)
│   ├── utils/        # Response helpers & utility functions
│   ├── workflow/     # Workflow Node Library (v6.3)
│   └── main.py       # FastAPI application entry point
├── docs/             # Technical architecture & engineering docs (ADRs 001–041)
├── logs/             # Local runtime execution logs
├── migrations/       # Alembic versioned migration environment
├── scripts/          # Operations and seed scripts
├── tests/            # Automated pytest test suites (156 passed)
├── .env
├── .env.example
├── ARCHITECTURE.md
├── README.md
└── requirements.txt
```

---

## Run Commands

Start the local FastAPI development server with live reload:
```bash
python -m uvicorn app.main:app --reload
```

The application will be accessible at:
- **Root**: http://127.0.0.1:8000/
- **Developer Console, Prompt Studio & Memory Studio**: http://127.0.0.1:8000/console
- **V1 Health Check**: http://127.0.0.1:8000/api/v1/health
- **V1 Chat Endpoint**: http://127.0.0.1:8000/api/v1/chat
- **V1 Runtime Endpoint**: http://127.0.0.1:8000/api/v1/runtime/chat
- **V1 Memory Endpoint**: http://127.0.0.1:8000/api/v1/memory
- **Swagger Documentation**: http://127.0.0.1:8000/docs

---

## Testing Commands

Run the complete automated test suite (156 passed in ~4.0s):
```bash
pytest
```
