from typing import Optional

from app.context.state import ConversationState
from app.context.types import NodeType
from app.workflow.base import BaseWorkflowNode
from app.workflow.metadata import NodeExecutionContext
from app.workflow.node_types import WorkflowNodeType


class MemoryNode(BaseWorkflowNode):
    """
    Workflow Node representing future memory retrieval/storage.
    Must NOT execute memory strategy operations. Only defines contract.
    """

    node_name: str = "MemoryNode"
    node_type: NodeType = NodeType.MEMORY
    node_category: WorkflowNodeType = WorkflowNodeType.MEMORY
    node_description: str = "Memory operations contract node."

    async def execute(
        self, state: ConversationState, context: Optional[NodeExecutionContext] = None
    ) -> ConversationState:
        """Asynchronously executes memory node logic (state pass-through contract placeholder)."""
        return state
