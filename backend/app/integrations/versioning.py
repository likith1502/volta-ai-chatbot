from pydantic import BaseModel, Field


class IntegrationVersion(BaseModel):
    version: str = "7.7.0"
    milestone: str = "Phase 7.7 Enterprise Integration Platform"
    frozen_dependencies: list[str] = Field(
        default_factory=lambda: [
            "app.runtime (v7.0)",
            "app.prompt (v7.1)",
            "app.memory (v7.2)",
            "app.tools (v7.3)",
            "app.graph_runtime (v7.4)",
            "app.agents (v7.5)",
            "app.rag (v7.6)",
        ]
    )
