from typing import Optional

from app.context.state import ConversationState
from app.context.types import NodeType
from app.workflow.base import BaseWorkflowNode
from app.workflow.metadata import NodeExecutionContext
from app.workflow.node_types import WorkflowNodeType


class EndNode(BaseWorkflowNode):
    """
    Workflow Node responsible for terminating workflow execution.
    Acts as the exit node contract placeholder in workflow graphs.
    """

    node_name: str = "EndNode"
    node_type: NodeType = NodeType.OUTPUT
    node_category: WorkflowNodeType = WorkflowNodeType.END
    node_description: str = "Workflow terminal node."

    async def execute(
        self, state: ConversationState, context: Optional[NodeExecutionContext] = None
    ) -> ConversationState:
        """Asynchronously executes end node logic (state pass-through contract placeholder)."""
        return state
