import asyncio
import logging
from typing import Any, Optional

from app.ai.exceptions import ModelUnavailableException, RateLimitException
from app.ai.factory import AIProviderFactory
from app.ai.prompts.prompt_builder import PromptBuilder
from app.context.state import ConversationState
from app.context.types import NodeType
from app.workflow.base import BaseWorkflowNode
from app.workflow.metadata import NodeExecutionContext
from app.workflow.node_types import WorkflowNodeType


logger = logging.getLogger("app.workflow.nodes.llm")

# Shown to customers when the AI service can't answer (instead of a vague
# canned line). Keep these free of internal details.
AI_BUSY_MESSAGE = (
    "I'm getting a lot of requests right now. "
    "Please wait a few seconds and send your message again."
)
AI_UNAVAILABLE_MESSAGE = (
    "Sorry, I couldn't reach the VOLTA assistant just now. "
    "Please try again in a moment."
)
RETRY_DELAY_SECONDS = 2.0


class LLMNode(BaseWorkflowNode):
    """
    Workflow Node executing provider-independent AI model inference.
    Orchestrates prompt construction and model invocation.
    """

    node_name: str = "LLMNode"
    node_type: NodeType = NodeType.LLM
    node_category: WorkflowNodeType = WorkflowNodeType.LLM
    node_description: str = "LLM inference workflow node."

    provider: Optional[Any] = None
    prompt_builder: Optional[Any] = None

    @staticmethod
    def _ride_context(state: ConversationState) -> Optional[str]:
        """Describes the trip being discussed right now so earlier trips in the chat are ignored."""
        ride = state.memory.extracted_entities.get("ride")
        if not isinstance(ride, dict) or ride.get("is_cancelled") or ride.get("is_booked"):
            return None

        def label(point_key: str, raw_key: str) -> Optional[str]:
            point = ride.get(point_key)
            point_label = point.get("label") if isinstance(point, dict) else None
            return point_label or ride.get(raw_key)

        pickup = label("pickup_point", "pickup_raw")
        destination = label("destination_point", "destination_raw")
        if not pickup or not destination:
            return None
        return (
            f"Pickup: {pickup}\nDestination: {destination}\n"
            "This is the ONLY trip the customer wants now. Do not mention or compare "
            "any earlier trips from this conversation. Reply in plain, complete sentences."
        )

    async def execute(
        self, state: ConversationState, context: Optional[NodeExecutionContext] = None
    ) -> ConversationState:
        """Asynchronously executes LLM generation turn on current conversation state."""
        if not state.conversation.current_message:
            return state

        provider = self.provider or AIProviderFactory.get_provider()
        prompt_builder = self.prompt_builder or PromptBuilder()

        user_text = state.conversation.current_message.get("content", "")
        history = state.conversation.history or []
        memories = state.memory.short_term_memory.get("memories", [])
        saved_locations = state.memory.short_term_memory.get("saved_locations", [])

        build_kwargs: dict[str, Any] = {}
        ride_context = self._ride_context(state)
        if ride_context:
            build_kwargs["ride_context"] = ride_context
        ai_request = prompt_builder.build(
            user_input=user_text,
            conversation_history=history,
            memories=memories,
            saved_locations=saved_locations,
            **build_kwargs,
        )

        try:
            try:
                ai_response = await provider.generate_response(ai_request)
            except (RateLimitException, ModelUnavailableException) as first_exc:
                # Rate limits and timeouts are usually brief: retry once.
                logger.warning("AI provider busy (%s); retrying once.", first_exc)
                await asyncio.sleep(RETRY_DELAY_SECONDS)
                ai_response = await provider.generate_response(ai_request)
        except Exception as exc:  # noqa: BLE001 - never fail silently
            logger.error("AI provider call failed: %s: %s", type(exc).__name__, exc)
            message = (
                AI_BUSY_MESSAGE
                if isinstance(exc, RateLimitException)
                else AI_UNAVAILABLE_MESSAGE
            )
            new_node_results = dict(state.execution.node_results)
            new_node_results[self.node_id] = {
                "content": message,
                "model_used": "unavailable",
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                "tool_calls": [],
                "error": type(exc).__name__,
            }
            return state.with_update(
                workflow_step=self.node_id,
                tool_calls=[],
                node_results=new_node_results,
            )

        tool_calls = [
            tc.model_dump() if hasattr(tc, "model_dump") else dict(tc)
            for tc in (ai_response.tool_calls or [])
        ]
        usage_data = (
            ai_response.usage.model_dump()
            if hasattr(ai_response.usage, "model_dump")
            else {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        )

        llm_payload = {
            "content": ai_response.content,
            "model_used": ai_response.model_used,
            "usage": usage_data,
            "tool_calls": tool_calls,
        }

        new_node_results = dict(state.execution.node_results)
        new_node_results[self.node_id] = llm_payload

        return state.with_update(
            workflow_step=self.node_id,
            tool_calls=tool_calls,
            node_results=new_node_results,
        )
