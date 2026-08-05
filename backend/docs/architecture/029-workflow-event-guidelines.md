# 029: Workflow Event Engineering Guidelines

## 1. Naming Conventions

- **Event Types**: Lower snake_case enum values in `WorkflowEventType` (e.g. `execution_started`, `node_completed`).
- **Event Categories**: Upper snake_case enum values in `WorkflowEventCategory` (`EXECUTION`, `NODE`, `GRAPH`, `STATE`, `CHECKPOINT`, `SYSTEM`, `SECURITY`, `CUSTOM`).
- **Listener Classes**: PascalCase ending with `Listener` (e.g., `TelemetryLoggingListener`, `MetricsCollectionListener`).

---

## 2. Listener Conventions (Observer-Only Rule)

1. Listeners MUST be completely read-only observers.
2. Listeners MUST NOT mutate `ConversationState`.
3. Listeners MUST NOT alter graph execution flow or control logic.
4. Listeners MUST NOT call external AI providers or make database writes directly.

---

## 3. Delivery & Error Isolation

- All listener invocations inside `WorkflowEventDispatcher` are wrapped in exception handlers.
- If a listener raises an exception in `on_event()`, `on_error()` is called, and the error is recorded in `WorkflowEventResult.errors`.
- An error in one listener MUST NOT prevent other subscribed listeners from receiving the event.

---

## 4. Priority Rules

Listeners and subscriptions execute in descending priority order:
1. `CRITICAL` (Weight: 4)
2. `HIGH` (Weight: 3)
3. `NORMAL` (Weight: 2)
4. `LOW` (Weight: 1)

---

## 5. Serialization Contracts

- Event domain objects remain format-agnostic.
- Use `EventEnvelope` and `WorkflowEventSerializer` (`JSONEventSerializer`, `MessagePackEventSerializer`, `ProtobufEventSerializer`) when converting events for external transport boundaries.
