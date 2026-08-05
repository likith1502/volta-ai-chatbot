from pydantic import BaseModel


class CheckpointVersion(BaseModel):
    """Versioning specifications for checkpoint schemas, state models, and graphs."""

    checkpoint_version: str = "1.0.0"
    schema_version: str = "1.0"
    state_version: str = "1.0"
    execution_version: str = "1.0"
    graph_version: str = "1.0"
