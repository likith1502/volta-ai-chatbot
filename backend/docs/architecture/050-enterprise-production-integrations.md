# ADR 050: Enterprise Integration Platform Architecture

> **VOLTA Urban Mobility AI Platform**
> **Status**: Accepted | **Date**: 2026-08-07 | **Phase**: v7.7.0

---

## Context

Phases v7.0–v7.6 established a 7-tier frozen Enterprise Runtime Stack (LLM Runtime, Prompt Engine, Memory Runtime, Tool Runtime, Graph Runtime, Multi-Agent Runtime, RAG Engine). All runtime layers are permanently frozen and immutable.

Phase 7.7 must connect the frozen runtime stack to production infrastructure (storage, vector databases, LLMs, authentication, databases, observability, messaging, search, schedulers, secret management) without modifying any core runtime package.

---

## Decision

Implement the **Enterprise Integration Platform** (`backend/app/integrations/`) as an independent package providing:

1. **`IntegrationProvider` ABC** as the universal adapter contract.
2. **`IntegrationRegistry`** for adapter registration, capability discovery, and priority failover.
3. **`IntegrationManager`** as the single orchestration entry point.
4. **`SecretProvider` ABC** (`EnvSecretProvider`) separating credentials from configuration.
5. **`IntegrationHealthManager`** aggregating per-adapter health into a single platform health report with `HealthLevel` (`GREEN`, `YELLOW`, `ORANGE`, `RED`).
6. **`IntegrationStatus`** enum (`UNKNOWN`, `CONFIGURED`, `READY`, `CONNECTED`, `DEGRADED`, `DISCONNECTED`, `FAILED`, `DISABLED`) for runtime health distinct from lifecycle existence.
7. **`IntegrationLifecycleState`** state machine (`REGISTERED` ➔ `INITIALIZING` ➔ `CONNECTED` ➔ `HEALTHY` ➔ `DEGRADED` ➔ `RECONNECTING` ➔ `FAILED`) preventing ambiguous runtime state transitions.
8. **Pluggable Retry Policies** (`NoRetry`, `LinearBackoff`, `ExponentialBackoff`, `CircuitBreaker`).
9. **`PluginManifest`** specifying adapter id, version, api_version, runtime_version, author, license, dependencies, and configuration_schema.
10. **Reserved Extension Directories** (`extensions/`, `plugins/`, `reference/`, `samples/`).

---

## 9 Production Adapter Categories

| Category | Stable IDs | Reference Implementation | Extension Placeholders |
| :--- | :--- | :--- | :--- |
| **Storage** | `storage.filesystem`, `storage.s3` | `FilesystemStorageAdapter`, `FilesystemSandboxAdapter` | S3, Azure Blob, GCS |
| **Vector DB** | `vector.inmemory`, `vector.pinecone` | `InMemoryVectorAdapter` | Pinecone, Qdrant, FAISS |
| **LLM** | `llm.gemini`, `llm.openai` | `GeminiLLMAdapter` | OpenAI, Anthropic, Ollama |
| **Auth** | `auth.jwt`, `auth.oauth2` | `JWTAuthAdapter` | OAuth2, Auth0, Keycloak |
| **Database** | `database.postgres`, `database.redis` | `PostgresDatabaseAdapter`, `RedisDatabaseAdapter` | MySQL, SQLite |
| **Observability** | `observability.prometheus`, `observability.opentelemetry` | `PrometheusObservabilityAdapter` | OTEL, Sentry, Grafana |
| **Messaging** | `messaging.webhook`, `messaging.kafka` | `WebhookMessagingAdapter` | Kafka, RabbitMQ |
| **Search** | `search.elasticsearch` | `ElasticsearchSearchAdapter` | Typesense, MeiliSearch |
| **Scheduler** | `scheduler.cron`, `scheduler.apscheduler` | `CronSchedulerAdapter` | APScheduler, Celery |

---

## Consequences

- All production vendor SDKs remain isolated to `backend/app/integrations/adapters/`. No SDK imports in frozen runtime layers.
- Automatic priority failover enabled via `IntegrationRegistry.resolve_active_provider(capability)`.
- Adapter health aggregation visible via `GET /api/v1/integrations/health`.
- All secret credentials managed by `SecretProvider` — never hardcoded.
