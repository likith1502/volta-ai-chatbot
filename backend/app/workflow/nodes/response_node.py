from typing import Optional

from app.context.state import ConversationState
from app.context.types import NodeType
from app.workflow.base import BaseWorkflowNode
from app.workflow.metadata import NodeExecutionContext
from app.workflow.node_types import WorkflowNodeType


class ResponseNode(BaseWorkflowNode):
    """
    Workflow Node representing future response generation.
    Must NOT generate responses directly. Only defines contract.
    """

    node_name: str = "ResponseNode"
    node_type: NodeType = NodeType.OUTPUT
    node_category: WorkflowNodeType = WorkflowNodeType.RESPONSE
    node_description: str = "Response generation contract node."

    async def execute(
        self, state: ConversationState, context: Optional[NodeExecutionContext] = None
    ) -> ConversationState:
        """Asynchronously executes response node logic (state pass-through contract placeholder)."""
        return state
