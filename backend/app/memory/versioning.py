from pydantic import BaseModel


class MemoryVersion(BaseModel):
    """Version tracking model for memory schema and runtime releases."""

    memory_version: str = "7.2.0"
    schema_version: str = "v1"
    serializer_version: str = "1.0.0"
