from typing import Optional

from app.ai.prompts.recommendation import is_cancellation_intent
from app.ai.prompts.human_text import (
    extract_quoted_fares,
    format_inr,
    place_name,
    vehicle_name,
)
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

        # Show the booking confirmation only on the turn the customer actually
        # confirmed (or repeated a confirmation). On later turns the old
        # booking stays in memory, but the reply must answer the new message.
        intent_result = state.execution.node_results.get("intent") or {}
        booking_this_turn = (
            intent_result.get("intent") == "ride_booking"
            or bool(tool_data.get("booking_reference"))
            or any(
                isinstance(r, dict) and isinstance(r.get("data"), dict)
                and r["data"].get("booking_reference")
                for r in (tool_data.get("results") or [])
            )
        )
        # A ride booked on an earlier turn must not leak into later replies
        # (old booking details, or a stale "Shall I book it?" question).
        current_text = (state.conversation.current_message or {}).get("content", "")
        cancelled_this_turn = is_cancellation_intent(current_text)
        ride_already_done = bool(
            ride_data
            and (
                (
                    (ride_data.get("is_booked") or ride_data.get("booking_reference"))
                    and not booking_this_turn
                )
                or (ride_data.get("is_cancelled") and not cancelled_this_turn)
            )
        )
        if ride_data and not ride_already_done:
            if ride_data.get("is_cancelled"):
                content = (
                    ride_data.get("clarification_question")
                    or "Your ride request has been cancelled. Let me know if there's anything else I can help you with!"
                )
            elif (ride_data.get("is_booked") or ride_data.get("booking_reference")) and booking_this_turn:
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
                        f"\n- Route: {place_name(pickup_lbl, 'Pickup')} → {place_name(dest_lbl, 'Destination')}"
                        if has_route
                        else ""
                    )
                    content = (
                        "Good news, this ride is already booked, so I haven't made a second booking.\n"
                        f"- Booking reference: **{ref}**\n"
                        f"- Status: {b_status}"
                        f"{route_line}"
                    )
                else:
                    raw_tier = (
                        ride_data.get("selected_display_name")
                        or (ride_data.get("selected_tier", "Ride").capitalize())
                    )
                    tier_str = vehicle_name(raw_tier)
                    fare_val = ride_data.get("selected_fare")
                    fare_line = f"\n- Fare: about {format_inr(fare_val)}" if fare_val else ""
                    content = (
                        f"Done! Your {tier_str} is booked. 🎉\n"
                        f"- Booking reference: **{ref}**\n"
                        f"- Route: {place_name(pickup_lbl, 'Pickup')} → {place_name(dest_lbl, 'Destination')}"
                        f"{fare_line}\n"
                        f"- Status: {b_status}\n\n"
                        "You'll get a notification in the app with your booking details. Have a safe trip!"
                    )
            elif ride_data.get("booking_error"):
                content = (
                    "Sorry, I couldn't complete that booking just now. "
                    "Please tell me your pickup and drop again and I'll get you fresh prices."
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
                            lines = ["Here are the cars available for your trip:"]
                            for opt in options:
                                name = opt.get("display_name", opt.get("tier", "Ride"))
                                fare = opt.get("fare")
                                eta = opt.get("eta_minutes")
                                lines.append(
                                    f"- **{vehicle_name(name)}**: {format_inr(fare)} (arrives in about {eta} min)"
                                )
                            formatted_opts = "\n".join(lines)
                            if content in (
                                "I am here to assist you.",
                                "I can help with that.",
                                "I can assist you with your ride.",
                                "",
                            ):
                                content = formatted_opts

        # Keep prices consistent: when Gemini presented the ride options with
        # its own fare estimates, store those fares in the quote so the
        # selection, confirmation and booking all use what the customer saw.
        fare_overrides: dict[str, str] = {}
        new_entities = None
        if (
            ride_data
            and ride_data.get("status") == "resolved"
            and not ride_data.get("selected_tier")
            and ride_data.get("available_options")
            and model_used != "unavailable"
            and content == llm_data.get("content")
        ):
            fare_overrides = extract_quoted_fares(content, ride_data["available_options"])
            if fare_overrides:
                updated_ride = dict(ride_data)
                updated_ride["available_options"] = [
                    {**opt, "fare": fare_overrides.get(str(opt.get("tier", "")).lower(), opt.get("fare"))}
                    for opt in ride_data["available_options"]
                ]
                new_entities = dict(state.memory.extracted_entities)
                new_entities["ride"] = updated_ride

        response_payload = {
            "fare_overrides": fare_overrides,
            "content": content,
            "model_used": model_used,
            "usage": usage,
            "total_tokens": total_tokens,
            "recommendation_id": recommendation_id,
        }

        new_node_results = dict(state.execution.node_results)
        new_node_results[self.node_id] = response_payload

        if new_entities is not None:
            return state.with_update(
                workflow_step=self.node_id,
                node_results=new_node_results,
                extracted_entities=new_entities,
            )
        return state.with_update(
            workflow_step=self.node_id,
            node_results=new_node_results,
        )
