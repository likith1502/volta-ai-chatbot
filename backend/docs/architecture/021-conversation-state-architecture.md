# 021 - Conversation State Architecture

**Status**: Accepted  
**Date**: August 4, 2026  
**Scope**: Foundation Architecture (Phase 6.1)

---

## 1. Purpose

The Conversation State Architecture establishes a strongly-typed, provider-agnostic, framework-isolated single source of truth for runtime state management across AI orchestration workflows. Every execution node in the future LangGraph engine consumes and returns a `ConversationState` instance.

> **State Ownership Principle**: `ConversationState` owns runtime workflow state only. Persistent business entities remain the responsibility of the database layer.

---

## 2. Core Responsibilities

- **Transport Object**: Acts as an immutable, serializable data transfer container across workflow nodes.
- **Provider Agnostic**: Contains no vendor-specific models or LLM execution logic (OpenAI, Claude, Gemini, etc.).
- **Framework Isolated**: Zero runtime dependencies on web frameworks (FastAPI), databases (SQLAlchemy), or external caches (Redis).
- **Sub-Model Modularization**: Groups state into dedicated sub-models to ensure scalability, clean separation of concerns, and future-proof extensibility.

---

## 3. Structural Design & Sub-Models

`ConversationState` composes the following strongly typed sub-models:

```
ConversationState (state_version=1)
├── metadata: StateMetadata
│   ├── state_id: UUID
│   ├── parent_state_id: UUID | None
│   ├── correlation_id: UUID
│   ├── request_id: UUID | None
│   ├── session_id: UUID | None
│   ├── created_at: datetime
│   ├── updated_at: datetime
│   └── version: int = 1
├── conversation: ConversationData
│   ├── conversation_id: UUID
│   ├── user_id: str | None
│   ├── current_message: dict | None
│   └── history: list[dict]
├── runtime: RuntimeState
│   ├── workflow_step: str
│   ├── workflow_status: WorkflowStatus
│   ├── execution_mode: ExecutionMode
│   └── checkpoint_id: UUID | None
├── execution: ExecutionState
│   ├── tool_calls: list[dict]
│   ├── tool_results: list[dict]
│   ├── node_results: dict[str, Any]
│   ├── executed_nodes: list[str]
│   └── errors: list[dict]
└── memory: MemoryState
    ├── short_term_memory: dict
    ├── long_term_memory: dict
    ├── detected_intent: dict | None
    └── extracted_entities: dict
```

### Key Elements:
- **`state_id` & `parent_state_id`**: Unique snapshot identifier and parent lineage link, enabling DAG-based state history, retries, branching, and workflow replay.
- **`StateMetadata`**: Enables distributed tracing, request correlation, auditing, and observability without altering state payloads.
- **`state_version`**: Explicit schema versioning allowing backward-compatible state migrations.
- **`checkpoint_id`**: Reserved placeholder for pause, resume, and checkpoint operations.
- **`executed_nodes`**: List tracking node execution sequence (`["input_node", "intent_node", "llm_node"]`).
- **`node_results`**: Dictionary allowing pipeline nodes (`intent`, `entities`, `memory`, `guardrail`) to register intermediate outputs cleanly.

---

## 4. Immutability & Update Strategy

To align with LangGraph's functional graph execution model, `ConversationState` is treated as **immutable**:

> **Project Rule**: `ConversationState` must be treated as immutable. Any state modification produces a new `ConversationState` instance rather than mutating an existing instance in place.

### Immutable Update Pattern:
```python
new_state = current_state.with_update(
    workflow_step="llm_node",
    detected_intent={"intent": "book_charger", "confidence": 0.98},
    node_results={"intent_detector": {"status": "success"}}
)
```
`with_update()` creates a deep copy/re-validated model, assigns `parent_state_id = current_state.state_id`, generates a new `state_id`, updates node history, touches `metadata.updated_at`, and leaves `current_state` untouched.

---

## 5. Serialization Rules

`ConversationState` must serialize deterministically to and from native Python types, JSON strings, Redis keys, and SQL databases without data loss.

```
ConversationState (Model)
       │  .to_dict()
       ▼
   Python dict
       │  json.dumps()
       ▼
  JSON Payload
       │
 ┌─────┴──────────────┐
 ▼                    ▼
Redis Cache      Database Storage
```

---

## 6. State Lifecycle Diagram

