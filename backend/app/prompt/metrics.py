from pydantic import BaseModel, Field


class PromptMetrics(BaseModel):
    """Execution telemetry and quality metrics container."""

    render_time_ms: float = Field(default=0.0, ge=0.0)
    validation_time_ms: float = Field(default=0.0, ge=0.0)
    optimization_time_ms: float = Field(default=0.0, ge=0.0)
    execution_time_ms: float = Field(default=0.0, ge=0.0)
    template_size_chars: int = Field(default=0, ge=0)
    rendered_size_chars: int = Field(default=0, ge=0)
    token_estimate: int = Field(default=0, ge=0)
    compression_ratio: float = Field(default=1.0, ge=0.0, description="Rendered size / Optimized size ratio")
    variable_coverage_pct: float = Field(default=100.0, ge=0.0, le=100.0)
    optimization_pct: float = Field(default=0.0, ge=0.0, le=100.0)
    estimated_complexity: str = Field(default="low", description="'low', 'medium', 'high'")
    validation_score: float = Field(default=1.0, ge=0.0, le=1.0)
