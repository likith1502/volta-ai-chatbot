"""Phase 7.8 — Deployment Package Tests.

Tests: deployment models, lifecycle, strategies, rollback, scaling,
environment, validator, health, backup, recovery, release manager.
"""

import pytest
from app.deployment.deployment import Deployment, DeploymentStatus
from app.deployment.lifecycle import DeploymentLifecycleManager, DeploymentLifecycleState
from app.deployment.strategy import (
    BlueGreenDeployment, CanaryDeployment, RecreateDeployment, RollingDeployment,
    DeploymentStrategyConfig, DeploymentStrategyType, create_strategy,
)
from app.deployment.rollback import RollbackManager, RollbackSnapshot, RollbackPlan
from app.deployment.scaling import (
    AutoScalingPolicy, HorizontalScaling, ReplicaPolicy, ResourceLimits,
    ScalingDirection, VerticalScaling,
)
from app.deployment.environment import Environment, EnvironmentManager, EnvironmentType, EnvironmentConfig
from app.deployment.validator import DeploymentValidator
from app.deployment.health import DeploymentHealthLevel, DeploymentHealthManager, DeploymentHealthReport
from app.deployment.backup import BackupManager, BackupPlan, BackupType, BackupStatus
from app.deployment.recovery import RecoveryManager, RecoveryPlan, RecoveryTrigger
from app.deployment.release import ReleaseManager, ReleaseManifest
from app.deployment.versioning import SemVer
from app.deployment.registry import DeploymentRegistry
from app.deployment.config import DeploymentConfig
from app.deployment.context import DeploymentContext
from app.deployment.capabilities import DeploymentCapabilities
from app.deployment.policy import DeploymentPolicy
from app.deployment.serializer import DeploymentSerializer
from app.deployment.statistics import DeploymentStatistics, DeploymentMetrics, DeploymentAnalytics
from app.deployment.analytics import DeploymentAnalyticsEngine
from app.deployment.metrics import DeploymentMetricsCollector
from app.deployment.events import DeploymentEvent, DeploymentEventBus
from app.deployment.hooks import DeploymentHooks, DeploymentHookResult
from app.deployment.exceptions import (
    DeploymentError, DeploymentValidationError, RollbackError,
    ScalingError, BackupError, RecoveryError, ReleaseCompatibilityError,
    EnvironmentNotFoundError, DeploymentStrategyError,
)
from app.deployment.contracts import (
    DeploymentValidatePayload, DeploymentDeployPayload, DeploymentRollbackPayload,
    DeploymentScalePayload,
)


# ===========================================================================
# Deployment Model
# ===========================================================================

class TestDeploymentModel:
    def test_deployment_default_status(self):
        d = Deployment(deployment_id="d1")
        assert d.status == DeploymentStatus.UNKNOWN

    def test_deployment_fields(self):
        d = Deployment(deployment_id="d2", environment="staging", strategy="canary", replica_count=3)
        assert d.environment == "staging"
        assert d.strategy == "canary"
        assert d.replica_count == 3

    def test_deployment_status_enum_values(self):
        assert DeploymentStatus.ACTIVE.value == "active"
        assert DeploymentStatus.FAILED.value == "failed"
        assert DeploymentStatus.TERMINATED.value == "terminated"
        assert DeploymentStatus.ROLLEDBACK.value == "rolledback"


# ===========================================================================
# Lifecycle State Machine
# ===========================================================================

