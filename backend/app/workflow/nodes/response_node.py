from typing import Optional

from app.context.state import ConversationState
from app.context.types import NodeType
from app.workflow.base import BaseWorkflowNode
from app.workflow.metadata import NodeExecutionContext
from app.workflow.node_types import WorkflowNodeType


class ResponseNode(BaseWorkflowNode):
    """
    Workflow Node consolidating execution outputs into final turn response payload.
    Extracts AI inference results, tool recommendations, and token metrics.
    """

    node_name: str = "ResponseNode"
    node_type: NodeType = NodeType.OUTPUT
    node_category: WorkflowNodeType = WorkflowNodeType.RESPONSE
    node_description: str = "Response consolidation workflow node."

    async def execute(
        self, state: ConversationState, context: Optional[NodeExecutionContext] = None
    ) -> ConversationState:
        """Asynchronously consolidates final conversational response from execution state."""
        if not state.conversation.current_message and not state.execution.node_results:
            return state

        llm_data = state.execution.node_results.get("llm", {})
        tool_data = state.execution.node_results.get("tool", {})

        content = llm_data.get("content", "I am here to assist you.")
        model_used = llm_data.get("model_used", "volta-assistant")
        usage = llm_data.get("usage", {})
        recommendation_id = tool_data.get("recommendation_id")

        total_tokens = usage.get("total_tokens", 0) if isinstance(usage, dict) else 0

        response_payload = {
            "content": content,
            "model_used": model_used,
            "usage": usage,
            "total_tokens": total_tokens,
            "recommendation_id": recommendation_id,
        }

        new_node_results = dict(state.execution.node_results)
        new_node_results[self.node_id] = response_payload

        return state.with_update(
            workflow_step=self.node_id,
            node_results=new_node_results,
        )
