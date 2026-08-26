"""Deployment policy — operational constraints and governance."""

from dataclasses import dataclass


@dataclass
class DeploymentPolicy:
    require_validation_before_deploy: bool = True
    require_backup_before_deploy: bool = True
    rollback_on_health_failure: bool = True
    allow_production_deploy_without_staging: bool = False
    enforce_semantic_versioning: bool = True
    max_canary_weight_pct: int = 50
    min_healthy_replicas_before_scale_down: int = 1
    auto_rollback_on_error_rate_pct: float = 5.0
    deployment_freeze_enabled: bool = False
    deployment_freeze_reason: str = ""
