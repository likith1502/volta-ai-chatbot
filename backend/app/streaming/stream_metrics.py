from pydantic import BaseModel


class StreamMetrics(BaseModel):
    """Telemetry metrics capturing stream message volume, dropped count, and throughput."""

    messages_sent: int = 0
    messages_dropped: int = 0
    subscribers: int = 0
    average_latency: float = 0.0
    throughput: float = 0.0
    errors: int = 0

    def record_sent(self, latency: float = 0.0) -> None:
        """Records a successfully dispatched stream message."""
        self.messages_sent += 1
        if self.messages_sent == 1:
            self.average_latency = round(latency, 4)
        else:
            self.average_latency = round((self.average_latency * (self.messages_sent - 1) + latency) / self.messages_sent, 4)

    def record_dropped(self) -> None:
        """Records a dropped message due to backpressure or filtering."""
        self.messages_dropped += 1

    def record_error(self) -> None:
        """Records a stream dispatch error."""
        self.errors += 1
