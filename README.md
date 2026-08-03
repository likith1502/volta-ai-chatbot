# VOLTA AI Chatbot

A production-grade, multi-modal AI-powered messaging chatbot and voice agent backend designed for the VOLTA urban mobility and ride-booking platform.

---

## Project Goals

- **Conversational Mobility**: Provide real-time, context-aware ride discovery, booking, and travel assistance.
- **Shared AI Brain**: Maintain persistent multi-turn conversational state across messaging (text) and real-time audio (voice) channels.
- **Enterprise Performance**: Deliver sub-second response times using asynchronous non-blocking Python architecture (FastAPI, Async PostgreSQL, Redis, LangGraph).

---

## Repository & Backend Structure

```
Volta-AI-Chatbot/
├── .github/              # GitHub templates, workflows, & community standards
├── backend/              # Core FastAPI application & AI services
│   ├── app/              # Application modules (api, database, services, models)
│   ├── docs/             # Internal technical architecture & design principles
│   ├── logs/             # Runtime execution log directory
│   ├── migrations/       # Alembic versioned schema migrations
│   ├── scripts/          # Operation & database seeding scripts
│   ├── tests/            # Automated pytest test suites
│   ├── alembic.ini       # Alembic migration configuration
│   ├── ARCHITECTURE.md   # Master backend architecture blueprint
│   └── README.md         # Backend developer guide
├── docs/                 # General project documentation hub
├── infrastructure/       # Deployment manifests & container configs
└── testing-ui/           # Lightweight testing frontend
```

---

## Architecture Overview

The backend employs a **Modular Clean Architecture** enforcing clean boundary separation between HTTP Routers, Business Services, Repositories, and Persistent Infrastructure.

```
FastAPI Router (app/api/v1/) ──► Services (app/services/) ──► Repositories (app/repositories/) ──► Async PostgreSQL / Redis
```

---

## Documentation Location

All technical documentation, Architecture Decision Records (ADRs), database constitutions, and coding standards are maintained under:

👉 [backend/docs/](backend/docs/)

Key Documents:
- [Master Backend Architecture](backend/ARCHITECTURE.md)
- [Database Design Principles](backend/docs/database/database-design-principles.md)
- [Engineering Principles & Constitution](backend/docs/engineering/engineering-principles.md)
- [Official Project Standards](backend/docs/engineering/project-standards.md)
- [Infrastructure Lock Record](backend/docs/architecture/011-infrastructure-lock.md)

---

## Technology Stack

- **Backend**: Python 3.11+, FastAPI (ASGI), Uvicorn
- **Database**: PostgreSQL 15+, Async SQLAlchemy 2.0 (`asyncpg` driver)
- **Migrations**: Alembic
- **Caching**: Redis
- **AI & Orchestration**: LangGraph, Pydantic
- **Testing**: pytest, `httpx`
- **Frontend**: React (`testing-ui`)

---

## Development Status & Roadmap

- ✅ **Phase 1: Project Structure**: Completed & Verified
- ✅ **Phase 2: FastAPI Core Platform**: Milestone 1 Completed & Passed
- ✅ **Phase 3: PostgreSQL & Alembic Foundation**: Chapter 2.1 & 2.2 Frozen (v1.0)
- 🚧 **Phase 4: Database Mixins & Domain Models**: Next (Chapters 2.3 - 2.5)
- 📅 **Phase 5: Redis Infrastructure**: Planned
- 📅 **Phase 6: Shared AI Brain & Conversation Pipeline**: Planned

---

## Contributing

We welcome contributions! Please review our guidelines before submitting pull requests:
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CODE_OF_CONDUCT.md](.github/CODE_OF_CONDUCT.md)

---

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
