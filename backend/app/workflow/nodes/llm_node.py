from typing import Any, Optional

from app.ai.factory import AIProviderFactory
from app.ai.prompts.prompt_builder import PromptBuilder
from app.context.state import ConversationState
from app.context.types import NodeType
from app.workflow.base import BaseWorkflowNode
from app.workflow.metadata import NodeExecutionContext
from app.workflow.node_types import WorkflowNodeType


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

        ai_request = prompt_builder.build(
            user_input=user_text,
            conversation_history=history,
            memories=memories,
        )

        ai_response = await provider.generate_response(ai_request)

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