class TestDeploymentLifecycle:
    def test_initial_state_is_created(self):
        lc = DeploymentLifecycleManager()
        assert lc.state == DeploymentLifecycleState.CREATED

    def test_legal_transition_created_to_validated(self):
        lc = DeploymentLifecycleManager()
        assert lc.transition(DeploymentLifecycleState.VALIDATED)
        assert lc.state == DeploymentLifecycleState.VALIDATED

    def test_full_legal_path(self):
        lc = DeploymentLifecycleManager()
        states = [
            DeploymentLifecycleState.VALIDATED,
            DeploymentLifecycleState.BUILDING,
            DeploymentLifecycleState.DEPLOYING,
            DeploymentLifecycleState.VERIFYING,
            DeploymentLifecycleState.RUNNING,
        ]
        for s in states:
            assert lc.transition(s), f"Failed transition to {s}"
        assert lc.state == DeploymentLifecycleState.RUNNING

    def test_illegal_transition_returns_false(self):
        lc = DeploymentLifecycleManager()
        assert not lc.transition(DeploymentLifecycleState.RUNNING)

    def test_rollback_from_running(self):
        lc = DeploymentLifecycleManager()
        for s in [DeploymentLifecycleState.VALIDATED, DeploymentLifecycleState.BUILDING,
                  DeploymentLifecycleState.DEPLOYING, DeploymentLifecycleState.VERIFYING,
                  DeploymentLifecycleState.RUNNING]:
            lc.transition(s)
        assert lc.transition(DeploymentLifecycleState.ROLLING_BACK)

    def test_terminated_is_final(self):
        lc = DeploymentLifecycleManager()
        lc.transition(DeploymentLifecycleState.FAILED)
        lc.transition(DeploymentLifecycleState.TERMINATED)
        assert not lc.transition(DeploymentLifecycleState.CREATED)

    def test_history_is_tracked(self):
        lc = DeploymentLifecycleManager()
        lc.transition(DeploymentLifecycleState.VALIDATED)
        assert len(lc.history) == 2

    def test_can_transition_method(self):
        lc = DeploymentLifecycleManager()
        assert lc.can_transition(DeploymentLifecycleState.VALIDATED)
        assert not lc.can_transition(DeploymentLifecycleState.RUNNING)

    def test_scaling_from_running(self):
        lc = DeploymentLifecycleManager()
        for s in [DeploymentLifecycleState.VALIDATED, DeploymentLifecycleState.BUILDING,
                  DeploymentLifecycleState.DEPLOYING, DeploymentLifecycleState.VERIFYING,
                  DeploymentLifecycleState.RUNNING]:
            lc.transition(s)
        assert lc.transition(DeploymentLifecycleState.SCALING)


# ===========================================================================
# Deployment Strategies
# ===========================================================================

class TestDeploymentStrategies:
    @pytest.mark.asyncio
    async def test_rolling_deploy(self):
        strategy = RollingDeployment()
        result = await strategy.execute("d1", 2, "7.8.0")
        assert result["strategy"] == "rolling"
        assert result["replicas"] == 2

    @pytest.mark.asyncio
    async def test_blue_green_deploy(self):
        strategy = BlueGreenDeployment()
        result = await strategy.execute("d2", 2, "7.8.0")
        assert result["strategy"] == "blue_green"
        assert result["traffic_shifted"] is True

    @pytest.mark.asyncio
    async def test_canary_deploy(self):
        strategy = CanaryDeployment()
        result = await strategy.execute("d3", 2, "7.8.0")
        assert result["strategy"] == "canary"
        assert result["promoted"] is True

    @pytest.mark.asyncio
    async def test_recreate_deploy(self):
        strategy = RecreateDeployment()
        result = await strategy.execute("d4", 1, "7.8.0")
        assert result["strategy"] == "recreate"
        assert result["deployed_new"] is True

    @pytest.mark.asyncio
    async def test_all_strategies_rollback(self):
        for cls in [RollingDeployment, BlueGreenDeployment, CanaryDeployment, RecreateDeployment]:
            strategy = cls()
            assert await strategy.rollback("d5") is True

    def test_strategy_factory_rolling(self):
        s = create_strategy(DeploymentStrategyType.ROLLING)
        assert isinstance(s, RollingDeployment)

    def test_strategy_factory_blue_green(self):
        s = create_strategy(DeploymentStrategyType.BLUE_GREEN)
        assert isinstance(s, BlueGreenDeployment)

    def test_strategy_factory_canary(self):
        s = create_strategy(DeploymentStrategyType.CANARY)
        assert isinstance(s, CanaryDeployment)

    def test_strategy_factory_recreate(self):
        s = create_strategy(DeploymentStrategyType.RECREATE)
        assert isinstance(s, RecreateDeployment)

    def test_strategy_factory_unknown_raises(self):
        with pytest.raises(ValueError):
            create_strategy("unknown_strategy")  # type: ignore

    def test_strategy_describe(self):
        s = RollingDeployment()
        desc = s.describe()
        assert desc["type"] == "rolling"


