from pydantic import BaseModel


class ReplayMetrics(BaseModel):
    """Telemetry metrics captured during execution replay operations."""

    replayed_steps: int = 0
    replay_duration: float = 0.0
    recovery_time: float = 0.0
    checkpoint_count: int = 0
    success_rate: float = 1.0

    def compute_success_rate(self, failed_steps: int = 0) -> None:
        """Calculates success rate metric."""
        total = self.replayed_steps + failed_steps
        if total == 0:
            self.success_rate = 1.0
        else:
            self.success_rate = round(max(0.0, self.replayed_steps / total), 4)
