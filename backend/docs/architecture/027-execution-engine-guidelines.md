# 027: Graph Execution Engine Guidelines

## 1. Execution & Traversal Rules

1. **Pre-Execution Validation**: Never bypass `graph.validate()`. If validation fails, abort immediately by raising `ExecutionValidationException`.
2. **Traversal Semantics**: Entry node is determined strictly by `graph.entry_node`. Traversal proceeds by selecting outgoing edges sorted by priority.
3. **Terminal Node Detection**: If a node has no outgoing edges, or if no outgoing edge condition evaluates to `True`, traversal terminates gracefully.

---

## 2. Depth & Loop Protection

- Graph depth must be tracked incrementally (`context.current_depth`).
- If `current_depth > policy.max_depth`, traversal must abort immediately by raising `ExecutionValidationException`.
- Cyclic graphs are permitted ONLY if `policy.allow_cycles` is explicitly set to `True` AND `current_depth <= policy.max_depth`.

---

## 3. Node Dispatching & Lifecycle

Every node executed by the dispatcher MUST follow the lifecycle chain:
1. `before_execute(state, context)`
2. `execute(state, context)`
3. `after_execute(state, context)`
4. `on_error(state, error, context)` (if any stage raises an exception)

---

## 4. State Ownership & Immutability

- `ConversationState` snapshots are passed immutably down the execution pipeline.
- The execution engine MUST NOT mutate previous state snapshots in-place.
- Each node step produces a new `ExecutionSnapshot` containing the current state snapshot.

---

## 5. Error Handling & Strategy Policy

- If a node raises an exception and `policy.stop_on_error` is `True`, execution halts, `ExecutionMetrics.failed_nodes` records the failure, and `ExecutionStatus.FAILED` is set.
- If `policy.stop_on_error` is `False`, execution records the failure and attempts to proceed along valid outgoing edges.

---

## 6. Performance Considerations

- Node lifecycle calls and edge predicate evaluations MUST be fully asynchronous (`async`/`await`).
- Telemetry event object creation MUST be non-blocking.
