from typing import Optional

from app.context.state import ConversationState
from app.context.types import NodeType
from app.workflow.base import BaseWorkflowNode
from app.workflow.metadata import NodeExecutionContext
from app.workflow.node_types import WorkflowNodeType


class LLMNode(BaseWorkflowNode):
    """
    Workflow Node representing future AI model inference.
    Must NOT invoke AI vendor SDKs (OpenAI, Gemini, Claude, Ollama). Only defines contract.
    """

    node_name: str = "LLMNode"
    node_type: NodeType = NodeType.LLM
    node_category: WorkflowNodeType = WorkflowNodeType.LLM
    node_description: str = "LLM inference contract node."

    async def execute(
        self, state: ConversationState, context: Optional[NodeExecutionContext] = None
    ) -> ConversationState:
        """Asynchronously executes LLM node logic (state pass-through contract placeholder)."""
        return state
