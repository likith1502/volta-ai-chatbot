# VOLTA AI Chatbot

A production-grade, asynchronous AI-powered messaging chatbot backend designed for the VOLTA urban mobility platform.

---

## Project Goals

- **Conversational Mobility**: Provide real-time, context-aware ride discovery, booking, and travel assistance over enterprise messaging channels.
- **Enterprise AI Messaging Runtime**: Maintain persistent multi-turn conversational state, graph workflows, and tool integration across messaging interactions.
- **Enterprise Performance**: Deliver sub-second response times using asynchronous non-blocking Python architecture (FastAPI, Async PostgreSQL, SQLAlchemy 2.0).

---

## Repository & Backend Structure

```
Volta-AI-Chatbot/
├── .github/              # GitHub templates, workflows, & community standards
├── backend/              # Core FastAPI application & AI services
│   ├── app/              # Application modules
│   │   ├── ai/           # Multi-provider AI engine (OpenAI, Claude, Gemini, Ollama)
│   │   ├── api/          # REST API presentation routers & dependencies (v1)
│   │   ├── checkpoints/  # Checkpoint & Replay Foundation (v6.6)
│   │   ├── config/       # Settings configuration & constants
│   │   ├── context/      # Conversation State Foundation (v6.1)
│   │   ├── core/         # Exception handlers & logging setup
│   │   ├── db/           # AsyncEngine, AsyncSession, Base metadata, Mixins
│   │   ├── dependencies/ # FastAPI dependency injection utilities
│   │   ├── events/       # Workflow Event & Observability Foundation (v6.5)
│   │   ├── exceptions/   # Domain & infrastructure exceptions
│   │   ├── execution/    # Graph Execution Engine (v6.4)
│   │   ├── graph/        # Graph Orchestration Foundation (v6.2)
│   │   ├── hitl/         # Human-in-the-Loop & Governance Foundation (v6.8)
│   │   ├── models/       # SQLAlchemy ORM domain models
│   │   ├── repositories/ # Generic & specialized data access repositories
│   │   ├── schemas/      # Pydantic DTO validation schemas
│   │   ├── services/     # Domain business services & ChatService
│   │   ├── streaming/    # Streaming & Real-Time Foundation (v6.7)
│   │   ├── utils/        # Response helpers & utility functions
│   │   └── workflow/     # Workflow Node Library (v6.3)
│   ├── docs/             # Technical architecture & engineering docs (ADRs 001–035)
│   ├── logs/             # Runtime execution log directory
│   ├── migrations/       # Alembic versioned schema migrations
│   ├── scripts/          # Operation & database seeding scripts
│   ├── tests/            # Automated pytest test suites (124 passed)
│   ├── alembic.ini       # Alembic migration configuration
│   ├── ARCHITECTURE.md   # Master backend architecture blueprint
│   └── README.md         # Backend developer guide
├── docs/                 # General project documentation hub
├── infrastructure/       # Deployment manifests & container configs
└── testing-ui/           # Lightweight testing frontend
```

---

## Architecture Overview

The backend employs a **Modular Clean Architecture** enforcing clean boundary separation between HTTP Routers, Business Services, Repositories, AI Orchestration, and Persistent Infrastructure.

```
FastAPI Router (app/api/v1/)
       │
       ▼
Chat Service & AI Engine (app/services/, app/ai/)
       │
       ├─────────────────────────────────────────┐
       ▼                                         ▼
Graph Execution & State Engine            Domain Repositories (app/repositories/)
(app/graph/, app/context/, app/execution/)       │
       │                                         ▼
       ├─────────────────┐        Async PostgreSQL (app/db/)
       ▼                 ▼
Event & Stream Bus     HITL Governance & Replay Engine
(app/events/, streaming/)  (app/hitl/, app/checkpoints/)
       │
       ▼
Enterprise Messaging Runtime (Phase 7) ──► Voice Platform (Phase 8 Expansion)
```

---

## Documentation Location

All technical documentation, Architecture Decision Records (ADRs 001–035), database constitutions, and coding standards are maintained under:

👉 [backend/docs/](backend/docs/)

Key Documents:
- [Master Backend Architecture](backend/ARCHITECTURE.md)
- [ADR Index (ADRs 001 – 035)](backend/docs/architecture/README.md)
- [Foundation Status & Lock Record](backend/docs/FOUNDATION_STATUS.md)
- [Project Milestones & Release History](backend/docs/PROJECT_MILESTONES.md)
- [Foundation Graduation Certificate](backend/docs/FOUNDATION_CERTIFICATE_v6.8.1.md)

---

## Technology Stack

- **Backend**: Python 3.11+, FastAPI (ASGI), Uvicorn
- **Database**: PostgreSQL 15+, Async SQLAlchemy 2.0 (`asyncpg` driver)
- **Migrations**: Alembic
- **AI Engine**: Multi-Provider Adapter Engine (OpenAI, Anthropic Claude, Google Gemini, Ollama)
- **State & Graph**: Provider-Agnostic Graph Execution Engine & Node Library
- **Testing**: pytest (124 passed in strict asyncio mode), `httpx`
- **Frontend**: React (`testing-ui`)

---

## Development Status & Roadmap

### Completed Foundations (Phase 1 – Phase 6.8.1)
- ✅ **v1.0**: Infrastructure Foundation *(Locked)*
- ✅ **v1.1**: Database Base Mixins *(Locked)*
- ✅ **v2.0**: Domain Models Layer *(Locked)*
- ✅ **v2.6**: Repository Layer & Standardization *(Locked)*
- ✅ **v3.0**: Application Service Layer *(Locked)*
- ✅ **v4.0**: REST API Presentation Layer *(Locked)*
- ✅ **v5.0**: Enterprise AI Foundation *(Locked)*
- ✅ **v6.1**: Conversation State Foundation *(Locked)*
- ✅ **v6.2**: Graph Orchestration Foundation *(Locked)*
- ✅ **v6.3**: Workflow Node Library *(Locked)*
- ✅ **v6.4**: Graph Execution Engine *(Locked)*
- ✅ **v6.5**: Workflow Event & Observability Foundation *(Locked)*
- ✅ **v6.6**: Checkpoint & Replay Foundation *(Locked)*
- ✅ **v6.7**: Streaming & Real-Time Foundation *(Locked)*
- ✅ **v6.8**: Human-in-the-Loop Foundation *(Locked)*
- ✅ **v6.8.1**: Documentation & Repository Synchronization *(Locked)*

### Active Milestone Roadmap
- 🚀 **Phase 7 — Enterprise Messaging Runtime** *(Current Target)*
  - `7.0` LLM Runtime Engine
  - `7.1` Prompt Execution Engine
  - `7.2` Memory Runtime
  - `7.3` Tool Runtime
  - `7.4` Graph Runtime Integration
  - `7.5` Multi-Agent Runtime
  - `7.6` RAG Engine
  - `7.7` Production Integrations
  - `7.8` Deployment & Scaling
- 📅 **Phase 8 — Voice Platform** *(Future Horizon)*
  - `8.0` Speech-to-Text (STT)
  - `8.1` Text-to-Speech (TTS)
  - `8.2` Audio Streaming
  - `8.3` Voice Sessions
  - `8.4` Telephony Integrations
  - `8.5` Multimodal Conversations

---

## Contributing

We welcome contributions! Please review our guidelines before submitting pull requests:
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CODE_OF_CONDUCT.md](.github/CODE_OF_CONDUCT.md)

---

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
