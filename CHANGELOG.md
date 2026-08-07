# Changelog

All notable changes to the VOLTA AI Chatbot platform are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v7.6.0] - 2026-08-07

### Added
- **Enterprise RAG Engine** (`backend/app/rag/`): Provider-independent, storage-independent Retrieval-Augmented Generation platform coordinating document ingestion, parsing, chunking, embedding, vector indexing, retrieval planning, pluggable reranking, citation generation, context assembly, caching, ingestion jobs, and retrieval explanations without modifying frozen runtime layers (v7.0–v7.5).
- **`IngestionRuntime` & `QueryRuntime` Separation**: Dedicated Ingestion Runtime (Parse ➔ Chunk ➔ Embed ➔ Index) with `IngestionJob` background tracking vs Query Runtime (Rewrite ➔ Plan ➔ Retrieve ➔ Rerank ➔ Context ➔ Citations).
- **`RetrievalPlanner` & `RetrievalPlan`**: Structured retrieval planning for Vector, Keyword, Hybrid, Metadata Filter, Recent Documents, and Multi-Document strategies.
- **`Chunk` vs `EmbeddedChunk` Separation**: Un-embedded text blocks decoupled from vector embedding bindings.
- **Pluggable Rerankers**: `BaseReranker` ABC with `CosineReranker`, `HybridReranker`, `MetadataReranker`, `WeightedReranker`, and `CrossEncoderReranker` (placeholder).
- **`RetrievalCache` Abstraction**: `CacheProvider` ABC & `InMemoryCacheProvider` caching embeddings, retrieval results, reranking, and context.
- **`DocumentLifecycleManager`**: Lifecycle state machine (`UPLOADED` ➔ `PARSING` ➔ `CHUNKED` ➔ `INDEXED` ➔ `READY` ➔ `ARCHIVED` ➔ `DELETED`).
- **REST API Presentation Layer**: Router `/api/v1/rag` with endpoints `POST /documents`, `GET /documents`, `GET /documents/{id}`, `DELETE /documents/{id}`, `POST /ingest`, `POST /retrieve`, `POST /query`, `GET /statistics`, `GET /analytics`, `GET /health`.
- **Developer Console — Knowledge Studio**: 3-panel UI (`testing-ui/index.html`) mounted at `/console` featuring Panel A (Document Library & Ingestion), Panel B (Chunk & Embedding Viewer), and Panel C (Retrieval & Reranking Inspector).
- **Architecture Decision Records & Graduation Suite**: `ADR 048` (Enterprise RAG Engine Architecture), `ADR 049` (Enterprise Retrieval Guidelines), `RUNTIME_BASELINE_v7.6.md`, `RUNTIME_CERTIFICATE_v7.6.md`, and `test_rag_full_stack_smoke.py`.

---

## [v7.5.0] - 2026-08-07

### Added
- **Enterprise Multi-Agent Orchestration Runtime** (`backend/app/agents/`): Provider-independent, framework-independent multi-agent platform orchestrating autonomous worker agents, supervisor agents, planner agents, team composition, task queues, mailbox messaging, and delegation depth without modifying lower runtime layers.
- **`AgentDefinition` & `AgentInstance`**: Blueprint vs worker pod separation enabling scalable worker instance replication.
- **`AgentPersona` & `AgentCapabilities`**: Behavioral personas (`communication_style`, `expertise`, `tone`, `constraints`, `reasoning_style`) separated from permissions and capabilities.
- **`AgentPermissionSet` & `AgentExecutionBudget`**: Fine-grained permissions (`CAN_DELEGATE`, `CAN_APPROVE`, `CAN_EXECUTE_TOOLS`, `CAN_ACCESS_MEMORY`) and execution safety budgets (max runtime, retries, tool calls, delegation depth, tokens, cost).
- **`AgentLifecycleManager`**: State machine transitions (`CREATED` ➔ `REGISTERED` ➔ `READY` ➔ `RUNNING` ➔ `WAITING` ➔ `DELEGATING` ➔ `PAUSED` ➔ `COMPLETED` ➔ `FAILED` ➔ `TERMINATED`).
- **`AgentTeam` & `TeamManager`**: Multi-agent team composition and lifecycle (`CREATED` ➔ `READY` ➔ `RUNNING` ➔ `WAITING` ➔ `COMPLETED` ➔ `FAILED`).
- **Reference Team Templates** (`backend/app/agents/templates/`): Pre-built specs (`mobility_support`, `travel_booking`, `research_discovery`, `code_review`).
- **`CommunicationManager` & `AgentMailbox`**: Inter-agent messaging and event-driven notifications via `WorkflowEventBus` (v6.5).
- **`TaskQueue`, `TaskScheduler` & `DelegationManager`**: Task dispatching, priority scheduling, delegation depth tracking, and budget enforcement.
- **Specialized Agents**: `SupervisorAgent`, `PlannerAgent`, `CoordinatorAgent`, and `AgentRouter`.
- **Reserved Extensions Architecture**: Created `backend/app/agents/extensions/` directory for custom strategies and routers.
- **REST API Presentation Layer**: Router `/api/v1/agents` with endpoints `POST /register`, `POST /execute`, `POST /delegate`, `POST /message`, `POST /task`, `GET /`, `GET /{agent_id}`, `GET /statistics`, `GET /analytics`, `GET /health`.
- **Developer Console — Agent Studio**: 3-panel UI (`testing-ui/index.html`) mounted at `/console` featuring Panel A (Live Multi-Agent Team Graph), Panel B (Execution Tree & Mailbox Stream), and Panel C (Agent Registry & Capability Inspector).
- **Architecture Decision Records & Graduation Suite**: `ADR 046` (Enterprise Multi-Agent Orchestration Runtime Architecture), `ADR 047` (Agent Engineering Guidelines), `RUNTIME_BASELINE_v7.5.md`, and `RUNTIME_CERTIFICATE_v7.5.md`.

