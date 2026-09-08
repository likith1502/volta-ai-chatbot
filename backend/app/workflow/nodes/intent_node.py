from typing import Optional

from app.ai.prompts.recommendation import is_recommendation_requested
from app.context.state import ConversationState
from app.context.types import NodeType
from app.workflow.base import BaseWorkflowNode
from app.workflow.metadata import NodeExecutionContext
from app.workflow.node_types import WorkflowNodeType


class IntentNode(BaseWorkflowNode):
    """
    Workflow Node for conversational intent classification.
    Identifies ride recommendation vs general conversation intent.
    """

    node_name: str = "IntentNode"
    node_type: NodeType = NodeType.GUARDRAIL
    node_category: WorkflowNodeType = WorkflowNodeType.INTENT
    node_description: str = "Intent classification workflow node."

    async def execute(
        self, state: ConversationState, context: Optional[NodeExecutionContext] = None
    ) -> ConversationState:
        """Asynchronously classifies intent from state conversational message."""
        if not state.conversation.current_message:
            return state

        user_text = state.conversation.current_message.get("content", "")
        is_rec = is_recommendation_requested(user_text)
        intent_payload = {
            "intent": "ride_recommendation" if is_rec else "conversation",
            "confidence": 0.95 if is_rec else 0.90,
            "requires_recommendation": is_rec,
        }

        new_node_results = dict(state.execution.node_results)
        new_node_results[self.node_id] = intent_payload

        return state.with_update(
            workflow_step=self.node_id,
            detected_intent=intent_payload,
            node_results=new_node_results,
        )
