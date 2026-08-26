import logging

from app.graph_runtime.planner import GraphPlanner
from app.graph_runtime.scheduler import GraphScheduler

logger = logging.getLogger("app.graph_runtime.factory")


class GraphRuntimeFactory:
    """Factory for constructing Graph Runtime components."""

    @staticmethod
    def create_planner() -> GraphPlanner:
        return GraphPlanner()

    @staticmethod
    def create_scheduler() -> GraphScheduler:
        return GraphScheduler()
