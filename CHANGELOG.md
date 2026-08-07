# Changelog

All notable changes to the VOLTA AI Chatbot platform are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v7.1.0] - 2026-08-07

### Added
- **Enterprise Prompt Execution Engine** (`backend/app/prompt/`): Provider-independent, framework-independent prompt composition, templating, rendering, validation, linting, optimization, and lifecycle management layer.
- **`PromptRepository` Abstraction**: Abstract storage layer (`PromptRepository` ABC & `InMemoryPromptRepository`) preparing for Database, Git, Filesystem, and Cloud Prompt Hub backends.
- **`PromptProfile` Separation**: Separated *how to generate* (model, temperature, max tokens, response format) from *what to say* (templates).
- **`PromptCompiler`**: Format compiler converting `PromptResponse` and `PromptProfile` into `CompiledPrompt` payloads for `RuntimeManager`.
- **`processors/` Subpackage**: `PromptRenderer`, `PromptValidator`, `PromptOptimizer`, and `PromptLinter` (detects duplicate instructions, contradictory statements, and excessive prompt length).
- **Prompt Chain Contracts**: `PromptStep`, `PromptChain`, and `ChainResult` contracts preparing for Phase 7.5 Multi-Agent Runtime workflows.
- **Telemetry & Quality Scorecards**: `PromptCostEstimator` (request & monthly projections), `PromptQualityAnalyzer` (readability, density, hallucination risk, overall grade), `PromptBenchmarkRunner`, and `PromptAnalyticsManager`.
- **Sandbox Mode & Side-by-Side Comparison**: REST API endpoints `POST /api/v1/prompts/sandbox/execute` and `POST /api/v1/prompts/compare`.
- **Prompt Studio Mini-IDE**: Interactive browser UI panel (`testing-ui/index.html`) mounted at `/console` featuring live template rendering, variable payload JSON editor, side-by-side diff view, and provider comparison.
- **Architecture Decision Records**: `ADR 038` (Prompt Execution Engine Architecture) and `ADR 039` (Prompt Engineering Guidelines).

---

## [v7.0.0] - 2026-08-07

### Added
- **Enterprise LLM Runtime Engine** (`backend/app/runtime/`): Provider-independent core runtime execution engine (`RuntimeProvider` ABC, `ChatMessage`, `RuntimeRequest`, `RuntimeResponse`, `RuntimeTokenUsage`, `ProviderCapabilities`).
- **Google Gemini Provider**: Production provider using official `google-genai` SDK (`gemini-2.5-flash`, `gemini-2.5-pro`).
- **Mock Provider**: Deterministic mock provider for offline development and testing.
- **`RuntimeManager` Orchestrator**: Provider dispatch, exponential backoff retries, token accounting, and `WorkflowEventBus` notification emissions.
- **Developer Testing Console**: Interactive frontend (`testing-ui/index.html`) mounted at `/console`.
- **Architecture Decision Records**: `ADR 036` (Enterprise LLM Runtime Engine) and `ADR 037` (Runtime Engineering Guidelines).

---

## [v6.8.1] - 2026-08-07

### Synchronized
- Architecture Baseline Snapshot (`backend/docs/ARCHITECTURE_BASELINE_v6.8.1.md`).
- Roadmap realignment: Phase 7 set to Enterprise Messaging Runtime; Phase 8 set to Voice Platform Expansion.
- Foundation lock freeze for all 15 foundation tiers (v1.0 – v6.8).

---

## [v6.8.0] - 2026-08-05

### Added
- **Human-in-the-Loop (HITL) & Governance Foundation** (`backend/app/hitl/`): Approval requests, lifecycle states (`PENDING`, `APPROVED`, `REJECTED`, `TIMEOUT`, `CANCELLED`), `HITLGovernanceEngine`, `HITLInterruptManager`, and `HITLInterruptRegistry`.
- `ADR 034` and `ADR 035`.

---

