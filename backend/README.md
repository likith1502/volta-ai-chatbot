# VOLTA AI Chatbot - Backend Platform

A production-grade, asynchronous AI-powered messaging chatbot backend for the VOLTA urban mobility platform. Built with Python 3.11+, FastAPI, Async PostgreSQL, SQLAlchemy 2.0, Alembic, and Provider-Agnostic Conversational AI.

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
AI Provider Layer (app/ai/)           Domain Repositories (app/repositories/)
 (OpenAI, Claude, Gemini, Ollama)                │
                                                 ▼
                                   Infrastructure & Persistence (app/db/)
```

All application configuration is centrally managed via Pydantic `Settings` (`app/config/settings.py`). Database operations execute asynchronously through SQLAlchemy `AsyncSession` and `asyncpg`.

---

## Technology Stack

- **Framework**: FastAPI (ASGI)
- **Language**: Python 3.11+
- **Database**: PostgreSQL 15+
- **Async ORM**: SQLAlchemy 2.0 (`asyncpg` driver)
- **Migrations**: Alembic
- **AI Engine**: Provider-Agnostic `AIProvider` Interface (`OpenAI`, Anthropic Claude, Gemini, Ollama)
- **Settings**: Pydantic BaseSettings (`pydantic-settings`)
- **Testing**: pytest & `httpx` (`TestClient`)

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
│   ├── models/       # SQLAlchemy ORM models
│   ├── repositories/ # Data access repository layer
│   ├── schemas/      # Pydantic DTO validation schemas
│   ├── services/     # Domain services & ChatService orchestrator
│   ├── streaming/    # Streaming & Real-Time Foundation (v6.7)
│   ├── utils/        # Response helpers & utility functions
│   ├── workflow/     # Workflow Node Library (v6.3)
│   └── main.py       # FastAPI application entry point
├── docs/             # Technical architecture & engineering docs
├── logs/             # Local runtime execution logs
├── migrations/       # Alembic versioned migration environment
├── scripts/          # Operations and seed scripts
├── tests/            # Automated pytest test suites
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
- **V1 Health Check**: http://127.0.0.1:8000/api/v1/health
- **V1 Chat Endpoint**: http://127.0.0.1:8000/api/v1/chat
- **Swagger Documentation**: http://127.0.0.1:8000/docs

---

## Testing Commands

Run the complete automated test suite (124 passed in ~3.2s):
```bash
pytest
```

---

## Development Roadmap & Releases

### Completed Foundations (v1.0 – v6.8.1)
- **Release v1.0**: Infrastructure Foundation *(Completed & Locked)*
- **Release v1.1**: Database Base Mixins *(Completed & Locked)*
- **Release v2.0**: Domain Models *(Completed & Locked)*
- **Release v2.5**: Repository Pattern *(Completed & Locked)*
- **Release v2.6**: Project Structure Standardization *(Completed & Locked)*
- **Release v3.0**: Service Layer *(Completed & Locked)*
- **Release v4.0**: REST API Layer *(Completed & Locked)*
- **Release v5.0**: AI Foundation & Conversation Intelligence *(Completed & Locked)*
- **Release v6.1**: Conversation State Foundation *(Completed & Locked)*
- **Release v6.2**: Graph Orchestration Foundation *(Completed & Locked)*
- **Release v6.3**: Workflow Node Library *(Completed & Locked)*
- **Release v6.4**: Graph Execution Engine *(Completed & Locked)*
- **Release v6.5**: Workflow Event & Observability Foundation *(Completed & Locked)*
- **Release v6.6**: Checkpoint & Replay Foundation *(Completed & Locked)*
- **Release v6.7**: Streaming & Real-Time Foundation *(Completed & Locked)*
- **Release v6.8**: Human-in-the-Loop Foundation *(Completed & Locked)*
- **Release v6.8.1**: Documentation & Repository Synchronization *(Completed & Locked)*

### Active & Future Roadmap
- 🚀 **Phase 7 — Enterprise Messaging Runtime** *(Active Target)*
  - `7.0` LLM Runtime Engine
  - `7.1` Prompt Execution Engine
  - `7.2` Memory Runtime
  - `7.3` Tool Runtime
  - `7.4` Graph Runtime Integration
  - `7.5` Multi-Agent Runtime
  - `7.6` RAG Engine
  - `7.7` Production Integrations
  - `7.8` Deployment & Scaling
- 📅 **Phase 8 — Voice Platform** *(Future Expansion)*
  - `8.0` Speech-to-Text (STT)
  - `8.1` Text-to-Speech (TTS)
  - `8.2` Audio Streaming
  - `8.3` Voice Sessions
  - `8.4` Telephony Integrations
  - `8.5` Multimodal Conversations


