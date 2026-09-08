from typing import Optional

from app.context.state import ConversationState
from app.context.types import NodeType
from app.workflow.base import BaseWorkflowNode
from app.workflow.metadata import NodeExecutionContext
from app.workflow.node_types import WorkflowNodeType


class DecisionNode(BaseWorkflowNode):
    """
    Workflow Node responsible for branch decision evaluation.
    Evaluates detected intent and execution state to direct traversal route.
    """

    node_name: str = "DecisionNode"
    node_type: NodeType = NodeType.ROUTER
    node_category: WorkflowNodeType = WorkflowNodeType.DECISION
    node_description: str = "Branch decision routing node."

    async def execute(
        self, state: ConversationState, context: Optional[NodeExecutionContext] = None
    ) -> ConversationState:
        """Asynchronously evaluates routing decision from conversation intent and state."""
        if not state.conversation.current_message and not state.execution.node_results:
            return state

        intent_data = state.memory.detected_intent or {}
        requires_rec = intent_data.get("requires_recommendation", False)
        has_tool_calls = bool(state.execution.tool_calls)

        if has_tool_calls:
            route = "tool"
        elif requires_rec:
            route = "recommendation"
        else:
            route = "llm"

        decision_payload = {
            "route": route,
            "requires_tool": has_tool_calls or requires_rec,
            "selected_branch": route,
        }

        new_node_results = dict(state.execution.node_results)
        new_node_results[self.node_id] = decision_payload

        return state.with_update(
            workflow_step=self.node_id,
            node_results=new_node_results,
        )
