# 035: Human-in-the-Loop (HITL) Engineering Guidelines

## 1. Approval Philosophy & Immutability

1. **Strict Immutability**: `ApprovalRequest` objects are frozen (`frozen=True`). Once instantiated, approval requests MUST NOT be modified in-place.
2. **State Transition Integrity**: Approval requests transition strictly through valid states (`CREATED` -> `ASSIGNED` -> `WAITING` -> `APPROVED` / `REJECTED` -> `COMPLETED`).
3. **Audit History**: All decision actions (approve, reject, escalate, cancel) MUST log a record in `ApprovalHistory` via `ApprovalDecision` and `HumanRole` enums.

---

## 2. Governance Principles & Duty Separation

1. **Separation of Duties**: Requester and reviewer identities MUST be distinct when `separation_of_duties=True` in `GovernancePolicy`. Self-approval is rejected.
2. **Manager Separation**: `ApprovalManager` governs approval request lifecycle and decisions; `ResumeManager` governs execution resumption from checkpoints; `InterruptManager` governs interruption signaling.

---

## 3. Naming & Enum Conventions

- **Approval Status**: Lowercase string enums in `ApprovalStatus` (`created`, `pending`, `assigned`, `waiting`, `approved`, `rejected`, `cancelled`, `expired`, `escalated`, `completed`).
- **Approval Decision**: Lowercase string enums in `ApprovalDecision` (`approve`, `reject`, `request_changes`, `escalate`, `cancel`, `defer`, `none`).
- **Human Roles**: Lowercase string enums in `HumanRole` (`reviewer`, `approver`, `admin`, `auditor`, `observer`, `operator`, `system`).

---

## 4. Extension Guidelines

- To integrate notification services or approval UI dashboards in future runtime phases, subscribe to `ApprovalEvent` DTOs or extend `ApprovalRegistry` handlers without modifying core HITL domain models.