```
[ Create ]
   │  Initialize default state or create via ConversationStateManager
   ▼
[ Load ]
   │  Retrieve active state payload for current conversation ID
   ▼
[ Update ]
   │  Workflow node executes and returns new state via with_update()
   ▼
[ Checkpoint ] (Reserved)
   │  Persist checkpoint snapshot with checkpoint_id when interrupted
   ▼
[ Resume ] (Reserved)
   │  Restore state snapshot from checkpoint_id
   ▼
[ Complete ]
   │  Workflow reaches terminal node with WorkflowStatus.COMPLETED
   ▼
[ Archive ]
   │  State saved to persistent database or session cleared
```

---

## 7. Architecture ASCII Diagram

```
                 ┌───────────────────────────────────────┐
                 │       User Chat / Web Request         │
                 └──────────────────┬────────────────────┘
                                    │
                                    ▼
                 ┌───────────────────────────────────────┐
                 │       ConversationStateManager        │ (Abstract Contract)
                 └──────────────────┬────────────────────┘
                                    │  loads/saves
                                    ▼
 ┌─────────────────────────────────────────────────────────────────────────┐
 │                            ConversationState                            │
 │                                                                         │
 │ ┌───────────────────┐ ┌───────────────────┐ ┌─────────────────────────┐ │
 │ │   StateMetadata   │ │  ConversationData │ │       RuntimeState      │ │
 │ └───────────────────┘ └───────────────────┘ └─────────────────────────┘ │
 │ ┌───────────────────┐ ┌───────────────────┐                             │
 │ │   ExecutionState  │ │    MemoryState    │                             │
 │ └───────────────────┘ └───────────────────┘                             │
 └──────────────────────────────────┬──────────────────────────────────────┘
                                    │
       ┌────────────────────────────┼────────────────────────────┐
       ▼                            ▼                            ▼
┌──────────────┐             ┌──────────────┐             ┌──────────────┐
│  Node: Intent│ ──────────> │   Node: LLM  │ ──────────> │  Node: Tool  │
└──────────────┘             └──────────────┘             └──────────────┘
```

---

## 8. Future Persistence & Integration Architecture

`ConversationState` serves as the primary transport model for:
- **LangGraph Orchestrator**: Consumes and returns state channels across graph nodes.
- **Redis Cache Store**: Key-value fast session persistence via `ConversationStateManager`.
- **Vector Database**: Semantic memory retrieval node outputs stored in `memory` state.
- **Event Bus & WebSockets**: Telemetry stream consumers receiving `WorkflowEvent` payloads.
- **Workflow Replay & Debugging**: State lineage graph reconstructed using `state_id` and `parent_state_id`.
- **Observability Pipeline**: Request tracing and latency logging via `StateMetadata`.

---

## 9. Risk Register

| Risk | Severity | Mitigation Strategy |
| :--- | :--- | :--- |
| **State payload size growth** | Low | Offload large historical message lists to long-term memory/DB storage when exceeding turn limits. |
| **Schema evolution & migration** | Low | `state_version` field enables versioned deserializers and schema migration handlers in `from_dict()`. |
| **Large binary payloads in state** | Medium | Strictly enforce storing references/URLs to binary assets rather than raw bytes within `node_results`. |

---

## 10. Explicit Non-Goals

This chapter intentionally **DOES NOT** include:
- ❌ LangGraph workflow nodes or graph building
- ❌ Redis state storage or caching implementation
- ❌ Checkpoint persistence engine
- ❌ State recovery or fault tolerance handlers
- ❌ Streaming or SSE connection handling
- ❌ WebSockets communication
- ❌ Provider execution (OpenAI, Claude, Gemini calls)
- ❌ Tool invocation logic
- ❌ Database models or SQLAlchemy repositories
- ❌ Business domain logic

---

## 11. Architecture Review Verification

- [x] **No circular imports**: Modular package structure with clean dependency graph.
- [x] **No framework leakage**: Zero dependencies on FastAPI, WebSockets, or HTTP frameworks.
- [x] **No provider leakage**: No vendor SDK references.
- [x] **No database dependency**: Pure memory/data structures. Business entities belong in DB.
- [x] **No Redis dependency**: Store contract defined via abstract base class.
- [x] **No LangGraph dependency**: Transport object created independently of execution graph.
- [x] **Serializable**: Seamless `to_dict()` and `from_dict()` support.
- [x] **Immutable-friendly**: `with_update()` pattern enforces functional updates and deep copies.
- [x] **Async-ready**: Abstract manager contracts use native async definitions.
- [x] **Thread-safe**: Value semantics on data transport objects.
- [x] **SOLID & Open/Closed**: Extensible via composition and abstract contract interfaces.
