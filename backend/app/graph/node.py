from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.context.state import ConversationState
from app.context.types import NodeType
from app.graph.contracts import IGraphNode


class BaseNode(BaseModel, IGraphNode, ABC):
    """
    Base abstract node component for graph workflows.
    All workflow nodes must inherit from this class and implement the execute() method.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    node_id: str
    node_name: str
    node_type: NodeType = NodeType.CUSTOM
    description: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)

    @abstractmethod
    async def execute(self, state: ConversationState) -> ConversationState:
        """
        Asynchronously executes node operations on state and returns an updated ConversationState.
        Must be implemented by concrete node subclasses.
        """
        pass
