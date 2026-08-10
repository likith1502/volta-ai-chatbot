# VOLTA AI Platform — End-to-End Execution Walkthroughs

This directory contains implementation-accurate, source-verified developer walkthroughs explaining how requests flow through the **VOLTA AI Platform** end-to-end.

All walkthroughs document the repository **AS IT EXISTS**, tracing execution through FastAPI REST routers, Pydantic schemas, application services, domain repositories, runtime managers, and integration provider adapters.

---

## 📚 Walkthrough Catalog

1. [**Standard Chat Request Walkthrough**](standard-chat-request.md)
   - Traces `POST /api/v1/chat` conversational turns.
   - Covers user validation, conversation session creation, memory retrieval, prompt construction, LLM generation, tool dispatching, database persistence, and response enveloping.

2. [**RAG Query & Context Retrieval Walkthrough**](rag-query.md)
   - Traces `POST /api/v1/rag/query` and `POST /api/v1/rag/retrieve`.
   - Covers query rewriting, retrieval planning, vector similarity search, reranking (Cosine, Hybrid, Cross-Encoder), citation building, and RAG context-augmented generation.

3. [**Multi-Agent Execution & Delegation Walkthrough**](multi-agent-execution.md)
   - Traces `POST /api/v1/agents/execute`, `POST /api/v1/agents/delegate`, and `POST /api/v1/agents/message`.
   - Covers `AgentRuntimeManager`, `SupervisorAgent`, `PlannerAgent`, `DelegationManager`, `TaskQueue` prioritization, `AgentMailbox` messaging, and agent task execution turns.

4. [**Document Ingestion Pipeline Walkthrough**](document-ingestion.md)
   - Traces `POST /api/v1/rag/documents` and `POST /api/v1/rag/ingest`.
   - Covers document registration, `DocumentLifecycleManager` states (`CREATED` ➔ `ACTIVE`), text parsing, chunking, `EmbeddingProvider` vector generation, and `VectorRepository` indexing.

---

## 🏛️ Frozen Subsystem Layers Reference

Every walkthrough maps to one or more frozen core subsystem layers (v7.0–v7.8):

| Layer | Subsystem Name | Source Package | Core Manager / Entry Point |
| :--- | :--- | :--- | :--- |
| **v7.0** | Runtime Engine | `app.runtime` | `RuntimeManager` ([backend/app/runtime/manager.py](file:///c:/Users/Likit/Desktop/Volta-AI-Chatbot/backend/app/runtime/manager.py)) |
| **v7.1** | Prompt Engine | `app.prompt` | `PromptManager` ([backend/app/prompt/manager.py](file:///c:/Users/Likit/Desktop/Volta-AI-Chatbot/backend/app/prompt/manager.py)) |
| **v7.2** | Memory Repository | `app.memory` | `MemoryManager` ([backend/app/memory/manager.py](file:///c:/Users/Likit/Desktop/Volta-AI-Chatbot/backend/app/memory/manager.py)) |
| **v7.3** | Tool Execution Engine | `app.tools` | `ToolManager` ([backend/app/tools/manager.py](file:///c:/Users/Likit/Desktop/Volta-AI-Chatbot/backend/app/tools/manager.py)) |
| **v7.4** | Graph State Runtime | `app.graph_runtime` | `GraphRuntimeManager` ([backend/app/graph_runtime/manager.py](file:///c:/Users/Likit/Desktop/Volta-AI-Chatbot/backend/app/graph_runtime/manager.py)) |
| **v7.5** | Multi-Agent Runtime | `app.agents` | `AgentRuntimeManager` ([backend/app/agents/manager.py](file:///c:/Users/Likit/Desktop/Volta-AI-Chatbot/backend/app/agents/manager.py)) |
| **v7.6** | RAG Engine | `app.rag` | `RAGManager` ([backend/app/rag/manager.py](file:///c:/Users/Likit/Desktop/Volta-AI-Chatbot/backend/app/rag/manager.py)) |
| **v7.7** | Production Integrations | `app.integrations` | `IntegrationManager` ([backend/app/integrations/manager.py](file:///c:/Users/Likit/Desktop/Volta-AI-Chatbot/backend/app/integrations/manager.py)) |
| **v7.8** | Deployment & Operations | `app.deployment` | `DeploymentManager` ([backend/app/deployment/manager.py](file:///c:/Users/Likit/Desktop/Volta-AI-Chatbot/backend/app/deployment/manager.py)) |
