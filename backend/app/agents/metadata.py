from pydantic import BaseModel, Field


class AgentMetadata(BaseModel):
    """Metadata tags and operational labels for an agent."""

    tags: list[str] = Field(default_factory=lambda: ["enterprise", "v7.5"])
    domain: str = "urban_mobility"
    author: str = "Volta Engineering"
    version: str = "7.5.0"
