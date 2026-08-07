# ADR 046: Enterprise Multi-Agent Orchestration Runtime Architecture

## Status
Accepted

## Date
2026-08-07

## Context
Following Phase 7.4 (Graph Runtime Integration), Phase 7.5 establishes the **Enterprise Multi-Agent Orchestration Runtime** under package `backend/app/agents/`. The platform requires a provider-independent, framework-independent multi-agent orchestration layer that coordinates autonomous AI worker agents, supervisor agents, planner agents, team composition, task queues, mailbox messaging, and delegation depth without modifying previously frozen runtime packages (`app/runtime/`, `app/prompt/`, `app/memory/`, `app/tools/`, `app/graph_runtime/`).

## Decision
We establish the **Enterprise Multi-Agent Orchestration Runtime** under package `backend/app/agents/`.

### Key Architectural Decisions
1. **Decoupled Agent Orchestration**:
   - `AgentRuntimeManager` is the single central orchestration entry point. Lower runtime layers are consumed strictly via public manager interfaces (`GraphRuntimeManager`, `ToolManager`, `MemoryManager`, `PromptManager`, `RuntimeManager`, `WorkflowEventBus`).
2. **Separation of Agent Definition and Agent Instance**:
   - `AgentDefinition` captures blueprint specifications (identity, role, persona, capabilities, default policy, budget, permissions).
   - `AgentInstance` captures active worker pod state (instance ID, definition ID, active task, lifecycle state, local context).
3. **Event-Driven Inter-Agent Communication**:
   - `AgentMessage` and `AgentMailbox` managed via `CommunicationManager` publishing event notifications directly to `WorkflowEventBus` (v6.5).
4. **Task System & Delegation**:
   - `AgentTask`, `TaskQueue`, `TaskScheduler`, and `DelegationManager` supporting priority queuing, sub-task delegation, delegation depth limits, and budget enforcement.
5. **Team Composition**:
   - `AgentTeam`, `TeamRegistry`, and `TeamManager` supporting multi-agent team execution topologies (`SupervisorAgent` ➔ `PlannerAgent` / `ResearchAgent` / `ToolAgent` / `ReviewerAgent`).

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
    RAGEngine["Phase 7.6: RAG Engine"]
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
- **Zero Framework Coupling**: Eliminates dependency on external multi-agent SDKs (AutoGen, CrewAI, LangGraph).
- **Scalable Worker Pods**: `AgentDefinition` vs `AgentInstance` enables spawning multiple worker pods of the same blueprint type.
- **Robust Delegation Safety**: Delegation depth limits and budget checks prevent infinite delegation loops.
