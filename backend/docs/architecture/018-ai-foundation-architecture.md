# ADR 018: AI Foundation Architecture & Enterprise Refinements

## Status
Accepted

## Date
2026-08-03

---

## Context
Integrating conversational AI capabilities into the Volta platform requires a modular, provider-agnostic engine architecture that decouples external LLM SDKs (OpenAI, Anthropic Claude, Google Gemini, Azure OpenAI, Ollama) from core application orchestration services.

The v5.0 Enterprise Refinement pass introduces an **AI Tool Execution Framework**, **Memory Retrieval Strategy Pattern**, and **Prompt Builder**, creating an extensible enterprise AI Foundation.

---

## Technical Decisions & Rationale

### 1. Abstract AI Provider Interface (`AIProvider`)
- **Decision**: All conversational AI engines implement `AIProvider` (`app/ai/base.py`) with a single abstract method:
  `async def generate_response(self, request: AIRequest) -> AIResponse:`
- **Rationale**: Isolates external SDKs and API request structures. `ChatService` and application routers interact exclusively with provider-agnostic request/response DTOs (`AIRequest`, `AIResponse`, `AITokenUsage`, `AIToolCall`).

### 2. Provider Factory Pattern (`AIProviderFactory`)
- **Decision**: AI provider instances are constructed via `AIProviderFactory.get_provider()` (`app/ai/factory.py`) driven by `settings.AI_PROVIDER`.
- **Rationale**: Enables swapping AI engines (e.g. switching from OpenAI to Anthropic Claude or local Ollama) dynamically via environment configuration without modifying `ChatService` or API routers.

### 3. Provider-Independent Tool Execution Framework (`app/ai/tools/`)
- **Decision**: Introduced `AITool(ABC)` base interface, `RecommendationTool`, `AIToolRegistry`, and `AIToolDispatcher`.
- **Rationale**: AI Providers issue tool call requests (`AIToolCall`), but **never** execute business logic directly. `AIToolDispatcher` resolves and executes registered tools (e.g., calling `RecommendationService`), preventing `ChatService` from coupling to individual domain tools.

### 4. Memory Retrieval Strategy Pattern (`app/ai/memory/`)
- **Decision**: Introduced `MemoryStrategy(ABC)` interface and `RecentConversationStrategy`, instantiated via `MemoryStrategyFactory.get_strategy()` (`MEMORY_STRATEGY=recent`).
- **Rationale**: Establishes a pluggable memory strategy pipeline. Future semantic memory retrieval, vector databases (PGVector, Qdrant), or hybrid search strategies can be plugged in via configuration with zero modifications to `ChatService`.

### 5. Centralized Prompt Builder (`PromptBuilder`)
- **Decision**: Introduced `PromptBuilder` (`app/ai/prompts/prompt_builder.py`) to handle prompt composition.
- **Rationale**: Merges system prompts (`VOLTA_SYSTEM_PROMPT`), user memories, conversation history, and current user input into `AIRequest`. Keeps prompt formatting out of `ChatService`.

### 6. Refined `ChatService` Workflow
- **Decision**: `ChatService` (`app/services/chat.py`) acts strictly as a high-level application orchestrator:
  1. Load Conversation
  2. Retrieve Memories (`MemoryStrategy`)
  3. Build Prompt (`PromptBuilder`)
  4. Invoke AI Engine (`AIProvider`)
  5. Dispatch Tool Requests (`AIToolDispatcher`)
  6. Persist Turns & Commit Transaction
- **Rationale**: Enforces single responsibility and clean architecture across all AI interactions.
