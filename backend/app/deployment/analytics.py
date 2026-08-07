"""Deployment analytics engine."""

from app.deployment.statistics import DeploymentAnalytics


class DeploymentAnalyticsEngine:
    def __init__(self) -> None:
        self._analytics = DeploymentAnalytics()

    def compute(
        self,
        total_deployments: int,
        failed_deployments: int,
        rollbacks: int,
        lead_time_hours: float = 2.0,
    ) -> DeploymentAnalytics:
        if total_deployments > 0:
            self._analytics.change_failure_rate_pct = (failed_deployments / total_deployments) * 100
            self._analytics.rollback_rate_pct = (rollbacks / total_deployments) * 100
        self._analytics.lead_time_for_changes_hours = lead_time_hours
        return self._analytics

    @property
    def analytics(self) -> DeploymentAnalytics:
        return self._analytics
