"""Deployment statistics and analytics."""

from dataclasses import dataclass, field


@dataclass
class DeploymentStatistics:
    total_deployments: int = 0
    successful_deployments: int = 0
    failed_deployments: int = 0
    rollbacks_triggered: int = 0
    scaling_events: int = 0
    backups_completed: int = 0
    recovery_tests_run: int = 0
    validations_run: int = 0
    validations_passed: int = 0


@dataclass
class DeploymentMetrics:
    avg_deployment_duration_seconds: float = 0.0
    avg_validation_duration_seconds: float = 0.0
    p95_latency_ms: float = 0.0
    cpu_utilization_pct: float = 0.0
    memory_utilization_pct: float = 0.0
    error_rate_pct: float = 0.0


@dataclass
class DeploymentAnalytics:
    deployment_frequency_per_day: float = 0.0
    rollback_rate_pct: float = 0.0
    mean_time_to_recovery_minutes: float = 0.0
    mean_time_between_failures_hours: float = 0.0
    change_failure_rate_pct: float = 0.0
    lead_time_for_changes_hours: float = 0.0