# ===========================================================================
# Rollback Manager
# ===========================================================================

class TestRollbackManager:
    def test_capture_snapshot(self):
        rm = RollbackManager()
        snap = RollbackSnapshot(
            snapshot_id="snap1", deployment_id="d1", version="7.7.0",
            environment="prod", replica_count=2, image_tag="7.7.0",
        )
        sid = rm.capture_snapshot(snap)
        assert sid == "snap1"
        assert len(rm.list_snapshots()) == 1

    def test_build_plan(self):
        rm = RollbackManager()
        snap = RollbackSnapshot(
            snapshot_id="snap2", deployment_id="d2", version="7.6.0",
            environment="prod", replica_count=2, image_tag="7.6.0",
        )
        rm.capture_snapshot(snap)
        plan = rm.build_plan("d2", "snap2", "rb1")
        assert plan is not None
        assert plan.rollback_id == "rb1"
        assert plan.target_version == "7.6.0"

    def test_build_plan_missing_snapshot(self):
        rm = RollbackManager()
        plan = rm.build_plan("d3", "snap_missing", "rb_x")
        assert plan is None

    @pytest.mark.asyncio
    async def test_execute_rollback(self):
        rm = RollbackManager()
        snap = RollbackSnapshot(
            snapshot_id="snap3", deployment_id="d3", version="7.5.0",
            environment="prod", replica_count=1, image_tag="7.5.0",
        )
        rm.capture_snapshot(snap)
        rm.build_plan("d3", "snap3", "rb2")
        result = await rm.execute_rollback("rb2")
        assert result["success"] is True
        assert "7.5.0" in result["target_version"]

    @pytest.mark.asyncio
    async def test_execute_rollback_missing_plan(self):
        rm = RollbackManager()
        with pytest.raises(ValueError):
            await rm.execute_rollback("rb_nonexistent")

    def test_rollback_history(self):
        rm = RollbackManager()
        snap = RollbackSnapshot(
            snapshot_id="snap4", deployment_id="d4", version="7.4.0",
            environment="prod", replica_count=2, image_tag="7.4.0",
        )
        rm.capture_snapshot(snap)
        rm.build_plan("d4", "snap4", "rb3")
        import asyncio
        asyncio.run(rm.execute_rollback("rb3"))
        assert "rb3" in rm.rollback_history


# ===========================================================================
# Scaling Engine
# ===========================================================================

