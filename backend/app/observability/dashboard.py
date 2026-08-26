"""Dashboard provider — Grafana reference placeholder."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Dashboard:
    dashboard_id: str
    title: str
    url: str
    panels: list[str]
    data_source: str = "prometheus"


class DashboardProvider(ABC):
    @abstractmethod
    def get_dashboard(self, dashboard_id: str) -> Dashboard | None: ...

    @abstractmethod
    def list_dashboards(self) -> list[Dashboard]: ...


class GrafanaDashboardProvider(DashboardProvider):
    """Reference Grafana dashboard provider."""

    provider_id = "dashboard.grafana"
    name = "Grafana Dashboard Provider"

    def __init__(self) -> None:
        self._dashboards: dict[str, Dashboard] = {
            "platform_health": Dashboard(
                dashboard_id="platform_health",
                title="VOLTA Platform Health",
                url="http://grafana:3000/d/platform_health",
                panels=[
                    "CPU",
                    "Memory",
                    "Request Rate",
                    "Error Rate",
                    "Latency P95",
                    "Replica Count",
                ],
            ),
            "rag_performance": Dashboard(
                dashboard_id="rag_performance",
                title="RAG Engine Performance",
                url="http://grafana:3000/d/rag_performance",
                panels=[
                    "Retrieval Latency",
                    "Chunk Quality Score",
                    "Cache Hit Rate",
                    "Ingestion Queue Depth",
                ],
            ),
            "agent_activity": Dashboard(
                dashboard_id="agent_activity",
                title="Multi-Agent Runtime Activity",
                url="http://grafana:3000/d/agent_activity",
                panels=[
                    "Active Agents",
                    "Task Queue Depth",
                    "Delegation Rate",
                    "Budget Exhaustion Events",
                ],
            ),
        }

    def get_dashboard(self, dashboard_id: str) -> Dashboard | None:
        return self._dashboards.get(dashboard_id)

    def list_dashboards(self) -> list[Dashboard]:
        return list(self._dashboards.values())
