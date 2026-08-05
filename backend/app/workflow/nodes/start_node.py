from typing import Optional

from app.context.state import ConversationState
from app.context.types import NodeType
from app.workflow.base import BaseWorkflowNode
from app.workflow.metadata import NodeExecutionContext
from app.workflow.node_types import WorkflowNodeType


class StartNode(BaseWorkflowNode):
    """
    Workflow Node responsible for starting workflow execution.
    Acts as the entry node contract placeholder in workflow graphs.
    """

    node_name: str = "StartNode"
    node_type: NodeType = NodeType.INPUT
    node_category: WorkflowNodeType = WorkflowNodeType.START
    node_description: str = "Workflow entrypoint node."

    async def execute(
        self, state: ConversationState, context: Optional[NodeExecutionContext] = None
    ) -> ConversationState:
        """Asynchronously executes start node logic (state pass-through contract placeholder)."""
        return state
