from pydantic import BaseModel, Field
from app.memory.memory import Memory


class MemoryQualityReport(BaseModel):
    """Scorecard analyzing memory quality, content density, and redundancy risk."""

    content_density_score: float = Field(default=85.0, ge=0.0, le=100.0)
    redundancy_risk: str = Field(default="low", description="'low', 'medium', 'high'")
    overall_quality_grade: str = Field(default="A", description="'A', 'B', 'C', 'D'")


class MemoryQualityAnalyzer:
    """Evaluates memory entries and produces quality scorecards."""

    def analyze(self, memory: Memory) -> MemoryQualityReport:
        content_len = len(memory.content)
        risk = "low"
        if content_len < 10:
            risk = "high"
        elif content_len > 1000:
            risk = "medium"

        grade = "A" if risk == "low" else ("B" if risk == "medium" else "C")
        return MemoryQualityReport(
            content_density_score=min(100.0, max(40.0, content_len * 2.0)),
            redundancy_risk=risk,
            overall_quality_grade=grade,
        )