class TestScalingEngine:
    def test_resource_limits_defaults(self):
        rl = ResourceLimits()
        assert rl.cpu_request == "250m"
        assert rl.memory_request == "512Mi"

    def test_replica_policy_defaults(self):
        rp = ReplicaPolicy()
        assert rp.min_replicas == 1
        assert rp.max_replicas == 10

    def test_horizontal_compute_scale_up(self):
        hs = HorizontalScaling(
            policy=ReplicaPolicy(min_replicas=1, max_replicas=10, desired_replicas=2),
            auto_policy=AutoScalingPolicy(cpu_threshold_pct=70.0),
        )
        target = hs.compute_desired_replicas(2, cpu_pct=85.0, memory_pct=50.0)
        assert target == 3

    def test_horizontal_compute_scale_down(self):
        hs = HorizontalScaling(
            policy=ReplicaPolicy(min_replicas=1, max_replicas=10, desired_replicas=2),
            auto_policy=AutoScalingPolicy(cpu_threshold_pct=70.0),
        )
        target = hs.compute_desired_replicas(4, cpu_pct=20.0, memory_pct=20.0)
        assert target == 3

    def test_horizontal_no_scale(self):
        hs = HorizontalScaling(
            policy=ReplicaPolicy(min_replicas=1, max_replicas=10, desired_replicas=2),
            auto_policy=AutoScalingPolicy(cpu_threshold_pct=70.0),
        )
        target = hs.compute_desired_replicas(2, cpu_pct=50.0, memory_pct=60.0)
        assert target == 2

    @pytest.mark.asyncio
    async def test_horizontal_scale_event(self):
        hs = HorizontalScaling(
            policy=ReplicaPolicy(), auto_policy=AutoScalingPolicy(),
        )
        event = await hs.scale("d1", 2, 4)
        assert event.direction == ScalingDirection.UP
        assert event.from_replicas == 2
        assert event.to_replicas == 4

    @pytest.mark.asyncio
    async def test_horizontal_scale_down_event(self):
        hs = HorizontalScaling(policy=ReplicaPolicy(), auto_policy=AutoScalingPolicy())
        event = await hs.scale("d1", 4, 2)
        assert event.direction == ScalingDirection.DOWN

    def test_vertical_scaling_recommend(self):
        vs = VerticalScaling(ResourceLimits())
        rec = vs.recommend(cpu_pct=80.0, memory_pct=90.0)
        assert rec.cpu_request == "500m"
        assert rec.memory_request == "1Gi"

    def test_vertical_scaling_apply(self):
        vs = VerticalScaling(ResourceLimits())
        new_limits = ResourceLimits(cpu_request="500m", memory_request="1Gi")
        vs.apply(new_limits)
        assert vs.current_limits.cpu_request == "500m"
        assert len(vs.history) == 2


# ===========================================================================
# Environment Manager
# ===========================================================================

class TestEnvironmentManager:
    def test_default_environments_exist(self):
        em = EnvironmentManager()
        envs = em.list_environments()
        types = {e.env_type for e in envs}
        assert EnvironmentType.PRODUCTION in types
        assert EnvironmentType.DEVELOPMENT in types
        assert EnvironmentType.STAGING in types
        assert EnvironmentType.TESTING in types
        assert EnvironmentType.DISASTER_RECOVERY in types

    def test_get_environment(self):
        em = EnvironmentManager()
        env = em.get_environment(EnvironmentType.PRODUCTION)
        assert env is not None
        assert env.name == "Production"

    def test_active_environment_default_production(self):
        em = EnvironmentManager()
        env = em.active_environment
        assert env is not None
        assert env.env_type == EnvironmentType.PRODUCTION

    def test_activate_staging(self):
        em = EnvironmentManager()
        result = em.activate(EnvironmentType.STAGING)
        assert result is True
        assert em.active_environment.env_type == EnvironmentType.STAGING

    def test_only_one_environment_active(self):
        em = EnvironmentManager()
        em.activate(EnvironmentType.STAGING)
        active_count = sum(1 for e in em.list_environments() if e.is_active)
        assert active_count == 1

    def test_feature_flag_default_false(self):
        em = EnvironmentManager()
        result = em.get_feature_flag(EnvironmentType.PRODUCTION, "some_new_feature")
        assert result is False

    def test_update_config(self):
        em = EnvironmentManager()
        config = EnvironmentConfig(log_level="ERROR", replica_count=5)
        result = em.update_config(EnvironmentType.STAGING, config)
        assert result is True
        env = em.get_environment(EnvironmentType.STAGING)
        assert env.config.log_level == "ERROR"


# ===========================================================================
# Deployment Validator
# ===========================================================================

class TestDeploymentValidator:
    def test_validate_all_pass(self):
        v = DeploymentValidator()
        report = v.validate("d1")
        assert report.all_passed is True
        assert report.passed_count == 16
        assert report.failed_count == 0

    def test_validate_single_layer(self):
        v = DeploymentValidator()
        check = v.validate_layer("llm_runtime_v7_0")
        assert check.passed is True

    def test_validate_unknown_layer(self):
        v = DeploymentValidator()
        check = v.validate_layer("nonexistent_layer")
        assert check.passed is False

    def test_validate_configuration_passes(self):
        v = DeploymentValidator()
        config = {"platform_version": "7.8.0", "environment": "production", "strategy": "rolling"}
        assert v.validate_configuration(config) is True

    def test_validate_configuration_fails_missing(self):
        v = DeploymentValidator()
        assert v.validate_configuration({}) is False

    def test_validate_compatibility_same_major(self):
        v = DeploymentValidator()
        assert v.validate_compatibility("7.7.0", "7.8.0") is True

    def test_validate_compatibility_different_major(self):
        v = DeploymentValidator()
        assert v.validate_compatibility("6.0.0", "7.8.0") is False


