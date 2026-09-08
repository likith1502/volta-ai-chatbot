from typing import Any, Optional

from app.ai.models import AIToolCall
from app.context.state import ConversationState
from app.context.types import NodeType
from app.workflow.base import BaseWorkflowNode
from app.workflow.metadata import NodeExecutionContext
from app.workflow.node_types import WorkflowNodeType


class ToolNode(BaseWorkflowNode):
    """
    Workflow Node for tool and external capability execution.
    Dispatches tool calls via AIToolDispatcher and registers results in state.
    """

    node_name: str = "ToolNode"
    node_type: NodeType = NodeType.TOOL
    node_category: WorkflowNodeType = WorkflowNodeType.TOOL
    node_description: str = "Tool execution workflow node."

    tool_dispatcher: Optional[Any] = None

    async def execute(
        self, state: ConversationState, context: Optional[NodeExecutionContext] = None
    ) -> ConversationState:
        """Asynchronously executes requested tools or intent-driven recommendations."""
        if not state.conversation.current_message and not state.execution.tool_calls:
            return state

        recommendation_id: Optional[str] = None
        executed_results: list[dict[str, Any]] = []

        if self.tool_dispatcher:
            conv_id_str = str(state.conversation.conversation_id)

            if state.execution.tool_calls:
                for call in state.execution.tool_calls:
                    call_dict = dict(call)
                    args = dict(call_dict.get("arguments", {}))
                    args["conversation_id"] = conv_id_str
                    tool_name = call_dict.get("tool_name", "recommendation")
                    tool_call_obj = AIToolCall(tool_name=tool_name, arguments=args)
                    tool_res = await self.tool_dispatcher.dispatch(tool_call_obj)
                    res_dict = {
                        "tool_name": tool_name,
                        "success": tool_res.success,
                        "data": tool_res.data,
                    }
                    executed_results.append(res_dict)
                    if tool_res.success and tool_res.data and "recommendation_id" in tool_res.data:
                        recommendation_id = str(tool_res.data["recommendation_id"])
            elif state.memory.detected_intent and state.memory.detected_intent.get("requires_recommendation"):
                user_query = (
                    state.conversation.current_message.get("content", "")
                    if state.conversation.current_message
                    else ""
                )
                tool_call_obj = AIToolCall(
                    tool_name="recommendation",
                    arguments={"conversation_id": conv_id_str, "user_query": user_query},
                )
                tool_res = await self.tool_dispatcher.dispatch(tool_call_obj)
                res_dict = {
                    "tool_name": "recommendation",
                    "success": tool_res.success,
                    "data": tool_res.data,
                }
                executed_results.append(res_dict)
                if tool_res.success and tool_res.data and "recommendation_id" in tool_res.data:
                    recommendation_id = str(tool_res.data["recommendation_id"])

        tool_payload = {
            "executed": bool(executed_results),
            "recommendation_id": recommendation_id,
            "results": executed_results,
        }

        new_node_results = dict(state.execution.node_results)
        new_node_results[self.node_id] = tool_payload

        return state.with_update(
            workflow_step=self.node_id,
            tool_results=executed_results,
            node_results=new_node_results,
        )
