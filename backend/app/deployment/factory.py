"""Deployment factory — creates standard deployment configurations."""

from __future__ import annotations

from app.deployment.backup import BackupManager, BackupPlan, BackupType
from app.deployment.environment import EnvironmentManager, EnvironmentType
from app.deployment.recovery import RecoveryManager, RecoveryPlan
from app.deployment.release import ReleaseManager, ReleaseManifest
from app.deployment.rollback import RollbackManager
from app.deployment.scaling import (
    AutoScalingPolicy,
    HorizontalScaling,
    ReplicaPolicy,
    ResourceLimits,
    VerticalScaling,
)
from app.deployment.strategy import DeploymentStrategyConfig, RollingDeployment
from app.deployment.validator import DeploymentValidator


class DeploymentFactory:
    """Factory for creating pre-configured deployment subsystems."""

    @staticmethod
    def create_default_strategy() -> RollingDeployment:
        return RollingDeployment(
            config=DeploymentStrategyConfig(max_surge=1, max_unavailable=0)
        )

    @staticmethod
    def create_default_scaler() -> HorizontalScaling:
        return HorizontalScaling(
            policy=ReplicaPolicy(min_replicas=1, max_replicas=10, desired_replicas=2),
            auto_policy=AutoScalingPolicy(
                cpu_threshold_pct=70.0, memory_threshold_pct=80.0
            ),
        )

    @staticmethod
    def create_default_vertical_scaler() -> VerticalScaling:
        return VerticalScaling(limits=ResourceLimits())

    @staticmethod
    def create_default_release_manager() -> ReleaseManager:
        rm = ReleaseManager()
        rm.register_release(
            ReleaseManifest(
                version="7.8.0",
                release_name="VOLTA Enterprise Platform v7.8.0",
            )
        )
        rm.promote("7.8.0")
        return rm

    @staticmethod
    def create_default_backup_manager() -> BackupManager:
        bm = BackupManager()
        bm.register_plan(
            BackupPlan(
                plan_id="daily_full",
                name="Daily Full Backup",
                backup_type=BackupType.FULL,
                schedule_cron="0 2 * * *",
            )
        )
        bm.register_plan(
            BackupPlan(
                plan_id="hourly_incremental",
                name="Hourly Incremental Backup",
                backup_type=BackupType.INCREMENTAL,
                schedule_cron="0 * * * *",
            )
        )
        return bm

    @staticmethod
    def create_default_recovery_manager() -> RecoveryManager:
        rm = RecoveryManager()
        rm.register_plan(
            RecoveryPlan(
                plan_id="primary_dr",
                name="Primary Disaster Recovery Plan",
                rpo_minutes=60,
                rto_minutes=30,
            )
        )
        return rm

    @staticmethod
    def create_validator() -> DeploymentValidator:
        return DeploymentValidator()

    @staticmethod
    def create_environment_manager() -> EnvironmentManager:
        em = EnvironmentManager()
        em.activate(EnvironmentType.PRODUCTION)
        return em

    @staticmethod
    def create_rollback_manager() -> RollbackManager:
        return RollbackManager()
