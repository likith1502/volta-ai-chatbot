from pydantic import BaseModel, Field


class MemoryAnalyticsReport(BaseModel):
    """Telemetry report analyzing retrieval frequency, top memory types, and cleanup counts."""

    total_creations: int = Field(default=0, ge=0)
    total_searches: int = Field(default=0, ge=0)
    total_context_assemblies: int = Field(default=0, ge=0)
    average_assembly_latency_ms: float = Field(default=0.0, ge=0.0)
    expired_memories_count: int = Field(default=0, ge=0)


class MemoryAnalyticsManager:
    """Aggregates memory runtime analytics telemetry."""

    def __init__(self) -> None:
        self.creations = 0
        self.searches = 0
        self.assemblies = 0
        self.total_assembly_ms = 0.0

    def record_creation() -> None:
        self.creations += 1

    def record_search() -> None:
        self.searches += 1

    def record_assembly(self, duration_ms: float) -> None:
        self.assemblies += 1
        self.total_assembly_ms += duration_ms

    def get_report(self) -> MemoryAnalyticsReport:
        avg_lat = (self.total_assembly_ms / self.assemblies) if self.assemblies > 0 else 0.0
        return MemoryAnalyticsReport(
            total_creations=self.creations,
            total_searches=self.searches,
            total_context_assemblies=self.assemblies,
            average_assembly_latency_ms=avg_lat,
        )
