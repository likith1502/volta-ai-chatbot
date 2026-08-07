# VOLTA AI Chatbot

A production-grade, asynchronous AI-powered messaging chatbot backend designed for the VOLTA urban mobility platform.

[![Release](https://img.shields.io/badge/Release-v1.0.0-blue.svg)](https://github.com/likith1502/volta-ai-chatbot/releases/tag/v1.0.0)
[![Tests](https://img.shields.io/badge/Tests-421%20Passing-success.svg)](backend/tests/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-v1.0-green.svg)](https://fastapi.tiangolo.com/)

---

## Project Goals

- **Conversational Mobility**: Provide real-time, context-aware ride discovery, booking, and travel assistance over enterprise messaging channels.
- **Enterprise AI Messaging Runtime**: Maintain persistent multi-turn conversational state, graph workflows, prompt engineering, memory orchestration, tool integration, graph runtime execution, multi-agent team orchestration, and RAG knowledge retrieval across messaging interactions.
- **Enterprise Performance**: Deliver sub-second response times using asynchronous non-blocking Python architecture (FastAPI, Async PostgreSQL, SQLAlchemy 2.0).

---

## Repository & Backend Structure

```
Volta-AI-Chatbot/
├── .github/              # GitHub templates, workflows, & community standards
├── backend/              # Core FastAPI application & AI services
├── app/              # Application modules
│   ├── agents/       # Enterprise Multi-Agent Orchestration Runtime (v7.5)
│   ├── ai/           # Multi-provider AI engine (OpenAI, Claude, Gemini, Ollama)
│   ├── api/          # REST API presentation routers & dependencies (v1)
│   ├── checkpoints/  # Checkpoint & Replay Foundation (v6.6)
│   ├── config/       # Settings configuration & constants
│   ├── context/      # Conversation State Foundation (v6.1)
│   ├── core/         # Exception handlers & logging setup
│   ├── db/           # AsyncEngine, AsyncSession, Base metadata, Mixins
│   ├── dependencies/ # FastAPI dependency injection utilities
│   ├── deployment/   # Enterprise Deployment, Scaling & Operationalization (v7.8)
│   ├── events/       # Workflow Event & Observability Foundation (v6.5)
│   ├── exceptions/   # Domain & infrastructure exceptions
│   ├── execution/    # Graph Execution Engine (v6.4)
│   ├── graph/        # Graph Orchestration Foundation (v6.2)
│   ├── graph_runtime/# Enterprise Graph Runtime Integration (v7.4)
│   ├── hitl/         # Human-in-the-Loop & Governance Foundation (v6.8)
│   ├── integrations/ # Enterprise Integration Platform (v7.7)
│   ├── memory/       # Enterprise Memory Runtime (v7.2)
│   ├── models/       # SQLAlchemy ORM domain models
│   ├── observability/# Platform Metrics, Logging, Tracing & Alerting (v7.8)
│   ├── prompt/       # Prompt Execution Engine (v7.1)
│   ├── rag/          # Enterprise RAG Engine (v7.6)
│   ├── repositories/ # Generic & specialized data access repositories
│   ├── runtime/      # Enterprise LLM Runtime Engine (v7.0)
│   ├── schemas/      # Pydantic DTO validation schemas
│   ├── services/     # Domain business services & ChatService
│   ├── streaming/    # Streaming & Real-Time Foundation (v6.7)
│   ├── tools/        # Enterprise Tool Runtime (v7.3)
│   ├── utils/        # Response helpers & utility functions
│   └── workflow/     # Workflow Node Library (v6.3)
├── docs/             # Technical architecture & engineering docs (ADRs 001–053)
├── logs/             # Runtime execution log directory
├── migrations/       # Alembic versioned schema migrations
├── scripts/          # Operation & database seeding scripts
├── tests/            # Automated pytest test suites (421 passed)
│   ├── alembic.ini       # Alembic migration configuration
│   ├── ARCHITECTURE.md   # Master backend architecture blueprint
│   └── README.md         # Backend developer guide
├── docs/                 # General project documentation hub
├── infrastructure/       # Deployment manifests & container configs
└── testing-ui/           # Developer Testing Console, Prompt Studio, Memory Studio, Tool Studio, Graph Studio & Agent Studio
```

---

## Master Architecture Overview

The backend employs a **Modular Clean Architecture** enforcing clean boundary separation between HTTP Routers, Business Services, Multi-Agent Orchestration, Graph Runtime Orchestration, Tool Orchestration, Memory Orchestration, Prompt Engineering, LLM Runtime Execution, Repositories, and Persistent Infrastructure.

```
FastAPI Router (app/api/v1/)
       │
       ▼
Chat Service & AI Orchestration (app/services/, app/ai/)
       │
       ├─────────────────────────────────────────┐
       ▼                                         ▼
Enterprise Multi-Agent Runtime (app/agents/ v7.5) Domain Repositories (app/repositories/)
       │                                         │
       ▼                                         ▼
Enterprise Graph Runtime (app/graph_runtime/ v7.4) Async PostgreSQL (app/db/)
       │
       ├─────────────────┐
       ▼                 ▼
Event & Stream Bus     HITL Governance & Replay Engine
(app/events/, streaming/)  (app/hitl/, app/checkpoints/)
       │
       ▼
Enterprise Tool Runtime (app/tools/ v7.3)
       │
       ▼
Enterprise Memory Runtime (app/memory/ v7.2)
       │
       ▼
Prompt Execution Engine (app/prompt/ v7.1)
       │
       ▼
Enterprise LLM Runtime Engine (app/runtime/ v7.0)
       │
       ▼
Google Gemini SDK / Mock Provider
```

---

## Documentation Location

All technical documentation, Architecture Decision Records (ADRs 001–047), database constitutions, and coding standards are maintained under:

👉 [backend/docs/](backend/docs/)

Key Documents:
- [Master Backend Architecture](backend/ARCHITECTURE.md)
- [Master Runtime Architecture Blueprint](backend/docs/RUNTIME_ARCHITECTURE.md)
- [ADR Index (ADRs 001 – 047)](backend/docs/architecture/README.md)
- [Foundation Status & Lock Record](backend/docs/FOUNDATION_STATUS.md)
- [Project Milestones & Release History](backend/docs/PROJECT_MILESTONES.md)
- [Final Enterprise Runtime Graduation Certificate](backend/docs/ENTERPRISE_RUNTIME_GRADUATION.md)
- [ADR 046: Enterprise Multi-Agent Orchestration Runtime Architecture](backend/docs/architecture/046-enterprise-multi-agent-runtime.md)
- [ADR 047: Agent Engineering Guidelines](backend/docs/architecture/047-agent-engineering-guidelines.md)

---

## Technology Stack

- **Backend**: Python 3.11+, FastAPI (ASGI), Uvicorn
- **Database**: PostgreSQL 15+, Async SQLAlchemy 2.0 (`asyncpg` driver)
- **Migrations**: Alembic
- **Runtime Engine**: Official `google-genai` SDK (`gemini-2.5-flash`, `gemini-2.5-pro`) & Provider-Independent Runtime Layer
- **Prompt Engine**: PromptManager, PromptProfiles, PromptCompiler, PromptLinter, PromptPipeline
- **Memory Engine**: MemoryManager, MemoryLifecycleManager, ContextAssemblyStrategy, MemoryScorer
- **Tool Engine**: ToolManager, BaseTool ABC, ToolSchema, ToolManifest, ToolPipeline, ToolChain, ToolDiscoveryService
- **Graph Engine**: GraphRuntimeManager, GraphPlanner, GraphScheduler, GraphExecutionPlan, GraphCursor, GraphRuntimePipeline
- **Multi-Agent Engine**: AgentRuntimeManager, AgentDefinition, AgentInstance, AgentPersona, SupervisorAgent, PlannerAgent, TeamManager
- **Testing**: pytest (175 passed in strict asyncio mode), `httpx`
- **Developer UI**: Developer Console (`testing-ui/index.html`) featuring Runtime Console, Prompt Studio, Memory Studio, Tool Studio, Graph Studio & Agent Studio

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
- 🚀 **Phase 7 — Enterprise Messaging Runtime** *(Active Phase)*
  - ✅ `7.0` LLM Runtime Engine *(v7.0.0 Completed)*
  - ✅ `7.1` Prompt Execution Engine *(v7.1.0 Completed)*
  - ✅ `7.2` Memory Runtime *(v7.2.0 Completed)*
  - ✅ `7.3` Tool Runtime *(v7.3.0 Completed)*
  - ✅ `7.4` Graph Runtime Integration *(v7.4.0 Completed)*
  - ✅ `7.5` Enterprise Multi-Agent Orchestration Runtime *(v7.5.0 Completed)*
  - ⏳ `7.6` RAG Engine *(Next Sub-Phase)*
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