# ===========================================================================
# Health Manager
# ===========================================================================

class TestDeploymentHealthManager:
    @pytest.mark.asyncio
    async def test_check_deployment_health_default_green(self):
        hm = DeploymentHealthManager()
        report = await hm.check_deployment_health("d1")
        assert report.health_level == DeploymentHealthLevel.GREEN
        assert report.is_healthy is True

    @pytest.mark.asyncio
    async def test_check_platform_health(self):
        hm = DeploymentHealthManager()
        summary = await hm.check_platform_health()
        assert summary.overall_health == DeploymentHealthLevel.GREEN
        assert summary.total_deployments >= 1

    def test_record_custom_report(self):
        hm = DeploymentHealthManager()
        report = DeploymentHealthReport(
            deployment_id="d2",
            health_level=DeploymentHealthLevel.YELLOW,
            is_healthy=False,
            replica_count=2,
            ready_replicas=1,
        )
        hm.record_report(report)
        assert "d2" in hm._reports

    def test_availability_pct(self):
        report = DeploymentHealthReport(
            deployment_id="d3",
            replica_count=4,
            ready_replicas=3,
        )
        assert report.availability_pct == 75.0

    def test_health_level_enum(self):
        assert DeploymentHealthLevel.GREEN.value == "green"
        assert DeploymentHealthLevel.RED.value == "red"


# ===========================================================================
# Backup Manager
# ===========================================================================

class TestBackupManager:
    def test_register_plan(self):
        bm = BackupManager()
        plan = BackupPlan(plan_id="plan1", name="Daily Full", backup_type=BackupType.FULL)
        bm.register_plan(plan)
        assert len(bm.list_plans()) == 1

    @pytest.mark.asyncio
    async def test_execute_backup(self):
        bm = BackupManager()
        plan = BackupPlan(plan_id="plan2", name="Hourly Inc", backup_type=BackupType.INCREMENTAL)
        bm.register_plan(plan)
        snapshot = await bm.execute_backup("plan2")
        assert snapshot.status == BackupStatus.COMPLETED
        assert snapshot.size_bytes > 0

    @pytest.mark.asyncio
    async def test_execute_backup_missing_plan(self):
        bm = BackupManager()
        with pytest.raises(ValueError):
            await bm.execute_backup("nonexistent")

    def test_get_latest_snapshot(self):
        bm = BackupManager()
        plan = BackupPlan(plan_id="plan3", name="Test", backup_type=BackupType.SNAPSHOT)
        bm.register_plan(plan)
        import asyncio
        asyncio.run(bm.execute_backup("plan3"))
        asyncio.run(bm.execute_backup("plan3"))
        snap = bm.get_latest_snapshot("plan3")
        assert snap is not None

    def test_get_latest_snapshot_missing(self):
        bm = BackupManager()
        assert bm.get_latest_snapshot("nonexistent") is None

    def test_list_snapshots_by_plan(self):
        bm = BackupManager()
        plan = BackupPlan(plan_id="plan4", name="Test2", backup_type=BackupType.FULL)
        bm.register_plan(plan)
        import asyncio
        asyncio.run(bm.execute_backup("plan4"))
        snaps = bm.list_snapshots("plan4")
        assert len(snaps) == 1


# ===========================================================================
# Recovery Manager
# ===========================================================================

