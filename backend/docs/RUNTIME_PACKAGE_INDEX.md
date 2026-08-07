# Enterprise Messaging Runtime Package Index

> **VOLTA AI Chatbot Platform** | **Package Index & Architecture Reference**
> **Release Version**: `v7.6.0` | **Status**: Active Reference

---

## Package Index

### 1. `backend/app/runtime/` — Enterprise LLM Runtime Engine (v7.0)
- **Primary Responsibility**: Provides a provider-independent, framework-independent LLM execution engine capable of executing model requests, managing session histories, handling streaming, and tracking token telemetry.

### 2. `backend/app/prompt/` — Prompt Execution Engine (v7.1)
- **Primary Responsibility**: Provides prompt composition, template compilation, validation, linting, security policy enforcement, variable resolution, and middleware pipeline processing.

### 3. `backend/app/memory/` — Enterprise Memory Runtime (v7.2)
- **Primary Responsibility**: Provides intelligent conversation memory orchestration, lifecycle transitions, retrieval scoring, context assembly strategies, and token window budget management.

### 4. `backend/app/tools/` — Enterprise Tool Runtime (v7.3)
- **Primary Responsibility**: Provides secure tool registration, JSON Schema discovery, permission authorization, execution policy enforcement, pipeline processing, sequential chaining, and telemetry dispatch.

### 5. `backend/app/graph_runtime/` — Enterprise Graph Runtime Integration (v7.4)
- **Primary Responsibility**: Provides StateGraph execution planning, navigation cursor scheduling, 9-stage middleware processing, retry decisions, timeout enforcement, state snapshot replay, and interrupt handling.

### 6. `backend/app/agents/` — Enterprise Multi-Agent Orchestration Runtime (v7.5)
- **Primary Responsibility**: Provides autonomous agent blueprint definitions, worker instances, behavioral personas, permission sets, team composition, inter-agent mailbox messaging, priority task scheduling, and supervisor delegation.

### 7. `backend/app/rag/` — Enterprise RAG Engine (v7.6)
- **Primary Responsibility**: Provides provider-independent document ingestion, parsing, chunking, embedding abstraction, vector indexing, retrieval planning, pluggable reranking, citation generation, context assembly, caching, and retrieval explanations.
- **Key Modules**:
  - `manager.py`: `RAGManager` central orchestrator.
  - `ingestion_runtime.py`: `IngestionRuntime` handling Parse ➔ Chunk ➔ Embed ➔ Index.
  - `query_runtime.py`: `QueryRuntime` handling Rewrite ➔ Plan ➔ Retrieve ➔ Rerank ➔ Context ➔ Citations.
  - `planner.py`: `RetrievalPlanner` generating `RetrievalPlan`.
  - `reranker.py`: `BaseReranker` ABC with `CosineReranker`, `HybridReranker`, `MetadataReranker`, `WeightedReranker`, `CrossEncoderReranker`.
  - `cache.py`: `CacheProvider` ABC & `InMemoryCacheProvider`.
  - `job_manager.py`: `JobManager` tracking background `IngestionJob` tasks.
