"""Deployment Manager — central orchestration entry point for Phase 7.8.

Coordinates:
- Validation
- Deployment execution
- Rollback
- Scaling
- Release management
- Environment management
- Backup
- Disaster recovery
- Health monitoring
- Analytics
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Optional

from app.deployment.analytics import DeploymentAnalyticsEngine
from app.deployment.backup import BackupManager
from app.deployment.config import DeploymentConfig
from app.deployment.contracts import (
    DeploymentDeployPayload,
    DeploymentRollbackPayload,
    DeploymentScalePayload,
    DeploymentStatusResponse,
    DeploymentValidatePayload,
)
from app.deployment.deployment import Deployment, DeploymentStatus
from app.deployment.environment import EnvironmentManager
from app.deployment.events import DeploymentEvent, DeploymentEventBus
from app.deployment.factory import DeploymentFactory
from app.deployment.health import DeploymentHealthLevel, DeploymentHealthManager, PlatformHealthSummary
from app.deployment.hooks import DeploymentHooks
from app.deployment.lifecycle import DeploymentLifecycleManager, DeploymentLifecycleState
from app.deployment.metrics import DeploymentMetricsCollector
from app.deployment.recovery import RecoveryManager
from app.deployment.registry import DeploymentRegistry
from app.deployment.release import ReleaseManager
from app.deployment.rollback import RollbackManager, RollbackSnapshot
from app.deployment.scaling import HorizontalScaling, ScalingEvent
from app.deployment.statistics import DeploymentStatistics
from app.deployment.strategy import DeploymentStrategy, create_strategy, DeploymentStrategyType
from app.deployment.validator import DeploymentValidationReport, DeploymentValidator

logger = logging.getLogger("app.deployment.manager")


class DeploymentManager:
    """Central orchestration entry point for the Enterprise Deployment Platform.

    This is the only component that orchestrates all deployment subsystems.
    All REST API endpoints and external callers MUST use this manager exclusively.
    """

    def __init__(
        self,
        config: Optional[DeploymentConfig] = None,
    ) -> None:
        self.config = config or DeploymentConfig()
        self.registry = DeploymentRegistry()
        self.validator = DeploymentFactory.create_validator()
        self.release_manager = DeploymentFactory.create_default_release_manager()
        self.environment_manager = DeploymentFactory.create_environment_manager()
        self.rollback_manager = DeploymentFactory.create_rollback_manager()
        self.backup_manager = DeploymentFactory.create_default_backup_manager()
        self.recovery_manager = DeploymentFactory.create_default_recovery_manager()
        self.health_manager = DeploymentHealthManager()
        self.scaler = DeploymentFactory.create_default_scaler()
        self.metrics_collector = DeploymentMetricsCollector()
        self.analytics_engine = DeploymentAnalyticsEngine()
        self.statistics = DeploymentStatistics()
        self.event_bus = DeploymentEventBus()
        self.hooks = DeploymentHooks()

        # Seed default deployment record
        self._seed_default_deployment()

    def _seed_default_deployment(self) -> None:
        d = Deployment(
            deployment_id="volta-platform-v7.8",
            platform_version="7.8.0",
            environment="production",
            strategy="rolling",
            status=DeploymentStatus.ACTIVE,
            replica_count=2,
            image_tag="7.8.0",
        )
        self.registry.register(d)

    # -------------------------------------------------------------------------
    # Validation
    # -------------------------------------------------------------------------

    async def validate(self, payload: DeploymentValidatePayload) -> DeploymentValidationReport:
        """Validate a deployment before executing."""
        logger.info("Validating deployment '%s'", payload.deployment_id)
        report = self.validator.validate(payload.deployment_id)
        self.statistics.validations_run += 1
        if report.all_passed:
            self.statistics.validations_passed += 1
        self.event_bus.emit(DeploymentEvent(
            event_type="validation_completed",
            deployment_id=payload.deployment_id,
            payload={"all_passed": report.all_passed},
        ))
        return report

    # -------------------------------------------------------------------------
    # Deploy
    # -------------------------------------------------------------------------

    async def deploy(self, payload: DeploymentDeployPayload) -> Deployment:
        """Execute a deployment using the specified strategy."""
        logger.info("Deploying '%s' with strategy '%s'", payload.deployment_id, payload.strategy)

        # Validate first
        validation = self.validator.validate(payload.deployment_id)
        if not validation.all_passed:
            raise ValueError(f"Deployment validation failed for '{payload.deployment_id}'")

        # Create deployment record
        deployment = Deployment(
            deployment_id=payload.deployment_id,
            environment=payload.environment,
            strategy=payload.strategy,
            image_tag=payload.image_tag,
            status=DeploymentStatus.ACTIVE,
            replica_count=payload.replica_count,
        )
        lifecycle = DeploymentLifecycleManager()
        lifecycle.transition(DeploymentLifecycleState.VALIDATED)
        lifecycle.transition(DeploymentLifecycleState.BUILDING)
        lifecycle.transition(DeploymentLifecycleState.DEPLOYING)
        lifecycle.transition(DeploymentLifecycleState.VERIFYING)
        lifecycle.transition(DeploymentLifecycleState.RUNNING)

        self.registry.register(deployment)
        self.statistics.total_deployments += 1
        self.statistics.successful_deployments += 1

        # Capture rollback snapshot
        snap = RollbackSnapshot(
            snapshot_id=f"snap_{deployment.deployment_id}_{uuid.uuid4().hex[:8]}",
            deployment_id=deployment.deployment_id,
            version=self.config.platform_version,
            environment=deployment.environment,
            replica_count=deployment.replica_count,
            image_tag=deployment.image_tag,
        )
        self.rollback_manager.capture_snapshot(snap)

        self.event_bus.emit(DeploymentEvent(
            event_type="deploy_completed",
            deployment_id=deployment.deployment_id,
            payload={"strategy": payload.strategy, "image_tag": payload.image_tag},
        ))
        return deployment

    # -------------------------------------------------------------------------
    # Rollback
    # -------------------------------------------------------------------------

    async def rollback(self, payload: DeploymentRollbackPayload) -> dict[str, Any]:
        """Execute a rollback to a previous snapshot."""
        rollback_id = f"rb_{uuid.uuid4().hex[:8]}"
        plan = self.rollback_manager.build_plan(
            deployment_id=payload.deployment_id,
            snapshot_id=payload.snapshot_id,
            rollback_id=rollback_id,
        )
        if not plan:
            raise ValueError(f"Snapshot '{payload.snapshot_id}' not found.")
        result = await self.rollback_manager.execute_rollback(rollback_id)
        self.statistics.rollbacks_triggered += 1
        self.registry.update_status(payload.deployment_id, DeploymentStatus.ROLLEDBACK)
        self.event_bus.emit(DeploymentEvent(
            event_type="rollback_completed",
            deployment_id=payload.deployment_id,
            payload=result,
        ))
        return result

    # -------------------------------------------------------------------------
    # Scaling
    # -------------------------------------------------------------------------

    async def scale(self, payload: DeploymentScalePayload) -> ScalingEvent:
        """Scale a deployment horizontally."""
        d = self.registry.get(payload.deployment_id)
        current = d.replica_count if d else 1
        event = await self.scaler.scale(
            deployment_id=payload.deployment_id,
            current=current,
            target=payload.target_replicas,
        )
        if d:
            d.replica_count = payload.target_replicas
        self.statistics.scaling_events += 1
        self.event_bus.emit(DeploymentEvent(
            event_type="scale_completed",
            deployment_id=payload.deployment_id,
            payload={"from": current, "to": payload.target_replicas, "reason": payload.reason},
        ))
        return event

    # -------------------------------------------------------------------------
    # Health
    # -------------------------------------------------------------------------

    async def get_platform_health(self) -> PlatformHealthSummary:
        """Return aggregated platform health."""
        return await self.health_manager.check_platform_health()

    async def get_deployment_status(self, deployment_id: str) -> DeploymentStatusResponse:
        """Return deployment status DTO."""
        d = self.registry.get(deployment_id)
        health = await self.health_manager.check_deployment_health(deployment_id)
        return DeploymentStatusResponse(
            deployment_id=deployment_id,
            status=d.status.value if d else DeploymentStatus.UNKNOWN.value,
            lifecycle_state=DeploymentLifecycleState.RUNNING.value,
            environment=d.environment if d else "unknown",
            replica_count=d.replica_count if d else 0,
            ready_replicas=d.replica_count if d else 0,
            health_level=health.health_level.value,
            platform_version=self.config.platform_version,
        )

    # -------------------------------------------------------------------------
    # Statistics / Analytics
    # -------------------------------------------------------------------------

    def get_statistics(self) -> DeploymentStatistics:
        return self.statistics

    def get_analytics(self) -> dict[str, Any]:
        analytics = self.analytics_engine.compute(
            total_deployments=self.statistics.total_deployments,
            failed_deployments=self.statistics.failed_deployments,
            rollbacks=self.statistics.rollbacks_triggered,
        )
        from dataclasses import asdict
        return asdict(analytics)
