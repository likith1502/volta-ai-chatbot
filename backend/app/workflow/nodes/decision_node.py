from typing import Optional

from app.context.state import ConversationState
from app.context.types import NodeType
from app.workflow.base import BaseWorkflowNode
from app.workflow.metadata import NodeExecutionContext
from app.workflow.node_types import WorkflowNodeType


class DecisionNode(BaseWorkflowNode):
    """
    Workflow Node responsible for branch decision contracts.
    Must NOT implement routing logic or evaluate conditions directly.
    """

    node_name: str = "DecisionNode"
    node_type: NodeType = NodeType.ROUTER
    node_category: WorkflowNodeType = WorkflowNodeType.DECISION
    node_description: str = "Branch decision contract node."

    async def execute(
        self, state: ConversationState, context: Optional[NodeExecutionContext] = None
    ) -> ConversationState:
        """Asynchronously executes decision node logic (state pass-through contract placeholder)."""
        return state
