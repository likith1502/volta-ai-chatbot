from pydantic import BaseModel, Field


class StreamValidationResult(BaseModel):
    """Validation outcome container summarizing diagnostic results for stream payloads."""

    is_valid: bool = True
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    compatible: bool = True
    schema_version: str = "1.0"
