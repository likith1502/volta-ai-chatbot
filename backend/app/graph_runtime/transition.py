from typing import Optional

from pydantic import BaseModel


class GraphTransition(BaseModel):
    """Represents a state transition edge between two runtime graph nodes."""

    from_node: str
    to_node: str
    condition_key: Optional[str] = None
    is_executed: bool = False
