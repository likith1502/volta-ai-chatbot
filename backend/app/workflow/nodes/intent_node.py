import logging
import re
import uuid
from decimal import Decimal
from typing import Any, Optional


from app.ai.prompts.recommendation import (
    extract_vehicle_tier,
    is_ambiguous_booking_intent,
    is_booking_confirmation,
    is_cancellation_intent,
    is_knowledge_base_query,
    is_ride_intent,
)
from app.context.state import ConversationState
from app.context.types import NodeType
from app.schemas.ride import RideEntityState, RideSlotStatus
from app.workflow.base import BaseWorkflowNode
from app.workflow.metadata import NodeExecutionContext
from app.workflow.node_types import WorkflowNodeType
from app.workflow.nodes.entity_node import RideEntityResolver

logger = logging.getLogger("app.workflow.nodes.intent")


class IntentNode(BaseWorkflowNode):
    """Workflow Node for conversational intent classification, slot resolution, and booking confirmation.

    Identifies ride recommendation vs booking vs general conversation intent, resolves location
    slots across conversation turns, and determines readiness for cab pricing quotes or bookings.
    """

    node_name: str = "IntentNode"
    node_type: NodeType = NodeType.GUARDRAIL
    node_category: WorkflowNodeType = WorkflowNodeType.INTENT
    node_description: str = (
        "Intent classification and ride slot evaluation workflow node."
    )

    location_resolver: Optional[Any] = None

    async def execute(
        self, state: ConversationState, context: Optional[NodeExecutionContext] = None
    ) -> ConversationState:
        """Asynchronously classifies intent and resolves ride slots from conversational state."""
        if not state.conversation.current_message:
            return state

        user_text = state.conversation.current_message.get("content", "")
        new_entities = dict(state.memory.extracted_entities)
        new_node_results = dict(state.execution.node_results)

        # 1. Knowledge Base Queries route directly to conversation
        if is_knowledge_base_query(user_text):
            intent_payload = {
                "intent": "conversation",
                "confidence": 0.95,
                "requires_recommendation": False,
                "requires_booking": False,
            }
            new_node_results[self.node_id] = intent_payload
            return state.with_update(
                workflow_step=self.node_id,
                detected_intent=intent_payload,
                node_results=new_node_results,
            )

        # Retrieve prior ride state if present
        prior_ride_dict = state.memory.extracted_entities.get("ride")
        prior_ride = (
            RideEntityState.model_validate(prior_ride_dict) if prior_ride_dict else None
        )
        has_pending = bool(
            prior_ride
            and prior_ride.needs_clarification
            and not prior_ride.is_cancelled
        )

        user_id_str = state.conversation.user_id
        user_uuid: Optional[uuid.UUID] = None
        if user_id_str:
            try:
                user_uuid = uuid.UUID(str(user_id_str))
            except (ValueError, TypeError):
                user_uuid = None

        saved_locations = state.memory.short_term_memory.get("saved_locations", [])

        # 2. Check for ride cancellation
        if is_cancellation_intent(user_text):
            ride_state = await RideEntityResolver.resolve_slots(
                user_text=user_text,
                user_id=user_uuid,
                prior_state=prior_ride,
                saved_locations=saved_locations,
                location_resolver=self.location_resolver,
            )
            new_entities["ride"] = ride_state.model_dump(mode="json")
            intent_payload = {
                "intent": "ride_recommendation",
                "confidence": 0.95,
                "requires_recommendation": False,
                "requires_booking": False,
                "ride_status": ride_state.status.value,
            }
            new_node_results[self.node_id] = intent_payload
            return state.with_update(
                workflow_step=self.node_id,
                detected_intent=intent_payload,
                extracted_entities=new_entities,
                node_results=new_node_results,
            )

        # 3. Check if an active quote exists for vehicle selection or booking confirmation
        has_active_quote = bool(
            prior_ride
            and prior_ride.recommendation_id
            and prior_ride.status in (RideSlotStatus.RESOLVED, RideSlotStatus.AWAITING_CONFIRMATION)
            and not prior_ride.is_cancelled
            and not prior_ride.is_booked
        )

        # If a user explicitly specifies new pickup and destination (e.g., 'From A to B'),
        # or changes pickup/destination, it overrides the active quote and starts a new ride search.
        is_explicit_new_ride = bool(
            re.search(r"\bfrom\s+.+\s+to\s+.+\b", user_text, re.IGNORECASE)
            or re.search(r"\bto\s+.+\s+from\s+.+\b", user_text, re.IGNORECASE)
            or re.search(
                r"\b(?:change|update|make|switch)\s+(?:my\s+)?(?:pickup|destination|dropoff|route)\b",
                user_text,
                re.IGNORECASE,
            )
            or re.search(
                r"\b(?:pick\s+me\s+up\s+at|drop\s+me\s+off\s+at)\b",
                user_text,
                re.IGNORECASE,
            )
        )

        if has_active_quote and not is_explicit_new_ride:
            # 3A. Explicit Booking Confirmation
            if is_booking_confirmation(user_text):
                if prior_ride.selected_tier:
                    # User confirmed selected tier -> trigger BookingTool
                    intent_payload = {
                        "intent": "ride_booking",
                        "confidence": 0.95,
                        "requires_booking": True,
                        "requires_recommendation": False,
                        "ride_status": prior_ride.status.value,
                    }
                    new_node_results[self.node_id] = intent_payload
                    return state.with_update(
                        workflow_step=self.node_id,
                        detected_intent=intent_payload,
                        node_results=new_node_results,
                    )
                else:
                    # User confirmed without selecting a tier -> prompt for tier
                    opts_text = ", ".join(
                        [
                            f"{o.get('display_name', o.get('tier'))} ({o.get('currency', 'INR')} {o.get('fare')})"
                            for o in prior_ride.available_options
                        ]
                    )
                    prior_ride.clarification_question = (
                        f"Which vehicle option would you like to book? Please choose from the available options: {opts_text}."
                    )
                    new_entities["ride"] = prior_ride.model_dump(mode="json")
                    intent_payload = {
                        "intent": "ride_recommendation",
                        "confidence": 0.95,
                        "requires_booking": False,
                        "requires_recommendation": False,
                        "ride_status": prior_ride.status.value,
                    }
                    new_node_results[self.node_id] = intent_payload
                    return state.with_update(
                        workflow_step=self.node_id,
                        detected_intent=intent_payload,
                        extracted_entities=new_entities,
                        node_results=new_node_results,
                    )

            # 3B. Vehicle Tier Selection
            tier = extract_vehicle_tier(user_text)
            if tier:
                matching_opt = None
                for opt in prior_ride.available_options:
                    if opt.get("tier", "").lower() == tier.lower():
                        matching_opt = opt
                        break

                if matching_opt:
                    opt_name = matching_opt.get("display_name", tier.capitalize())
                    opt_fare = matching_opt.get("fare")
                    currency = matching_opt.get("currency", "INR")
                    pickup_lbl = (
                        prior_ride.pickup_point.label
                        if prior_ride.pickup_point
                        else prior_ride.pickup_raw
                    ) or "your pickup"
                    dest_lbl = (
                        prior_ride.destination_point.label
                        if prior_ride.destination_point
                        else prior_ride.destination_raw
                    ) or "your destination"

                    prior_ride.selected_tier = tier
                    prior_ride.selected_fare = Decimal(str(opt_fare)) if opt_fare is not None else None
                    prior_ride.selected_display_name = opt_name
                    prior_ride.status = RideSlotStatus.AWAITING_CONFIRMATION
                    prior_ride.clarification_question = (
                        f"You have selected {opt_name} with a quoted fare of {currency} {opt_fare} from {pickup_lbl} to {dest_lbl}. "
                        "Would you like to confirm this booking? (Please reply 'Confirm' or 'Yes, confirm')"
                    )
                    new_entities["ride"] = prior_ride.model_dump(mode="json")
                    intent_payload = {
                        "intent": "ride_selection",
                        "confidence": 0.95,
                        "requires_booking": False,
                        "requires_recommendation": False,
                        "ride_status": prior_ride.status.value,
                    }
                    new_node_results[self.node_id] = intent_payload
                    return state.with_update(
                        workflow_step=self.node_id,
                        detected_intent=intent_payload,
                        extracted_entities=new_entities,
                        node_results=new_node_results,
                    )
                else:
                    opts_text = ", ".join(
                        [
                            o.get("display_name", o.get("tier"))
                            for o in prior_ride.available_options
                        ]
                    )
                    prior_ride.clarification_question = (
                        f"{tier.capitalize()} is not available for this route. "
                        f"Please choose from the available options: {opts_text}."
                    )
                    new_entities["ride"] = prior_ride.model_dump(mode="json")
                    intent_payload = {
                        "intent": "ride_recommendation",
                        "confidence": 0.95,
                        "requires_booking": False,
                        "requires_recommendation": False,
                        "ride_status": prior_ride.status.value,
                    }
                    new_node_results[self.node_id] = intent_payload
                    return state.with_update(
                        workflow_step=self.node_id,
                        detected_intent=intent_payload,
                        extracted_entities=new_entities,
                        node_results=new_node_results,
                    )

            # Check if user explicitly requested an unquoted vehicle tier (e.g. 'helicopter', 'luxury', 'bike', 'auto')
            unsupported_m = re.search(
                r"\b(?:book|want|need|choose|take|get)\s+(?:the\s+|a\s+|an\s+)?([a-zA-Z]+)\b",
                user_text,
                re.IGNORECASE,
            )
            if unsupported_m:
                requested_word = unsupported_m.group(1).lower()
                if requested_word not in ("a", "an", "the", "it", "cab", "ride", "car"):
                    opts_text = ", ".join(
                        [
                            o.get("display_name", o.get("tier"))
                            for o in prior_ride.available_options
                        ]
                    )
                    prior_ride.clarification_question = (
                        f"'{requested_word.capitalize()}' is not available for this route. "
                        f"Please choose from the available options: {opts_text}."
                    )
                    new_entities["ride"] = prior_ride.model_dump(mode="json")
                    intent_payload = {
                        "intent": "ride_recommendation",
                        "confidence": 0.95,
                        "requires_booking": False,
                        "requires_recommendation": False,
                        "ride_status": prior_ride.status.value,
                    }
                    new_node_results[self.node_id] = intent_payload
                    return state.with_update(
                        workflow_step=self.node_id,
                        detected_intent=intent_payload,
                        extracted_entities=new_entities,
                        node_results=new_node_results,
                    )

            # 3C. Ambiguous Booking Intent without Tier
            if is_ambiguous_booking_intent(user_text):
                opts_text = ", ".join(
                    [
                        f"{o.get('display_name', o.get('tier'))} ({o.get('currency', 'INR')} {o.get('fare')})"
                        for o in prior_ride.available_options
                    ]
                )
                prior_ride.clarification_question = (
                    f"Which vehicle option would you like to book? Please choose from the available options: {opts_text}."
                )
                new_entities["ride"] = prior_ride.model_dump(mode="json")
                intent_payload = {
                    "intent": "ride_recommendation",
                    "confidence": 0.95,
                    "requires_booking": False,
                    "requires_recommendation": False,
                    "ride_status": prior_ride.status.value,
                }
                new_node_results[self.node_id] = intent_payload
                return state.with_update(
                    workflow_step=self.node_id,
                    detected_intent=intent_payload,
                    extracted_entities=new_entities,
                    node_results=new_node_results,
                )

        # 4. Check for ride intent (explicit or multi-turn continuation)
        is_ride = (
            is_ride_intent(user_text, has_pending_request=has_pending)
            or is_explicit_new_ride
        )

        if is_ride or has_pending:
            ride_state = await RideEntityResolver.resolve_slots(
                user_text=user_text,
                user_id=user_uuid,
                prior_state=prior_ride,
                saved_locations=saved_locations,
                location_resolver=self.location_resolver,
            )
            new_entities["ride"] = ride_state.model_dump(mode="json")
            requires_rec = ride_state.status == RideSlotStatus.RESOLVED

            intent_payload = {
                "intent": "ride_recommendation",
                "confidence": 0.95,
                "requires_recommendation": requires_rec,
                "requires_booking": False,
                "ride_status": ride_state.status.value,
            }
            new_node_results[self.node_id] = intent_payload
            return state.with_update(
                workflow_step=self.node_id,
                detected_intent=intent_payload,
                extracted_entities=new_entities,
                node_results=new_node_results,
            )

        # 5. Default: General conversation
        intent_payload = {
            "intent": "conversation",
            "confidence": 0.90,
            "requires_recommendation": False,
            "requires_booking": False,
        }
        new_node_results[self.node_id] = intent_payload
        return state.with_update(
            workflow_step=self.node_id,
            detected_intent=intent_payload,
            node_results=new_node_results,
        )