class TestRecoveryManager:
    def test_register_plan(self):
        rm = RecoveryManager()
        plan = RecoveryPlan(plan_id="dr1", name="Primary DR")
        rm.register_plan(plan)
        assert len(rm.list_plans()) == 1

    @pytest.mark.asyncio
    async def test_trigger_recovery(self):
        rm = RecoveryManager()
        plan = RecoveryPlan(plan_id="dr2", name="DR Plan 2", rto_minutes=30, rpo_minutes=60)
        rm.register_plan(plan)
        report = await rm.trigger_recovery("dr2", RecoveryTrigger.MANUAL)
        from app.deployment.recovery import RecoveryStatus
        assert report.status == RecoveryStatus.RECOVERED
        assert report.validation_passed is True

    @pytest.mark.asyncio
    async def test_trigger_recovery_missing_plan(self):
        rm = RecoveryManager()
        with pytest.raises(ValueError):
            await rm.trigger_recovery("nonexistent")

    @pytest.mark.asyncio
    async def test_test_recovery_scheduled(self):
        rm = RecoveryManager()
        plan = RecoveryPlan(plan_id="dr3", name="DR Test")
        rm.register_plan(plan)
        report = await rm.test_recovery("dr3")
        assert report.trigger == RecoveryTrigger.SCHEDULED_TEST

    def test_recovery_rto_within_sla(self):
        rm = RecoveryManager()
        plan = RecoveryPlan(plan_id="dr4", name="SLA Test", rto_minutes=30)
        rm.register_plan(plan)
        import asyncio
        report = asyncio.run(rm.trigger_recovery("dr4", RecoveryTrigger.MANUAL))
        assert report.actual_rto_minutes <= plan.rto_minutes


# ===========================================================================
# Release Manager
# ===========================================================================

class TestReleaseManager:
    def test_register_and_get_release(self):
        rm = ReleaseManager()
        manifest = ReleaseManifest(version="7.8.0", release_name="Phase 7.8")
        rm.register_release(manifest)
        assert rm.get_manifest("7.8.0") is not None

    def test_current_version_set_on_first_register(self):
        rm = ReleaseManager()
        manifest = ReleaseManifest(version="7.8.0", release_name="Phase 7.8")
        rm.register_release(manifest)
        assert rm.current_version == "7.8.0"

    def test_promote_version(self):
        rm = ReleaseManager()
        rm.register_release(ReleaseManifest(version="7.7.0", release_name="v7.7"))
        rm.register_release(ReleaseManifest(version="7.8.0", release_name="v7.8"))
        rm.promote("7.8.0")
        assert rm.current_version == "7.8.0"

    def test_invalid_semver_raises(self):
        rm = ReleaseManager()
        with pytest.raises(ValueError):
            rm.register_release(ReleaseManifest(version="not.semver", release_name="Bad"))

    def test_valid_semver(self):
        rm = ReleaseManager()
        assert rm.is_valid_semver("7.8.0")
        assert rm.is_valid_semver("1.0.0")
        assert not rm.is_valid_semver("7.8")
        assert not rm.is_valid_semver("v7.8.0")

    def test_compatibility_no_breaking_changes(self):
        rm = ReleaseManager()
        rm.register_release(ReleaseManifest(version="7.7.0", release_name="v7.7"))
        rm.register_release(ReleaseManifest(version="7.8.0", release_name="v7.8", breaking_changes=[]))
        result = rm.validate_compatibility("7.7.0", "7.8.0")
        assert result["is_compatible"] is True

    def test_compatibility_with_breaking_changes(self):
        rm = ReleaseManager()
        rm.register_release(ReleaseManifest(version="7.7.0", release_name="v7.7"))
        rm.register_release(ReleaseManifest(
            version="7.8.0", release_name="v7.8", breaking_changes=["API /old endpoint removed"]
        ))
        result = rm.validate_compatibility("7.7.0", "7.8.0")
        assert result["is_compatible"] is False


# ===========================================================================
# SemVer
# ===========================================================================