---

## [v7.4.0] - 2026-08-07

### Added
- **Enterprise Graph Runtime Integration** (`backend/app/graph_runtime/`): Decoupled runtime orchestration engine executing workflow DAG plans, scheduling, navigation, middleware pipelines, and runtime manager coordination.
- **`GraphExecutionPlan` & `GraphPlanner`**: Execution DAG planning model separating graph planning from execution scheduling.
- **`GraphScheduler` & `GraphCursor`**: Graph traversal scheduler tracking execution depth, parent/child nodes, and branch navigation.
- **`GraphRuntimePipeline` Middleware**: 9-stage middleware pipeline (`Validation` ➔ `Authorization` ➔ `Memory Injection` ➔ `Tool Resolution` ➔ `Prompt Rendering` ➔ `Runtime Execution` ➔ `Checkpoint` ➔ `Streaming` ➔ `Events`).
- **Execution Policies**: `GraphRuntimePolicy`, `RetryPolicy`, `RetryDecision`, `BackoffStrategy`, and `TimeoutPolicy`.
- **State & Context Snapshots**: `NodeExecutionContext` and `ExecutionTrace` supporting exact step-by-step state replay and inspection.
- **Integrations**: `GraphCheckpointIntegration` (Phase 6.6) and `GraphInterruptIntegration` (Phase 6.8 HITL).
- **Reserved Extensions Architecture**: Created `backend/app/graph_runtime/extensions/` directory for custom planners, schedulers, and middleware.
- **REST API Presentation Layer**: Router `/api/v1/graph-runtime` with endpoints `POST /execute`, `POST /resume`, `POST /pause`, `POST /cancel`, `GET /session`, `GET /health`, `GET /statistics`, `GET /analytics`.
- **Developer Console — Graph Studio**: 3-panel UI (`testing-ui/index.html`) mounted at `/console` featuring Panel A (Live DAG Visualizer), Panel B (Execution Timeline), and Panel C (Node Execution Inspector).
- **Architecture Decision Records & Graduation Suite**: `ADR 044` (Enterprise Graph Runtime Architecture), `ADR 045` (Graph Runtime Guidelines), `RUNTIME_BASELINE_v7.4.md`, and `RUNTIME_CERTIFICATE_v7.4.md`.

---

## [v7.3.0] - 2026-08-07

