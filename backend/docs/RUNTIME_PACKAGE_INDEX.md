# Enterprise Messaging Runtime Package Index

> **VOLTA AI Chatbot Platform** | **Package Index & Architecture Reference**
> **Release Version**: `v7.3.0` | **Status**: Active Reference

---

## Package Index

### 1. `backend/app/runtime/` — Enterprise LLM Runtime Engine (v7.0)
- **Primary Responsibility**: Provides a provider-independent, framework-independent LLM execution engine capable of executing model requests, managing session histories, handling streaming, and tracking token telemetry.
- **Key Modules**:
  - `manager.py`: `RuntimeManager` central orchestrator.
  - `provider.py`: `RuntimeProvider` ABC defining execution contracts.
  - `providers/gemini_provider.py`: Production integration for Google `google-genai` SDK (`gemini-2.5-flash` / `gemini-2.5-pro`).
  - `providers/mock_provider.py`: Offline mock provider for unit testing.
  - `session.py`: `RuntimeSession` managing turn history and token usage tracking.
  - `health.py`: `RuntimeHealthManager` system readiness check.

### 2. `backend/app/prompt/` — Prompt Execution Engine (v7.1)
- **Primary Responsibility**: Provides prompt composition, template compilation, validation, linting, security policy enforcement, variable resolution, and middleware pipeline processing.
- **Key Modules**:
  - `manager.py`: `PromptManager` decoupled prompt renderer & compiler orchestrator.
  - `compiler.py`: `PromptCompiler` translating profiles to executable prompts.
  - `profile.py`: `PromptProfile` separating prompt generation settings from raw templates.
  - `linter.py`: `PromptLinter` analyzing prompt quality and token efficiency.
  - `pipeline.py`: `PromptPipeline` 5-stage middleware execution engine.

### 3. `backend/app/memory/` — Enterprise Memory Runtime (v7.2)
- **Primary Responsibility**: Provides intelligent conversation memory orchestration, lifecycle transitions, retrieval scoring, context assembly strategies, and token window budget management.
- **Key Modules**:
  - `manager.py`: `MemoryManager` central memory orchestrator.
  - `lifecycle.py`: `MemoryLifecycleManager` handling state transitions (`CREATED` ➔ `ACTIVE` ➔ `PINNED` ➔ `ARCHIVED` ➔ `EXPIRED` ➔ `DELETED`).
  - `strategy.py`: `ContextAssemblyStrategy` ABC (`RecentStrategy`, `ImportanceStrategy`, `HybridStrategy`, `SlidingWindowStrategy`).
  - `scorer.py`: `MemoryScorer` calculating semantic relevance and temporal decay.
  - `budget.py`: `ContextWindowBudget` preventing token buffer overflows.

### 4. `backend/app/tools/` — Enterprise Tool Runtime (v7.3)
- **Primary Responsibility**: Provides secure tool registration, JSON Schema discovery, permission authorization, execution policy enforcement, pipeline processing, sequential chaining, and telemetry dispatch.
- **Key Modules**:
  - `manager.py`: `ToolManager` central tool orchestrator.
  - `tool.py`: `BaseTool` ABC and `Tool` domain model.
  - `schema.py`: `ToolSchema` defining JSON Schema inputs/outputs.
  - `manifest.py`: `ToolManifest` packaging specification with `deprecated` metadata.
  - `discovery.py`: `ToolDiscoveryService` querying tools by capability, type, and permission.
  - `pipeline.py`: `ToolPipeline` 6-step execution flow.
  - `chain.py`: `ToolChain` sequential multi-step tool execution.
  - `builtin/`: In-memory reference utilities (`EchoTool`, `CalculatorTool`, `DatetimeTool`, `UUIDTool`).
  - `adapters/`: Reserved package directory for future production tool connectors (Phase 7.7).
