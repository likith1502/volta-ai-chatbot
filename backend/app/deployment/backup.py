"""Backup Manager — backup plans, snapshots, restore points."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class BackupStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class BackupType(str, Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"


@dataclass
class BackupPlan:
    """Configuration for a recurring backup schedule."""

    plan_id: str
    name: str
    backup_type: BackupType = BackupType.FULL
    schedule_cron: str = "0 2 * * *"  # Daily at 02:00
    retention_days: int = 30
    targets: list[str] = field(
        default_factory=lambda: [
            "database",
            "vector_store",
            "memory_cache",
            "config",
            "secrets_metadata",
        ]
    )
    compression: bool = True
    encryption: bool = True
    enabled: bool = True


@dataclass
class BackupSnapshot:
    """A completed backup snapshot."""

    snapshot_id: str
    plan_id: str
    backup_type: BackupType
    status: BackupStatus
    size_bytes: int = 0
    targets_backed_up: list[str] = field(default_factory=list)
    checksum: str = ""
    created_at: float = 1786088000.0
    expires_at: float = 1786088000.0 + 86400 * 30
    storage_location: str = "/backups/"
    metadata: dict[str, Any] = field(default_factory=dict)


class BackupManager:
    """Manages backup plans, execution, and snapshot history."""

    def __init__(self) -> None:
        self._plans: dict[str, BackupPlan] = {}
        self._snapshots: dict[str, BackupSnapshot] = {}

    def register_plan(self, plan: BackupPlan) -> None:
        self._plans[plan.plan_id] = plan

    async def execute_backup(self, plan_id: str) -> BackupSnapshot:
        """Execute a backup and return the resulting snapshot."""
        plan = self._plans.get(plan_id)
        if not plan:
            raise ValueError(f"Backup plan '{plan_id}' not found.")
        snapshot = BackupSnapshot(
            snapshot_id=f"snap_{plan_id}_{len(self._snapshots)}",
            plan_id=plan_id,
            backup_type=plan.backup_type,
            status=BackupStatus.COMPLETED,
            size_bytes=1024 * 1024 * 50,  # 50MB mock
            targets_backed_up=plan.targets,
            checksum="sha256:abc123",
            storage_location=f"/backups/{plan_id}/",
        )
        self._snapshots[snapshot.snapshot_id] = snapshot
        return snapshot

    def get_snapshot(self, snapshot_id: str) -> Optional[BackupSnapshot]:
        return self._snapshots.get(snapshot_id)

    def list_plans(self) -> list[BackupPlan]:
        return list(self._plans.values())

    def list_snapshots(self, plan_id: Optional[str] = None) -> list[BackupSnapshot]:
        snaps = list(self._snapshots.values())
        if plan_id:
            snaps = [s for s in snaps if s.plan_id == plan_id]
        return snaps

    def get_latest_snapshot(self, plan_id: str) -> Optional[BackupSnapshot]:
        snaps = self.list_snapshots(plan_id)
        if not snaps:
            return None
        return sorted(snaps, key=lambda s: s.created_at, reverse=True)[0]
