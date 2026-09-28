import logging
import uuid
from typing import Any, Optional

from app.ai.prompts.recommendation import (
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
    """Workflow Node for conversational intent classification and slot resolution.

    Identifies ride recommendation vs general conversation intent, resolves location
    slots across conversation turns, and determines readiness for cab pricing quotes.
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
                "ride_status": ride_state.status.value,
            }
            new_node_results[self.node_id] = intent_payload
            return state.with_update(
                workflow_step=self.node_id,
                detected_intent=intent_payload,
                extracted_entities=new_entities,
                node_results=new_node_results,
            )

        # 3. Check for ride intent (explicit or multi-turn continuation)
        is_ride = is_ride_intent(user_text, has_pending_request=has_pending)

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
                "ride_status": ride_state.status.value,
            }
            new_node_results[self.node_id] = intent_payload
            return state.with_update(
                workflow_step=self.node_id,
                detected_intent=intent_payload,
                extracted_entities=new_entities,
                node_results=new_node_results,
            )

        # 4. Default: General conversation
        intent_payload = {
            "intent": "conversation",
            "confidence": 0.90,
            "requires_recommendation": False,
        }
        new_node_results[self.node_id] = intent_payload
        return state.with_update(
            workflow_step=self.node_id,
            detected_intent=intent_payload,
            node_results=new_node_results,
        )