### Added
- **Enterprise Tool Runtime** (`backend/app/tools/`): Provider-independent, framework-independent, secure tool orchestration, discovery, authorization, pipeline processing, chaining, and telemetry layer.
- **`ToolSchema` & `ToolManifest`**: Structural JSON Schema parameter definitions, manifest metadata, capabilities, and future-proof deprecation fields (`deprecated`, `replacement_tool`).
- **`ToolDiscoveryService`**: Tool query service searching registered manifests by type (`MATH`, `TIME`, `TEXT`, `UTILITY`), capability (`supports_async`, `supports_batch`), and permission.
- **`ToolPipeline` & `PipelineResult`**: 6-step execution pipeline (`Validation` ➔ `Permission Check` ➔ `Policy Evaluation` ➔ `Execution` ➔ `Analytics` ➔ `Event Emission`).
- **`ToolChain` & `ChainResult`**: Multi-step sequential tool execution engine feeding output of step $N$ into input of step $N+1$.
- **Built-in Reference Tools** (`backend/app/tools/builtin/`): `EchoTool`, `CalculatorTool` (`add`, `subtract`, `multiply`, `divide`), `DatetimeTool`, `UUIDTool`.
- **Reserved Adapter Architecture**: Created `backend/app/tools/adapters/` directory for future production integrations (Phase 7.7).
- **Formal Tool Events**: `ToolRegistered`, `ToolValidated`, `ToolStarted`, `ToolCompleted`, `ToolFailed`, `ToolTimedOut`, `ToolSkipped`, `ToolCancelled` published directly to `WorkflowEventBus` (v6.5).
- **REST API Presentation Layer**: Router `/api/v1/tools` with endpoints `POST /execute`, `GET /`, `GET /{tool_name}`, `GET /health`, `GET /statistics`, `POST /validate`, `POST /pipeline`, `POST /chain`.
- **Developer Console — Tool Studio & Overview**: Interactive UI panel (`testing-ui/index.html`) mounted at `/console` featuring Runtime Overview Dashboard (Runtime ✔, Prompt ✔, Memory ✔, Tools ✔, Provider ✔, Health ✔), available tool cards, JSON argument editor, pipeline trace visualizer, and schema viewer.
- **Architecture Decision Records & Graduation Suite**: `ADR 042` (Enterprise Tool Runtime Architecture), `ADR 043` (Tool Engineering Guidelines), `RUNTIME_CERTIFICATE_v7.3.md` (Runtime Graduation Certificate), `RUNTIME_DEPENDENCY_MATRIX.md`, and `RUNTIME_PACKAGE_INDEX.md`.

---

## [v7.2.0] - 2026-08-07

### Added
- **Enterprise Memory Runtime** (`backend/app/memory/`): Provider-independent, framework-independent conversation memory orchestration, lifecycle management, retrieval scoring, context assembly, and token window budget management layer.
- **`MemoryManager` Orchestrator**: Central memory management orchestrator with CRUD, search scoring, pinning/unpinning, archiving, policy cleanup, and `WorkflowEventBus` integration (v6.5).
- **`MemoryLifecycleManager`**: Formal state transition rules (`CREATED` ➔ `ACTIVE` ➔ `PINNED` ➔ `ARCHIVED` ➔ `EXPIRED` ➔ `DELETED`).
- **`ContextAssemblyStrategy` Abstraction**: Flexible strategy assembly (`RecentStrategy`, `ImportanceStrategy`, `HybridStrategy`, `SlidingWindowStrategy`).
- **Prompt Engine Integration**: Implemented `MemoryVariableProvider` extending Prompt Engine's `VariableProvider` ABC, dynamically resolving `{conversation_memory}` variables for `PromptManager`.
- **`MemoryTokenEstimator` & `ContextWindowBudget`**: Token budget calculation for single memory, list of memories, and full `MemoryContext`.
- **Repository Abstractions**: `MemoryRepository` ABC, `InMemoryMemoryRepository`, `MemoryFactory`, `MemoryRegistry`, and `MemoryStorageCapabilities`.
- **Telemetry & Health Reports**: `MemoryHealthManager`, `MemoryStatistics`, `MemoryMetrics`, `MemoryAnalyticsManager`, `MemoryQualityAnalyzer`, `MemoryCostEstimator`, `MemorySerializer`, and `MemoryVersion`.
- **REST API Presentation Layer**: Router `/api/v1/memory` with endpoints `POST /`, `GET /`, `GET /{id}`, `DELETE /{id}`, `POST /search`, `POST /context`, `POST /cleanup`, `GET /metrics`, `GET /statistics`, `GET /health`.
- **Developer Console — Memory Studio**: Interactive UI panel (`testing-ui/index.html`) mounted at `/console` featuring active memory inspector, lifecycle timeline, token budget visualizer, search scoring tester, and context preview.
- **Architecture Decision Records**: `ADR 040` (Enterprise Memory Runtime Architecture with Future Compatibility Matrix) and `ADR 041` (Memory Engineering Guidelines).

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
