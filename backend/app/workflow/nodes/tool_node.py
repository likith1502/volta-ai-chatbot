from typing import Any, Optional

from app.ai.models import AIToolCall
from app.context.state import ConversationState
from app.context.types import NodeType
from app.workflow.base import BaseWorkflowNode
from app.workflow.metadata import NodeExecutionContext
from app.workflow.node_types import WorkflowNodeType


class ToolNode(BaseWorkflowNode):
    """Workflow Node for tool and external capability execution.

    Dispatches tool calls via AIToolDispatcher and registers results in state.
    Passes resolved pickup and destination locations to RecommendationTool.
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
        new_entities = dict(state.memory.extracted_entities)

        if self.tool_dispatcher:
            conv_id_str = str(state.conversation.conversation_id)
            user_id_str = str(state.conversation.user_id) if state.conversation.user_id else None
            ride_data = dict(state.memory.extracted_entities.get("ride") or {})

            if state.execution.tool_calls:
                for call in state.execution.tool_calls:
                    call_dict = dict(call)
                    args = dict(call_dict.get("arguments", {}))
                    args["conversation_id"] = conv_id_str
                    if user_id_str:
                        args["user_id"] = user_id_str

                    if "pickup" not in args and ride_data:
                        pickup_arg = ride_data.get("pickup_point") or ride_data.get(
                            "pickup_raw"
                        )
                        if pickup_arg:
                            args["pickup"] = pickup_arg

                    if "destination" not in args and ride_data:
                        dest_arg = ride_data.get("destination_point") or ride_data.get(
                            "destination_raw"
                        )
                        if dest_arg:
                            args["destination"] = dest_arg

                    tool_name = call_dict.get("tool_name", "recommendation")
                    tool_call_obj = AIToolCall(tool_name=tool_name, arguments=args)
                    tool_res = await self.tool_dispatcher.dispatch(tool_call_obj)
                    res_dict = {
                        "tool_name": tool_name,
                        "success": tool_res.success,
                        "data": tool_res.data,
                    }
                    executed_results.append(res_dict)
                    if (
                        tool_res.success
                        and tool_res.data
                        and "recommendation_id" in tool_res.data
                    ):
                        recommendation_id = str(tool_res.data["recommendation_id"])

            elif state.memory.detected_intent and state.memory.detected_intent.get(
                "requires_recommendation"
            ):
                user_query = (
                    state.conversation.current_message.get("content", "")
                    if state.conversation.current_message
                    else ""
                )
                pickup_val = (
                    ride_data.get("pickup_point")
                    or ride_data.get("pickup_raw")
                    or user_query
                )
                dest_val = (
                    ride_data.get("destination_point")
                    or ride_data.get("destination_raw")
                    or "Destination"
                )

                tool_call_obj = AIToolCall(
                    tool_name="recommendation",
                    arguments={
                        "conversation_id": conv_id_str,
                        "user_query": user_query,
                        "pickup": pickup_val,
                        "destination": dest_val,
                    },
                )
                tool_res = await self.tool_dispatcher.dispatch(tool_call_obj)
                res_dict = {
                    "tool_name": "recommendation",
                    "success": tool_res.success,
                    "data": tool_res.data,
                }
                executed_results.append(res_dict)
                if (
                    tool_res.success
                    and tool_res.data
                    and "recommendation_id" in tool_res.data
                ):
                    recommendation_id = str(tool_res.data["recommendation_id"])
                    ride_data["recommendation_id"] = recommendation_id
                    ride_data["available_options"] = tool_res.data.get("options", [])
                    # Clear stale selection and booking state to enforce fresh tier choice
                    ride_data["selected_tier"] = None
                    ride_data["selected_fare"] = None
                    ride_data["selected_display_name"] = None
                    ride_data["booking_id"] = None
                    ride_data["booking_reference"] = None
                    ride_data["booking_status"] = None
                    ride_data["is_booked"] = False
                    ride_data["booking_error"] = None
                    new_entities["ride"] = ride_data

            elif state.memory.detected_intent and state.memory.detected_intent.get(
                "requires_booking"
            ):
                tool_call_obj = AIToolCall(
                    tool_name="booking",
                    arguments={
                        "conversation_id": conv_id_str,
                        "user_id": user_id_str,
                        "recommendation_id": ride_data.get("recommendation_id"),
                        "selected_tier": ride_data.get("selected_tier"),
                    },
                )
                tool_res = await self.tool_dispatcher.dispatch(tool_call_obj)
                res_dict = {
                    "tool_name": "booking",
                    "success": tool_res.success,
                    "data": tool_res.data,
                    "error": tool_res.error,
                }
                executed_results.append(res_dict)
                if tool_res.success and tool_res.data:
                    ride_data["booking_id"] = tool_res.data.get("booking_id")
                    ride_data["booking_reference"] = tool_res.data.get(
                        "booking_reference"
                    )
                    ride_data["booking_status"] = tool_res.data.get(
                        "booking_status", "confirmed"
                    )
                    ride_data["is_booked"] = True
                    ride_data["status"] = "booked"
                    new_entities["ride"] = ride_data
                elif not tool_res.success:
                    ride_data["booking_error"] = tool_res.error
                    new_entities["ride"] = ride_data

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
            extracted_entities=new_entities,
        )
