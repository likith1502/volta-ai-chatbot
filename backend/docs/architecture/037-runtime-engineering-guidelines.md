# ADR 037: Runtime Engineering Guidelines & Extension Standards

## Status
Accepted

## Date
2026-08-07

## Context
As Phase 7 expands into multi-provider integrations, memory engines, tool runtimes, and multi-agent workflows, clear engineering guidelines are required to maintain architectural consistency, type safety, error mapping, and testing standards across all runtime modules.

## Guidelines & Rules

### 1. Provider Implementation Rules
- Every provider MUST extend `RuntimeProvider` ABC (`app/runtime/base.py`).
- Providers MUST NOT leak SDK-specific exception types to callers. All SDK errors must be caught and translated into standardized exceptions (`ProviderAuthenticationError`, `ProviderRateLimitError`, `ProviderUnavailableError`, `RuntimeExecutionError`).
- Provider code MUST remain isolated in `app/runtime/providers/<provider_name>_provider.py`.

### 2. Configuration Philosophy
- Hardcoded credentials, endpoints, or model names are strictly forbidden.
- Configurations MUST be loaded through `RuntimeConfig`, `ProviderConfig`, and `GenerationConfig` via `settings.py` or environment variables.

### 3. Middleware Extension Model
- Cross-cutting concerns (logging, metrics collection, request validation, rate limiting) MUST be implemented as `RuntimeMiddleware` components in `app/runtime/middleware/`.
- Middleware components MUST NOT mutate `RuntimeRequest` in non-deterministic ways.

### 4. Exception Mapping Standard
- Exceptions MUST inherit from `RuntimeException` (`app/runtime/exceptions.py`).
- HTTP routers MUST convert runtime domain exceptions to `StandardResponse` error payloads using HTTP status codes (401, 429, 502, 503, 504).

### 5. Testing & Offline Capability
- Every provider MUST be accompanied by unit tests using `MockProvider` or mock SDK clients.
- `DEMO_MODE=True` MUST allow automatic fallback to `MockProvider` when API keys are unconfigured.
