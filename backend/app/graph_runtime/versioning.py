from pydantic import BaseModel, Field


class GraphRuntimeVersion(BaseModel):
    """Version metadata container."""

    version: str = "7.4.0"
    milestone: str = "Phase 7.4 Enterprise Graph Runtime Integration"
    frozen_dependencies: list[str] = Field(
        default_factory=lambda: [
            "app.runtime (v7.0)",
            "app.prompt (v7.1)",
            "app.memory (v7.2)",
            "app.tools (v7.3)",
        ]
    )
