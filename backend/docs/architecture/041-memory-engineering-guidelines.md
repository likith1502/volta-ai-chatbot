# ADR 041: Memory Engineering Guidelines & Extension Standards

## Status
Accepted

## Date
2026-08-07

## Context
As Phase 7 advances into Tool Runtime, Multi-Agent Runtime, and RAG Engine, clear memory engineering standards are required for memory creation, scoring, lifecycle management, and context assembly.

## Guidelines & Rules

### 1. Memory Creation & Type Classification
- Every memory element MUST specify a valid `MemoryType` (`SHORT_TERM`, `LONG_TERM`, `WORKING`, `SYSTEM`, `USER`, `SESSION`, `EPISODIC`, `SEMANTIC`, `CUSTOM`).
- Memory importance MUST be normalized between `0.0` and `1.0`.

### 2. State Transition Lifecycle Rules
- Memory status transitions MUST pass through `MemoryLifecycleManager`.
- Valid transitions: `CREATED` ➔ `ACTIVE` ➔ `PINNED` ➔ `ARCHIVED` ➔ `EXPIRED` ➔ `DELETED`.
- Pinned memories (`status = MemoryStatus.PINNED`) MUST NOT be evicted or expired by automated retention policies.

### 3. Context Assembly & Token Budgeting
- Context assembly MUST specify a `ContextAssemblyStrategy` (`RecentStrategy`, `ImportanceStrategy`, `HybridStrategy`, `SlidingWindowStrategy`).
- Total memory token consumption MUST NOT exceed `memory_token_budget` in `ContextWindowBudget`.

### 4. Extension Hooks
- Custom pre/post processing MUST be attached via extension hooks (`BeforeCreateHook`, `AfterCreateHook`, `BeforeSearchHook`, `AfterSearchHook`, `BeforeCleanupHook`, `AfterCleanupHook`, `BeforeContextBuildHook`, `AfterContextBuildHook`) in `app/memory/hooks.py`.