class TestSemVer:
    def test_parse(self):
        v = SemVer.parse("7.8.0")
        assert v.major == 7
        assert v.minor == 8
        assert v.patch == 0

    def test_str(self):
        v = SemVer(7, 8, 0)
        assert str(v) == "7.8.0"

    def test_lt(self):
        assert SemVer(7, 7, 0) < SemVer(7, 8, 0)

    def test_eq(self):
        assert SemVer(7, 8, 0) == SemVer(7, 8, 0)

    def test_compatible_with_same_major(self):
        assert SemVer(7, 8, 0).is_compatible_with(SemVer(7, 7, 0))

    def test_incompatible_different_major(self):
        assert not SemVer(7, 8, 0).is_compatible_with(SemVer(8, 0, 0))

    def test_next_patch(self):
        v = SemVer(7, 8, 0).next_patch()
        assert v == SemVer(7, 8, 1)

    def test_next_minor(self):
        v = SemVer(7, 8, 0).next_minor()
        assert v == SemVer(7, 9, 0)

    def test_next_major(self):
        v = SemVer(7, 8, 0).next_major()
        assert v == SemVer(8, 0, 0)

    def test_parse_invalid(self):
        with pytest.raises(ValueError):
            SemVer.parse("not.valid")


# ===========================================================================
# Registry
# ===========================================================================

class TestDeploymentRegistry:
    def test_register_and_get(self):
        reg = DeploymentRegistry()
        d = Deployment(deployment_id="r1", status=DeploymentStatus.ACTIVE)
        reg.register(d)
        assert reg.get("r1") is not None

    def test_list_all(self):
        reg = DeploymentRegistry()
        reg.register(Deployment(deployment_id="r2"))
        reg.register(Deployment(deployment_id="r3"))
        assert len(reg.list_all()) == 2

    def test_list_by_status(self):
        reg = DeploymentRegistry()
        reg.register(Deployment(deployment_id="r4", status=DeploymentStatus.ACTIVE))
        reg.register(Deployment(deployment_id="r5", status=DeploymentStatus.FAILED))
        assert len(reg.list_by_status(DeploymentStatus.ACTIVE)) == 1

    def test_update_status(self):
        reg = DeploymentRegistry()
        reg.register(Deployment(deployment_id="r6"))
        result = reg.update_status("r6", DeploymentStatus.TERMINATED)
        assert result is True
        assert reg.get("r6").status == DeploymentStatus.TERMINATED

    def test_remove(self):
        reg = DeploymentRegistry()
        reg.register(Deployment(deployment_id="r7"))
        result = reg.remove("r7")
        assert result is True
        assert reg.get("r7") is None

    def test_total_count(self):
        reg = DeploymentRegistry()
        reg.register(Deployment(deployment_id="r8"))
        reg.register(Deployment(deployment_id="r9"))
        assert reg.total_count == 2


# ===========================================================================
# Config / Context / Capabilities / Policy
# ===========================================================================

class TestDeploymentConfig:
    def test_defaults(self):
        c = DeploymentConfig()
        assert c.platform_version == "7.8.0"
        assert c.default_environment == "production"
        assert c.enable_auto_scaling is True


class TestDeploymentContext:
    def test_defaults(self):
        ctx = DeploymentContext()
        assert ctx.dry_run is False
        assert ctx.environment == "production"


class TestDeploymentCapabilities:
    def test_defaults(self):
        caps = DeploymentCapabilities()
        assert caps.supports_rolling is True
        assert caps.supports_blue_green is True
        assert caps.supports_canary is True
        assert caps.supports_horizontal_scaling is True
        assert caps.supports_disaster_recovery is True


class TestDeploymentPolicy:
    def test_defaults(self):
        policy = DeploymentPolicy()
        assert policy.require_validation_before_deploy is True
        assert policy.rollback_on_health_failure is True
        assert policy.deployment_freeze_enabled is False


# ===========================================================================
# Serializer
# ===========================================================================

class TestDeploymentSerializer:
    def test_serialize_dataclass(self):
        config = DeploymentConfig()
        d = DeploymentSerializer.to_dict(config)
        assert "platform_version" in d

    def test_serialize_to_json(self):
        config = DeploymentConfig()
        json_str = DeploymentSerializer.to_json(config)
        assert "7.8.0" in json_str


