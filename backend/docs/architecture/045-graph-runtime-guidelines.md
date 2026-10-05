# ADR 045: Graph Runtime Engineering Guidelines & Extension Standards

## Status
Accepted

## Date
2026-08-07

## Context
As Phase 7 advances into Multi-Agent Runtime (v7.5) and RAG Engine (v7.6), clear engineering standards are required for graph execution planning, scheduling, state transitions, checkpointing, and middleware pipeline extensions.

## Guidelines & Rules

### 1. Inter-Layer Communication
- Graph Runtime MUST interact with lower runtime layers strictly through public contracts (`RuntimeManager`, `PromptManager`, `MemoryManager`, `ToolManager`).
- Direct internal state mutations or private property access are forbidden.

### 2. Planning & Scheduling Philosophy
- Graph planning (`GraphPlanner`) MUST remain decoupled from graph execution (`GraphRuntimeExecutor`).
- Execution plans MUST produce valid `GraphExecutionPlan` models before scheduling.

### 3. Middleware Extension Model
- Custom runtime logic (rate limiting, observability, custom authentication) MUST be implemented as `GraphRuntimeMiddleware` instances registered with `GraphRuntimePipeline`.
- Custom extensions MUST be placed in `backend/app/graph_runtime/extensions/`.
