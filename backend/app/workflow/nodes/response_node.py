from typing import Optional

from app.context.state import ConversationState
from app.context.types import NodeType
from app.workflow.base import BaseWorkflowNode
from app.workflow.metadata import NodeExecutionContext
from app.workflow.node_types import WorkflowNodeType


class ResponseNode(BaseWorkflowNode):
    """Workflow Node consolidating execution outputs into final turn response payload.

    Extracts AI inference results, tool recommendations, slot clarification prompts,
    and token metrics.
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

        # Check ride entity state to present clarification prompts, quotes, or booking confirmations
        ride_data = state.memory.extracted_entities.get("ride")
        if ride_data:
            if ride_data.get("is_cancelled"):
                content = (
                    ride_data.get("clarification_question")
                    or "Your ride request has been cancelled. Let me know if there's anything else I can help you with!"
                )
            elif ride_data.get("is_booked") or ride_data.get("booking_reference"):
                ref = ride_data.get("booking_reference")
                b_status = ride_data.get("booking_status", "confirmed").capitalize()
                pickup_lbl = (
                    ride_data.get("pickup_point", {}).get("label")
                    if isinstance(ride_data.get("pickup_point"), dict)
                    else getattr(ride_data.get("pickup_point"), "label", None)
                ) or ride_data.get("pickup_raw", "Pickup")
                dest_lbl = (
                    ride_data.get("destination_point", {}).get("label")
                    if isinstance(ride_data.get("destination_point"), dict)
                    else getattr(ride_data.get("destination_point"), "label", None)
                ) or ride_data.get("destination_raw", "Destination")

                if ride_data.get("is_duplicate_replay"):
                    has_route = bool(
                        pickup_lbl
                        and dest_lbl
                        and pickup_lbl != "Pickup"
                        and dest_lbl != "Destination"
                    )
                    route_line = (
                        f"\n- Route: {pickup_lbl} to {dest_lbl}"
                        if has_route
                        else ""
                    )
                    content = (
                        "This ride has already been confirmed.\n"
                        f"- Booking Reference: {ref}\n"
                        f"- Status: {b_status}"
                        f"{route_line}\n\n"
                        "Your existing booking remains confirmed in the VOLTA system."
                    )
                else:
                    raw_tier = (
                        ride_data.get("selected_display_name")
                        or (ride_data.get("selected_tier", "Ride").capitalize())
                    )
                    tier_str = raw_tier if raw_tier.lower().startswith("volta") else f"Volta {raw_tier}"
                    fare_val = ride_data.get("selected_fare")
                    fare_line = f"\n- Quoted Fare: INR {fare_val}" if fare_val else ""
                    content = (
                        f"Your {tier_str} ride has been successfully booked!\n"
                        f"- Booking Reference: {ref}\n"
                        f"- Status: {b_status}\n"
                        f"- Vehicle Tier: {tier_str}"
                        f"{fare_line}\n"
                        f"- Route: {pickup_lbl} to {dest_lbl}\n\n"
                        "Your booking is confirmed in the VOLTA system. A notification has been sent to your account."
                    )
            elif ride_data.get("booking_error"):
                content = (
                    f"We were unable to confirm your booking: {ride_data['booking_error']}. "
                    "Please try again or request a new quote."
                )
            elif ride_data.get("clarification_question"):
                content = ride_data["clarification_question"]
            elif ride_data.get("status") == "resolved":
                # If tool executed and LLM output is generic placeholder, format options clearly
                if tool_data.get("results"):
                    for res in tool_data["results"]:
                        data = res.get("data")
                        if data and "options" in data:
                            options = data["options"]
                            currency = data.get("currency", "INR")
                            lines = ["Here are the available ride options:"]
                            for opt in options:
                                name = opt.get("display_name", opt.get("tier", "Ride"))
                                fare = opt.get("fare")
                                eta = opt.get("eta_minutes")
                                lines.append(
                                    f"- {name}: {currency} {fare} (ETA: {eta} mins)"
                                )
                            formatted_opts = "\n".join(lines)
                            if content in (
                                "I am here to assist you.",
                                "I can help with that.",
                                "I can assist you with your ride.",
                                "",
                            ):
                                content = formatted_opts

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
