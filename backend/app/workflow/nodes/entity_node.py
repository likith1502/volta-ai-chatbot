from typing import Optional

from app.context.state import ConversationState
from app.context.types import NodeType
from app.workflow.base import BaseWorkflowNode
from app.workflow.metadata import NodeExecutionContext
from app.workflow.node_types import WorkflowNodeType


class EntityNode(BaseWorkflowNode):
    """
    Workflow Node representing future entity extraction.
    Must NOT perform entity extraction directly. Only defines contract.
    """

    node_name: str = "EntityNode"
    node_type: NodeType = NodeType.GUARDRAIL
    node_category: WorkflowNodeType = WorkflowNodeType.ENTITY
    node_description: str = "Entity extraction contract node."

    async def execute(
        self, state: ConversationState, context: Optional[NodeExecutionContext] = None
    ) -> ConversationState:
        """Asynchronously executes entity node logic (state pass-through contract placeholder)."""
        return state
