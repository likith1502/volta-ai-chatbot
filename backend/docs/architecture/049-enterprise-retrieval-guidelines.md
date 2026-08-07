# ADR 049: Enterprise Retrieval Guidelines & Extension Standards

## Status
Accepted

## Date
2026-08-07

## Context
As Phase 7 advances into Production Integrations (v7.7), clear engineering standards are required for document ingestion, chunking strategies, vector indexing, retrieval planning, pluggable reranking, and citation formatting.

## Guidelines & Rules

### 1. Provider Independence & Adapter Scoping
- External vector database SDKs (FAISS, Pinecone, Qdrant, Chroma) MUST be implemented as adapters under `backend/app/rag/providers/`.
- External document parsers MUST be implemented as parsers under `backend/app/rag/parsers/`.

### 2. Retrieval Budget Enforcement
- RAG retrieval MUST enforce `RetrievalBudget` limits (`max_chunks`, `max_context_tokens`, `max_citations`).

### 3. Context Assembly Contract
- Assembled `RAGContext` MUST be passed to lower runtime layers strictly via public `PromptManager` and `RuntimeManager` contracts.
- The RAG Engine MUST NOT call LLM vendor APIs directly.

### 4. Citation & Traceability
- Every retrieval operation MUST generate audit `Citation` references and `RetrievalExplanation` metadata.
