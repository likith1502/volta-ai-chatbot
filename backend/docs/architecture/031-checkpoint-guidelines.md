# 031: Checkpoint & Replay Engineering Guidelines

## 1. Checkpoint Philosophy & Immutability

1. **Strict Immutability**: `Checkpoint` objects are strictly read-only (`frozen=True`). Once saved, a checkpoint MUST NOT be modified in-place.
2. **Lineage Preservation**: Every checkpoint receives a unique UUID `checkpoint_id`. Overwriting existing checkpoint IDs is strictly prohibited.
3. **Storage Isolation**: The checkpoint foundation maintains pure storage independence (`InMemoryCheckpointStore`). Do NOT introduce Redis or database imports into the core checkpoint module.

---

## 2. Replay Philosophy & Recovery Rules

1. **State Protection**: Replaying a workflow MUST NOT mutate original `ConversationState` snapshots. Replay creates a new execution context and produces a new state lineage.
2. **Version Compatibility**: Checkpoints must be validated against `CheckpointVersion` before restoration. If version compatibility fails, restoration MUST be rejected.
3. **Structured Audit History**: All replay operations (start, step, resume, restart, cancel) MUST be logged in `ReplayHistory` using `ReplayAction` enum values.

---

## 3. Naming & Enum Conventions

- **Checkpoint Status**: Lowercase string enums in `CheckpointStatus` (`created`, `active`, `archived`, `expired`, `corrupted`, `restored`).
- **Replay Modes**: Lowercase string enums in `ReplayMode` (`full`, `step`, `resume`, `simulation`, `debug`).
- **Replay Actions**: Lowercase string enums in `ReplayAction` (`start`, `step_forward`, `step_backward`, `resume`, `restart`, `finish`, `cancel`).

---

## 4. Extension Model

- To introduce persistent storage backends (e.g. Redis, SQL) in future phases, implement the `CheckpointStore` abstract interface (`save`, `load`, `delete`, `exists`, `list`, `clear`) and register via `CheckpointRegistry`.
