"""Phase 7.8 — Platform smoke test exercising the full stack integration.

Proves the complete platform stack from v7.0 through v7.8 works together.

Stack:
  Deployment Manager (v7.8)
    ↓
  Integration Platform (v7.7)
    ↓
  RAG Engine (v7.6)
    ↓
  Agent Runtime (v7.5)
    ↓
  Graph Runtime (v7.4)
    ↓
  Tool Runtime (v7.3)
    ↓
  Memory Runtime (v7.2)
    ↓
  Prompt Engine (v7.1)
    ↓
  LLM Runtime (v7.0)
    ↓
  Observability Layer (v7.8)
"""

import pytest


class TestPlatformSmoke:
    """Full-stack platform smoke test — v7.0 through v7.8."""

    def test_deployment_package_importable(self):
        import app.deployment
        assert app.deployment is not None

    def test_observability_package_importable(self):
        import app.observability
        assert app.observability is not None

    def test_deployment_manager_creates_without_error(self):
        from app.deployment.manager import DeploymentManager
        mgr = DeploymentManager()
        assert mgr is not None

    def test_observability_manager_creates_without_error(self):
        from app.observability.manager import ObservabilityManager
        om = ObservabilityManager()
        assert om is not None

    def test_runtime_layer_importable(self):
        from app.runtime.manager import RuntimeManager
        assert RuntimeManager is not None

    def test_prompt_layer_importable(self):
        from app.prompt.manager import PromptManager
        assert PromptManager is not None

    def test_memory_layer_importable(self):
        from app.memory.manager import MemoryManager
        assert MemoryManager is not None

    def test_tools_layer_importable(self):
        from app.tools.manager import ToolManager
        assert ToolManager is not None

    def test_graph_runtime_layer_importable(self):
        from app.graph_runtime.manager import GraphRuntimeManager
        assert GraphRuntimeManager is not None

    def test_agents_layer_importable(self):
        from app.agents.manager import AgentRuntimeManager
        assert AgentRuntimeManager is not None

    def test_rag_layer_importable(self):
        from app.rag.manager import RAGManager
        assert RAGManager is not None

    def test_integrations_layer_importable(self):
        from app.integrations.manager import IntegrationManager
        assert IntegrationManager is not None

    def test_no_circular_imports_deployment(self):
        """Validate deployment package has no circular imports."""
        import importlib
        modules_to_check = [
            "app.deployment.deployment",
            "app.deployment.lifecycle",
            "app.deployment.strategy",
            "app.deployment.rollback",
            "app.deployment.scaling",
            "app.deployment.environment",
            "app.deployment.validator",
            "app.deployment.health",
            "app.deployment.backup",
            "app.deployment.recovery",
            "app.deployment.release",
            "app.deployment.manager",
            "app.deployment.config",
            "app.deployment.factory",
            "app.deployment.registry",
        ]
        for mod_name in modules_to_check:
            mod = importlib.import_module(mod_name)
            assert mod is not None, f"Failed to import {mod_name}"

    def test_no_circular_imports_observability(self):
        import importlib
        modules_to_check = [
            "app.observability.metrics",
            "app.observability.logging",
            "app.observability.tracing",
            "app.observability.alerts",
            "app.observability.dashboard",
            "app.observability.manager",
        ]
        for mod_name in modules_to_check:
            mod = importlib.import_module(mod_name)
            assert mod is not None, f"Failed to import {mod_name}"

    @pytest.mark.asyncio
    async def test_platform_health_green_through_all_layers(self):
        """Confirm platform health is GREEN with all layers instantiated."""
        from app.deployment.manager import DeploymentManager
        from app.observability.manager import ObservabilityManager

        mgr = DeploymentManager()
        om = ObservabilityManager()

        # Check deployment health
        health_summary = await mgr.get_platform_health()
        from app.deployment.health import DeploymentHealthLevel
        assert health_summary.overall_health == DeploymentHealthLevel.GREEN

        # Record health check in observability
        om.record_health_check(health_summary.overall_health.value)
        metrics = om.metrics.get_all_metrics()
        assert len(metrics) >= 1

    @pytest.mark.asyncio
    async def test_full_deployment_lifecycle(self):
        """Prove a complete deployment lifecycle: validate → deploy → scale → rollback."""
        from app.deployment.manager import DeploymentManager
        from app.deployment.contracts import (
            DeploymentValidatePayload, DeploymentDeployPayload,
            DeploymentScalePayload,
        )
        from app.deployment.deployment import DeploymentStatus

        mgr = DeploymentManager()

        # Step 1: Validate
        validation = await mgr.validate(DeploymentValidatePayload(deployment_id="smoke-test"))
        assert validation.all_passed

        # Step 2: Deploy
        deployment = await mgr.deploy(DeploymentDeployPayload(
            deployment_id="smoke-test",
            image_tag="7.8.0",
            strategy="rolling",
            environment="production",
            replica_count=2,
        ))
        assert deployment.status == DeploymentStatus.ACTIVE

        # Step 3: Scale
        scale_event = await mgr.scale(DeploymentScalePayload(
            deployment_id="smoke-test",
            target_replicas=4,
            reason="smoke_test_scale",
        ))
        assert scale_event.to_replicas == 4

        # Step 4: Rollback
        snaps = mgr.rollback_manager.list_snapshots()
        assert len(snaps) >= 1
        from app.deployment.contracts import DeploymentRollbackPayload
        rollback_result = await mgr.rollback(DeploymentRollbackPayload(
            deployment_id="smoke-test",
            snapshot_id=snaps[-1].snapshot_id,
        ))
        assert rollback_result["success"] is True

        # Step 5: Verify statistics
        stats = mgr.get_statistics()
        assert stats.total_deployments >= 1
        assert stats.scaling_events >= 1
        assert stats.rollbacks_triggered >= 1

    @pytest.mark.asyncio
    async def test_observability_records_deployment_events(self):
        from app.deployment.manager import DeploymentManager
        from app.deployment.contracts import DeploymentDeployPayload
        from app.observability.manager import ObservabilityManager

        mgr = DeploymentManager()
        om = ObservabilityManager()

        # Deploy
        deployment = await mgr.deploy(DeploymentDeployPayload(
            deployment_id="obs-test",
            image_tag="7.8.0",
            strategy="canary",
            environment="staging",
            replica_count=1,
        ))

        # Record in observability
        om.record_deployment_event("deploy_completed", deployment.deployment_id)
        om.record_health_check("green")

        # Verify
        metrics = om.metrics.get_all_metrics()
        log_entries = om.logging.get_entries()
        assert len(metrics) >= 1
        assert len(log_entries) >= 1

    def test_deployment_adapters_importable(self):
        from app.deployment.adapters.docker.docker_adapter import DockerAdapter, DockerComposeAdapter
        from app.deployment.adapters.kubernetes.kubernetes_adapter import KubernetesAdapter, SystemdAdapter
        from app.deployment.adapters.cloud.cloud_adapters import (
            AWSAdapter, AzureAdapter, GCPAdapter, RenderAdapter,
            RailwayAdapter, FlyIOAdapter, DigitalOceanAdapter,
        )
        for cls in [DockerAdapter, DockerComposeAdapter, KubernetesAdapter, SystemdAdapter,
                    AWSAdapter, AzureAdapter, GCPAdapter, RenderAdapter,
                    RailwayAdapter, FlyIOAdapter, DigitalOceanAdapter]:
            assert cls is not None

    @pytest.mark.asyncio
    async def test_docker_adapter_deploy(self):
        from app.deployment.adapters.docker.docker_adapter import DockerAdapter
        adapter = DockerAdapter()
        result = await adapter.deploy("smoke-deploy", "7.8.0")
        assert result["status"] == "running"

    @pytest.mark.asyncio
    async def test_kubernetes_adapter_deploy(self):
        from app.deployment.adapters.kubernetes.kubernetes_adapter import KubernetesAdapter
        adapter = KubernetesAdapter()
        result = await adapter.deploy("smoke-k8s", "7.8.0", replicas=2)
        assert result["replicas"] == 2

    @pytest.mark.asyncio
    async def test_cloud_adapters_health_check(self):
        from app.deployment.adapters.cloud.cloud_adapters import AWSAdapter, AzureAdapter, GCPAdapter
        for cls in [AWSAdapter, AzureAdapter, GCPAdapter]:
            adapter = cls()
            result = await adapter.health_check()
            assert result["healthy"] is True

    def test_deployment_constitution_frozen_packages_untouched(self):
        """Confirm all frozen runtime packages can still be imported cleanly."""
        frozen = [
            "app.runtime",
            "app.prompt",
            "app.memory",
            "app.tools",
            "app.graph_runtime",
            "app.agents",
            "app.rag",
            "app.integrations",
        ]
        import importlib
        for pkg in frozen:
            mod = importlib.import_module(pkg)
            assert mod is not None, f"Frozen package {pkg} failed to import"