## [v6.7.0] - 2026-08-05

### Added
- **Streaming & Real-Time Foundation** (`backend/app/streaming/`): Priority stream dispatcher (`StreamDispatcher`), `StreamMessage`, `StreamEnvelope`, `StreamChannel`, `StreamSubscription`, and `StreamManager`.
- `ADR 032` and `ADR 033`.

---

## [v6.6.0] - 2026-08-05

### Added
- **Checkpoint & Replay Foundation** (`backend/app/checkpoints/`): State snapshot checkpointing, `CheckpointManager`, `ReplayEngine`, `SequentialReplayStrategy`, and `ReplayContext`.
- `ADR 030` and `ADR 031`.

---

## [v6.5.0] - 2026-08-05

### Added
- **Workflow Event & Observability Foundation** (`backend/app/events/`): In-memory event bus (`WorkflowEventBus`), `WorkflowEvent`, `EventEnvelope`, priority dispatching, and observer filtering.
- `ADR 028` and `ADR 029`.

---

## [v6.4.0] - 2026-08-05

### Added
- **Graph Execution Engine** (`backend/app/execution/`): Validation algorithms, depth limit protection, `ExecutionPolicy`, `ExecutionDispatcher`, and `ExecutionScheduler`.
- `ADR 026` and `ADR 027`.

---

## [v6.3.0] - 2026-08-05

### Added
- **Workflow Node Library** (`backend/app/workflow/`): Node contracts (`BaseNode`), concrete nodes (`StartNode`, `EndNode`, `DecisionNode`, `LLMNode`, `ToolNode`, `MemoryNode`, `IntentNode`, `EntityNode`, `ResponseNode`), and `WorkflowNodeRegistry`.
- `ADR 024` and `ADR 025`.

---

## [v6.2.0] - 2026-08-04

### Added
- **Graph Orchestration Foundation** (`backend/app/graph/`): `StateGraph`, node execution contracts, conditional edges (`ConditionalEdge`), depth limit protection, cycle detection, and `GraphTemplateRegistry`.
- `ADR 022` and `ADR 023`.

---

## [v6.1.0] - 2026-08-04

### Added
- **Conversation State Foundation** (`backend/app/context/`): Strongly-typed immutable state models (`StateMetadata`, `ConversationData`, `RuntimeState`, `ExecutionState`, `MemoryState`), snapshot lineage (`state_id`, `parent_state_id`), and abstract state manager.
- `ADR 021`.

---

## [v5.0.0] - 2026-08-03

### Added
- **Enterprise AI Foundation** (`backend/app/ai/`): Multi-provider AI adapters (`OpenAI`, `Claude`, `Gemini`, `Ollama`), adapter factory, unified model interfaces, cost/token tracking.
- `ADR 018` and `ADR 019`.

---

## [v4.0.0] - 2026-08-03

### Added
- **REST API Presentation Layer** (`backend/app/api/v1/`): FastAPI routers (`users`, `conversations`, `recommendations`, `bookings`, `notifications`, `chat`), Pydantic DTO schemas, service dependency injection.
- `ADR 017`.

---

## [v3.0.0] - 2026-08-03

### Added
- **Application Service Layer** (`backend/app/services/`): `UserService`, `ConversationService`, `RecommendationService`, `BookingService`, `NotificationService`, domain exception hierarchy.
- `ADR 016`.

---

## [v2.0.0] - 2026-08-03

### Added
- **Domain Models & Repositories Layer** (`backend/app/models/`, `backend/app/repositories/`): SQLAlchemy ORM models, generic `BaseRepository[T]`, specialized repositories, database mixins.
- `ADR 012` through `ADR 015`.

---

## [v1.0.0] - 2026-08-03

### Added
- **Infrastructure Foundation**: FastAPI core application, Pydantic settings, logging, PostgreSQL Async engine pooling, AsyncSession, Alembic migrations.
- `ADR 001` through `ADR 011`.
