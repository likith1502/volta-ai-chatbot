# ADR 047: Agent Engineering Guidelines & Extension Standards

## Status
Accepted

## Date
2026-08-07

## Context
As Phase 7 advances into RAG Engine (v7.6) and Production Integrations (v7.7), clear engineering standards are required for multi-agent delegation, persona separation, task scheduling, team composition, and inter-agent mailbox communication.

## Guidelines & Rules

### 1. Inter-Layer Communication
- Agents MUST interact with lower runtime layers strictly through public contracts (`GraphRuntimeManager`, `ToolManager`, `MemoryManager`, `PromptManager`, `RuntimeManager`).
- Direct internal state mutations or private property access of lower layers are forbidden.

### 2. Single Orchestration Entry Point
- `AgentRuntimeManager` is the single central orchestration entry point. All agent task executions, registrations, and delegations MUST pass through `AgentRuntimeManager`.

### 3. Delegation Safety & Budget Enforcement
- Every delegation turn MUST check `delegator.has_permission(AgentPermission.CAN_DELEGATE)`.
- Delegation depth MUST NOT exceed `max_delegation_depth` configured in `AgentExecutionBudget`.
- Exhausted agent budgets MUST raise `AgentBudgetExhaustedError`.

### 4. Extension Model
- Custom multi-agent strategies, routers, and schedulers MUST be placed in `backend/app/agents/extensions/`.
