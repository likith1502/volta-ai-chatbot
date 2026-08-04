import inspect
from typing import Any, Awaitable, Callable, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from app.context.state import ConversationState
from app.graph.contracts import IGraphEdge


class GraphEdge(BaseModel, IGraphEdge):
    """
    Directed graph edge connecting a source node to a target node.
    Supports optional priority and conditional predicate evaluation.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    source_node: str
    target_node: str
    edge_condition: Optional[
        Union[Callable[[ConversationState], bool], Callable[[ConversationState], Awaitable[bool]], str]
    ] = None
    priority: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)

    async def evaluate(self, state: ConversationState) -> bool:
        """
        Evaluates the edge condition predicate against the given ConversationState.
        Returns True if condition is satisfied or if edge is unconditional (edge_condition is None).
        """
        if self.edge_condition is None:
            return True

        if callable(self.edge_condition):
            res = self.edge_condition(state)
            if inspect.isawaitable(res):
                return bool(await res)
            return bool(res)

        if isinstance(self.edge_condition, str):
            res = state.execution.node_results.get(self.edge_condition)
            if res is not None:
                return bool(res)
            return bool(state.memory.extracted_entities.get(self.edge_condition))

        return True
