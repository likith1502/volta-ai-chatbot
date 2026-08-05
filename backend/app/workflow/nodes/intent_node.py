from typing import Optional

from app.context.state import ConversationState
from app.context.types import NodeType
from app.workflow.base import BaseWorkflowNode
from app.workflow.metadata import NodeExecutionContext
from app.workflow.node_types import WorkflowNodeType


class IntentNode(BaseWorkflowNode):
    """
    Workflow Node representing future intent classification.
    Must NOT perform classification directly. Only defines contract.
    """

    node_name: str = "IntentNode"
    node_type: NodeType = NodeType.GUARDRAIL
    node_category: WorkflowNodeType = WorkflowNodeType.INTENT
    node_description: str = "Intent classification contract node."

    async def execute(
        self, state: ConversationState, context: Optional[NodeExecutionContext] = None
    ) -> ConversationState:
        """Asynchronously executes intent node logic (state pass-through contract placeholder)."""
        return state
