from pydantic import BaseModel


class WorkflowEventMetrics(BaseModel):
    """Runtime statistics tracking event dispatch throughput, latency, and success rates."""

    events_processed: int = 0
    events_failed: int = 0
    dispatch_time: float = 0.0
    listener_time: float = 0.0
    success_rate: float = 1.0
    average_latency: float = 0.0

    def compute_metrics(self) -> None:
        """Recalculates success rate and average latency metrics."""
        total = self.events_processed + self.events_failed
        if total == 0:
            self.success_rate = 1.0
            self.average_latency = 0.0
        else:
            self.success_rate = round(self.events_processed / total, 4)
            self.average_latency = round(self.dispatch_time / total, 6)
