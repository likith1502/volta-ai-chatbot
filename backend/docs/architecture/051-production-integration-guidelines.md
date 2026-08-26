# ADR 051: Enterprise Production Integration Guidelines

> **VOLTA Urban Mobility AI Platform**
> **Status**: Accepted | **Date**: 2026-08-07 | **Phase**: v7.7.0

---

## Guidelines

### 1. Stable Adapter IDs
All adapters must use stable, immutable dot-notation IDs of the form `{category}.{name}`. Class name or package path must never determine adapter identity.

```
storage.filesystem    vector.inmemory    llm.gemini    auth.jwt
```

### 2. Reference vs Extension Distinction

| Type | Description | Production Ready |
| :--- | :--- | :---: |
| Reference Implementation | Fully functional lightweight adapter shipped with the platform | ✅ |
| Extension Placeholder | Subclasses with minimal mock overrides reserving extension points | 🔲 |

### 3. Secret Resolution
All adapter credentials must flow through `SecretProvider.get_secret(key)`. Direct `os.environ` reads inside adapters are forbidden.

### 4. Health Reports
Every `IntegrationProvider` must implement `check_health()` returning `IntegrationHealthReport` with `health_level`, `latency_ms`, `error_rate`, `uptime_pct`.

### 5. Lifecycle State Machine
Lifecycle transitions must follow the legal state machine defined in `IntegrationLifecycleManager`. Invalid transitions must return `False` and log a warning.

### 6. Adapter Priority & Failover
Adapters within the same category must expose `priority`. `IntegrationRegistry.resolve_active_provider(category)` always selects the highest-priority connected provider automatically.

### 7. Offline Testing
All automated tests must be fully offline. No live cloud calls in `pytest`. Real provider verification belongs in optional manual integration tests.

### 8. Plugin Manifests
Every new adapter must ship a `PluginManifest` declaring `id`, `name`, `version`, `api_version`, `runtime_version`, `category`, `author`, `depends_on`, and `conflicts_with`.