# ===========================================================================
# Statistics / Metrics / Analytics
# ===========================================================================

class TestStatisticsAndMetrics:
    def test_statistics_defaults(self):
        s = DeploymentStatistics()
        assert s.total_deployments == 0
        assert s.successful_deployments == 0

    def test_metrics_defaults(self):
        m = DeploymentMetrics()
        assert m.cpu_utilization_pct == 0.0

    def test_analytics_defaults(self):
        a = DeploymentAnalytics()
        assert a.rollback_rate_pct == 0.0

    def test_analytics_engine_compute(self):
        engine = DeploymentAnalyticsEngine()
        analytics = engine.compute(total_deployments=10, failed_deployments=1, rollbacks=2)
        assert analytics.change_failure_rate_pct == 10.0
        assert analytics.rollback_rate_pct == 20.0

    def test_metrics_collector_record_latency(self):
        mc = DeploymentMetricsCollector()
        mc.record_latency(150.0)
        mc.record_latency(200.0)
        assert mc.metrics.p95_latency_ms == 200.0

    def test_metrics_collector_record_cpu(self):
        mc = DeploymentMetricsCollector()
        mc.record_cpu(75.0)
        assert mc.metrics.cpu_utilization_pct == 75.0


# ===========================================================================
# Events and Hooks
# ===========================================================================

class TestDeploymentEvents:
    def test_emit_and_get_events(self):
        bus = DeploymentEventBus()
        bus.emit(DeploymentEvent(event_type="deploy", deployment_id="d1"))
        assert len(bus.get_events()) == 1

    def test_filter_by_deployment_id(self):
        bus = DeploymentEventBus()
        bus.emit(DeploymentEvent(event_type="deploy", deployment_id="d1"))
        bus.emit(DeploymentEvent(event_type="scale", deployment_id="d2"))
        events = bus.get_events("d1")
        assert len(events) == 1
        assert events[0].deployment_id == "d1"


class TestDeploymentHooks:
    @pytest.mark.asyncio
    async def test_hook_runs(self):
        hooks = DeploymentHooks()

        async def my_hook(ctx: dict) -> bool:
            return True

        hooks.register("pre_deploy", my_hook)
        results = await hooks.run("pre_deploy", {})
        assert len(results) == 1
        assert results[0].passed is True

    @pytest.mark.asyncio
    async def test_hook_failure(self):
        hooks = DeploymentHooks()

        async def failing_hook(ctx: dict) -> bool:
            raise ValueError("Hook failed!")

        hooks.register("post_deploy", failing_hook)
        results = await hooks.run("post_deploy", {})
        assert results[0].passed is False


# ===========================================================================
# Exceptions
# ===========================================================================

class TestDeploymentExceptions:
    def test_all_exceptions_inherit_base(self):
        for exc_cls in [
            DeploymentValidationError, RollbackError, ScalingError,
            BackupError, RecoveryError, ReleaseCompatibilityError,
            EnvironmentNotFoundError, DeploymentStrategyError,
        ]:
            assert issubclass(exc_cls, DeploymentError)

    def test_raise_and_catch(self):
        with pytest.raises(DeploymentError):
            raise DeploymentValidationError("Validation failed")


# ===========================================================================
# Contracts (Pydantic DTOs)
# ===========================================================================

class TestDeploymentContracts:
    def test_validate_payload(self):
        p = DeploymentValidatePayload(deployment_id="d1")
        assert p.platform_version == "7.8.0"

    def test_deploy_payload(self):
        p = DeploymentDeployPayload(deployment_id="d1", image_tag="7.8.0", replica_count=3)
        assert p.replica_count == 3

    def test_rollback_payload(self):
        p = DeploymentRollbackPayload(deployment_id="d1", snapshot_id="snap1")
        assert p.strategy == "rolling"

    def test_scale_payload(self):
        p = DeploymentScalePayload(deployment_id="d1", target_replicas=5)
        assert p.target_replicas == 5
