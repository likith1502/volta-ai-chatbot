from pydantic import BaseModel, Field


class CheckpointValidationResult(BaseModel):
    """Rich container summarizing checkpoint validation diagnostic results."""

    is_valid: bool = True
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    version_match: bool = True
    integrity_passed: bool = True
    compatible: bool = True
