"""Rollback Manager — rollback plans, snapshots, and restore points."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class RollbackSnapshot:
    """A point-in-time snapshot of a running deployment."""
    snapshot_id: str
    deployment_id: str
    version: str
    environment: str
    replica_count: int
    image_tag: str
    config_snapshot: dict[str, Any] = field(default_factory=dict)
    created_at: float = 1786088000.0


@dataclass
class RestorePoint:
    """A restore point derived from a rollback snapshot."""
    restore_id: str
    snapshot_id: str
    version: str
    restorable: bool = True
    estimated_restore_seconds: int = 30


@dataclass
class RollbackPlan:
    """Full plan for a deployment rollback."""
    rollback_id: str
    from_deployment_id: str
    to_snapshot_id: str
    target_version: str
    strategy: str = "rolling"
    estimated_duration_seconds: int = 30
    steps: list[str] = field(default_factory=list)


class RollbackManager:
    """Manages rollback plans, snapshots, and restore operations."""

    def __init__(self) -> None:
        self._snapshots: dict[str, RollbackSnapshot] = {}
        self._restore_points: dict[str, RestorePoint] = {}
        self._plans: dict[str, RollbackPlan] = {}
        self._rollback_history: list[str] = []

    def capture_snapshot(self, snapshot: RollbackSnapshot) -> str:
        """Capture and store a deployment snapshot."""
        self._snapshots[snapshot.snapshot_id] = snapshot
        rp = RestorePoint(
            restore_id=f"rp_{snapshot.snapshot_id}",
            snapshot_id=snapshot.snapshot_id,
            version=snapshot.version,
        )
        self._restore_points[rp.restore_id] = rp
        return snapshot.snapshot_id

    def build_plan(self, deployment_id: str, snapshot_id: str, rollback_id: str) -> Optional[RollbackPlan]:
        """Build a rollback plan for a given deployment → snapshot pair."""
        snap = self._snapshots.get(snapshot_id)
        if not snap:
            return None
        plan = RollbackPlan(
            rollback_id=rollback_id,
            from_deployment_id=deployment_id,
            to_snapshot_id=snapshot_id,
            target_version=snap.version,
            steps=[
                "pause_traffic",
                f"restore_snapshot:{snapshot_id}",
                "verify_health",
                "shift_traffic",
            ],
        )
        self._plans[rollback_id] = plan
        return plan

    async def execute_rollback(self, rollback_id: str) -> dict[str, Any]:
        """Execute the rollback plan and return a summary."""
        plan = self._plans.get(rollback_id)
        if not plan:
            raise ValueError(f"Rollback plan '{rollback_id}' not found.")
        self._rollback_history.append(rollback_id)
        return {
            "rollback_id": rollback_id,
            "target_version": plan.target_version,
            "steps_executed": plan.steps,
            "success": True,
        }

    def list_snapshots(self) -> list[RollbackSnapshot]:
        return list(self._snapshots.values())

    def list_plans(self) -> list[RollbackPlan]:
        return list(self._plans.values())

    @property
    def rollback_history(self) -> list[str]:
        return list(self._rollback_history)
