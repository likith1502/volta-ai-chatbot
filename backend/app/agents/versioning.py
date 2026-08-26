from pydantic import BaseModel, Field


class AgentVersion(BaseModel):
    version: str = "7.5.0"
    milestone: str = "Phase 7.5 Enterprise Multi-Agent Orchestration Runtime"
    frozen_dependencies: list[str] = Field(
        default_factory=lambda: [
            "app.runtime (v7.0)",
            "app.prompt (v7.1)",
            "app.memory (v7.2)",
            "app.tools (v7.3)",
            "app.graph_runtime (v7.4)",
        ]
    )
