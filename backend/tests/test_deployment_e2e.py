"""Phase 7.8 — DeploymentManager integration test."""

import pytest
from app.deployment.manager import DeploymentManager
from app.deployment.contracts import (
    DeploymentValidatePayload, DeploymentDeployPayload,
    DeploymentRollbackPayload, DeploymentScalePayload,
)
from app.deployment.deployment import DeploymentStatus
from app.deployment.health import DeploymentHealthLevel


class TestDeploymentManagerIntegration:
    def test_manager_initialization(self):
        mgr = DeploymentManager()
        assert mgr.validator is not None
        assert mgr.release_manager is not None
        assert mgr.backup_manager is not None
        assert mgr.recovery_manager is not None
        assert mgr.health_manager is not None
        assert mgr.registry.total_count >= 1  # seeded default

    @pytest.mark.asyncio
    async def test_validate_success(self):
        mgr = DeploymentManager()
        payload = DeploymentValidatePayload(deployment_id="test-d1")
        report = await mgr.validate(payload)
        assert report.all_passed is True
        assert mgr.statistics.validations_run == 1
        assert mgr.statistics.validations_passed == 1

    @pytest.mark.asyncio
    async def test_deploy_new_deployment(self):
        mgr = DeploymentManager()
        payload = DeploymentDeployPayload(
            deployment_id="deploy-test-1",
            image_tag="7.8.0",
            strategy="rolling",
            environment="production",
            replica_count=2,
        )
        deployment = await mgr.deploy(payload)
        assert deployment.status == DeploymentStatus.ACTIVE
        assert deployment.replica_count == 2
        assert mgr.statistics.total_deployments == 1

    @pytest.mark.asyncio
    async def test_deploy_captures_rollback_snapshot(self):
        mgr = DeploymentManager()
        payload = DeploymentDeployPayload(
            deployment_id="deploy-test-2",
            image_tag="7.8.0",
            strategy="blue_green",
            environment="staging",
            replica_count=1,
        )
        await mgr.deploy(payload)
        assert len(mgr.rollback_manager.list_snapshots()) >= 1

    @pytest.mark.asyncio
    async def test_scale_deployment(self):
        mgr = DeploymentManager()
        payload = DeploymentScalePayload(
            deployment_id="volta-platform-v7.8",
            target_replicas=4,
            reason="load_test",
        )
        event = await mgr.scale(payload)
        assert event.to_replicas == 4
        assert mgr.statistics.scaling_events == 1

    @pytest.mark.asyncio
    async def test_rollback_fails_missing_snapshot(self):
        mgr = DeploymentManager()
        payload = DeploymentRollbackPayload(
            deployment_id="volta-platform-v7.8",
            snapshot_id="nonexistent_snap",
        )
        with pytest.raises(ValueError):
            await mgr.rollback(payload)

    @pytest.mark.asyncio
    async def test_rollback_success(self):
        mgr = DeploymentManager()
        # First deploy (captures snapshot)
        deploy_payload = DeploymentDeployPayload(
            deployment_id="rb-test-deploy",
            image_tag="7.8.0",
            strategy="rolling",
            environment="production",
            replica_count=2,
        )
        await mgr.deploy(deploy_payload)
        snap = mgr.rollback_manager.list_snapshots()[0]
        rollback_payload = DeploymentRollbackPayload(
            deployment_id="rb-test-deploy",
            snapshot_id=snap.snapshot_id,
        )
        result = await mgr.rollback(rollback_payload)
        assert result["success"] is True
        assert mgr.statistics.rollbacks_triggered == 1

    @pytest.mark.asyncio
    async def test_get_platform_health(self):
        mgr = DeploymentManager()
        summary = await mgr.get_platform_health()
        assert summary.overall_health == DeploymentHealthLevel.GREEN

    @pytest.mark.asyncio
    async def test_get_deployment_status(self):
        mgr = DeploymentManager()
        status = await mgr.get_deployment_status("volta-platform-v7.8")
        assert status.deployment_id == "volta-platform-v7.8"
        assert status.platform_version == "7.8.0"

    def test_get_statistics(self):
        mgr = DeploymentManager()
        stats = mgr.get_statistics()
        assert stats.total_deployments == 0

    def test_get_analytics(self):
        mgr = DeploymentManager()
        analytics = mgr.get_analytics()
        assert "rollback_rate_pct" in analytics

    def test_event_bus_captures_events(self):
        import asyncio
        mgr = DeploymentManager()
        deploy_payload = DeploymentDeployPayload(
            deployment_id="event-test-deploy",
            image_tag="7.8.0",
            strategy="rolling",
            environment="production",
            replica_count=1,
        )
        asyncio.run(mgr.deploy(deploy_payload))
        events = mgr.event_bus.get_events()
        assert any(e.event_type == "deploy_completed" for e in events)

    def test_backup_manager_has_default_plans(self):
        mgr = DeploymentManager()
        plans = mgr.backup_manager.list_plans()
        assert len(plans) >= 2

    def test_recovery_manager_has_default_plan(self):
        mgr = DeploymentManager()
        plans = mgr.recovery_manager.list_plans()
        assert len(plans) >= 1

    def test_release_manager_current_version(self):
        mgr = DeploymentManager()
        assert mgr.release_manager.current_version == "7.8.0"

    def test_environment_manager_active_env(self):
        mgr = DeploymentManager()
        env = mgr.environment_manager.active_environment
        assert env is not None
        from app.deployment.environment import EnvironmentType
        assert env.env_type == EnvironmentType.PRODUCTION
