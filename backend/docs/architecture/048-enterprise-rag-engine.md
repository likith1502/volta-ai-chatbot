# ADR 048: Enterprise RAG Engine Architecture

## Status
Accepted

## Date
2026-08-07

## Context
Following Phase 7.5 (Enterprise Multi-Agent Orchestration Runtime), Phase 7.6 establishes the **Enterprise RAG Engine** under package `backend/app/rag/`. The platform requires a provider-independent, storage-independent Retrieval-Augmented Generation engine that coordinates document ingestion, parsing, chunking, embedding, vector indexing, retrieval planning, pluggable reranking, citation generation, and context assembly without modifying core runtime packages (`app/runtime/`, `app/prompt/`, `app/memory/`, `app/tools/`, `app/graph_runtime/`, `app/agents/`).

## Decision
We establish the **Enterprise RAG Engine** under package `backend/app/rag/`.

### Key Architectural Decisions
1. **Separation of Ingestion Runtime and Query Runtime**:
   - `IngestionRuntime` (`ingestion_runtime.py`): Parse ➔ Chunk ➔ Embed ➔ Index.
   - `QueryRuntime` (`query_runtime.py`): Rewrite ➔ Plan ➔ Retrieve ➔ Rerank ➔ Context ➔ Citations.
2. **Provider & Storage Independence**:
   - Abstract interfaces (`EmbeddingProvider`, `VectorRepository`, `BaseDocumentParser`, `CacheProvider`) with in-memory reference implementations. External vendor drivers belong in reserved package directories (`backend/app/rag/providers/`, `parsers/`, `extensions/`).
3. **Retrieval Planning & Pluggable Reranking**:
   - `RetrievalPlanner` generates `RetrievalPlan`. `BaseReranker` provides pluggable strategy implementations (`CosineReranker`, `HybridReranker`, `MetadataReranker`, `WeightedReranker`, `CrossEncoderReranker`).
4. **Decoupled Chunk & Embedding Models**:
   - `Chunk` (un-embedded text block) separated from `EmbeddedChunk` (vector binding).
5. **No Direct LLM Calls**:
   - `RAGManager` delegates all conversational generation to `PromptManager` (v7.1) and `RuntimeManager` (v7.0) via public interfaces.

---

## Full Runtime Stack Topology

```mermaid
graph TD
    REngine["Phase 7.0: LLM Runtime Engine (v7.0)"]
    PEngine["Phase 7.1: Prompt Execution Engine (v7.1)"]
    MEngine["Phase 7.2: Enterprise Memory Runtime (v7.2)"]
    TEngine["Phase 7.3: Enterprise Tool Runtime (v7.3)"]
    GEngine["Phase 7.4: Graph Runtime Integration (v7.4)"]
    AEngine["Phase 7.5: Enterprise Multi-Agent Orchestration Runtime (v7.5)"]
    RAGEngine["Phase 7.6: Enterprise RAG Engine (v7.6)"]
    IntEngine["Phase 7.7: Production Integrations"]
    DepEngine["Phase 7.8: Deployment & Scaling"]

    REngine --> PEngine
    PEngine --> MEngine
    MEngine --> TEngine
    TEngine --> GEngine
    GEngine --> AEngine
    AEngine --> RAGEngine
    RAGEngine --> IntEngine
    IntEngine --> DepEngine
```

---

## Consequences
- **Zero Framework Lock-in**: Easy swapping of embedding models, vector stores, and parsers without refactoring core code.
- **Auditability**: `Citation` engine and `RetrievalExplanation` provide exact traceability for enterprise audit compliance.
- **Resource Control**: `RetrievalBudget` enforces token and chunk bounds.
