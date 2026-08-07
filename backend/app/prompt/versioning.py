from datetime import datetime, timezone
from pydantic import BaseModel, Field


class TemplateRevision(BaseModel):
    """Immutable template revision record representing a specific version snapshot (e.g. 'v1', 'v2')."""

    revision_id: str = Field(default="v1", description="'v1', 'v2', 'v3'")
    template_id: str
    content_template: str
    system_instruction: str = ""
    author: str = "system"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    change_summary: str = "Initial revision"


class PromptVersion(BaseModel):
    """Version tracking model for prompt schema and runtime releases."""

    prompt_version: str = "7.1.0"
    schema_version: str = "v1"
    template_version: str = "1.0.0"
