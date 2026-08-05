from typing import Optional

from app.context.state import ConversationState
from app.context.types import NodeType
from app.workflow.base import BaseWorkflowNode
from app.workflow.metadata import NodeExecutionContext
from app.workflow.node_types import WorkflowNodeType


class ToolNode(BaseWorkflowNode):
    """
    Workflow Node representing future tool/function execution.
    Must NOT execute external tools. Only defines contract.
    """

    node_name: str = "ToolNode"
    node_type: NodeType = NodeType.TOOL
    node_category: WorkflowNodeType = WorkflowNodeType.TOOL
    node_description: str = "Tool execution contract node."

    async def execute(
        self, state: ConversationState, context: Optional[NodeExecutionContext] = None
    ) -> ConversationState:
        """Asynchronously executes tool node logic (state pass-through contract placeholder)."""
        return state
