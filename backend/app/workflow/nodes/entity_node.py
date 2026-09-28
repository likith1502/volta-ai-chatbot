import logging
import uuid
from typing import Any, Optional

from app.ai.prompts.recommendation import (
    extract_ride_slots,
    is_cancellation_intent,
    is_knowledge_base_query,
    is_ride_intent,
)
from app.context.state import ConversationState
from app.context.types import NodeType
from app.schemas.cab import LocationPoint
from app.schemas.ride import RideEntityState, RideSlotStatus
from app.workflow.base import BaseWorkflowNode
from app.workflow.metadata import NodeExecutionContext
from app.workflow.node_types import WorkflowNodeType

logger = logging.getLogger("app.workflow.nodes.entity")


class RideEntityResolver:
    """Deterministic resolver extracting and resolving ride pickup and destination locations."""

    @staticmethod
    async def resolve_location_point(
        raw_str: Optional[str],
        saved_locations: list[Any],
        location_resolver: Optional[Any] = None,
        user_id: Optional[uuid.UUID] = None,
    ) -> Optional[LocationPoint]:
        """Resolves a raw text location against user saved locations without fabricating coordinates."""
        if not raw_str or not raw_str.strip():
            return None

        cleaned = raw_str.strip()
        cleaned_lower = cleaned.lower()

        # 1. Match against the user's active saved locations in memory
        for loc in saved_locations:
            lbl = getattr(loc, "label", None) or (
                loc.get("label") if isinstance(loc, dict) else ""
            )
            if lbl and lbl.strip().lower() == cleaned_lower:
                loc_id = getattr(loc, "id", None) or (
                    loc.get("id") if isinstance(loc, dict) else None
                )
                loc_addr = getattr(loc, "address", None) or (
                    loc.get("address") if isinstance(loc, dict) else cleaned
                )
                loc_lat = getattr(loc, "latitude", None) or (
                    loc.get("latitude") if isinstance(loc, dict) else None
                )
                loc_lon = getattr(loc, "longitude", None) or (
                    loc.get("longitude") if isinstance(loc, dict) else None
                )
                return LocationPoint(
                    saved_location_id=loc_id,
                    label=lbl,
                    address=loc_addr,
                    latitude=loc_lat,
                    longitude=loc_lon,
                )

        # 2. Match via domain LocationResolver if available and user_id is provided
        if location_resolver and user_id:
            try:
                saved = await location_resolver.resolve(user_id, cleaned)
                if saved:
                    return LocationPoint(
                        saved_location_id=saved.id,
                        label=saved.label,
                        address=saved.address,
                        latitude=saved.latitude,
                        longitude=saved.longitude,
                    )
            except Exception as res_err:
                logger.debug("LocationResolver resolution exception: %s", res_err)

        # 3. Fallback to unsaved text: no fabricated coordinates, saved_location_id is None
        return LocationPoint(
            label=cleaned,
            address=cleaned,
            saved_location_id=None,
            latitude=None,
            longitude=None,
        )

    @classmethod
    async def resolve_slots(
        cls,
        user_text: str,
        user_id: Optional[uuid.UUID],
        prior_state: Optional[RideEntityState],
        saved_locations: list[Any],
        location_resolver: Optional[Any] = None,
    ) -> RideEntityState:
        """Processes user input turn to update and resolve multi-turn ride state slots."""
        # 1. KB Queries never update ride slots
        if is_knowledge_base_query(user_text):
            return prior_state or RideEntityState(status=RideSlotStatus.NOT_REQUESTED)

        # 2. Cancellation check
        if is_cancellation_intent(user_text):
            return RideEntityState(
                status=RideSlotStatus.CANCELLED,
                is_cancelled=True,
                clarification_question="Your ride request has been cancelled. Let me know if there's anything else I can help you with!",
            )

        # 3. If prior request was completed or cancelled, check if a brand-new ride request is made
        active_prior = prior_state
        if prior_state and (prior_state.is_complete or prior_state.is_cancelled):
            if is_ride_intent(user_text, has_pending_request=False):
                active_prior = None
            else:
                return RideEntityState(status=RideSlotStatus.NOT_REQUESTED)

        pending_status = active_prior.status if active_prior else None

        # 4. Extract slots from the current turn
        pickup_raw, dest_raw, is_cancelled, is_override = extract_ride_slots(
            user_text, pending_status=pending_status
        )

        if is_cancelled:
            return RideEntityState(
                status=RideSlotStatus.CANCELLED,
                is_cancelled=True,
                clarification_question="Your ride request has been cancelled. Let me know if there's anything else I can help you with!",
            )

        # 5. Merge with prior slots
        if is_override:
            effective_pickup_raw = (
                pickup_raw
                if pickup_raw is not None
                else (active_prior.pickup_raw if active_prior else None)
            )
            effective_dest_raw = (
                dest_raw
                if dest_raw is not None
                else (active_prior.destination_raw if active_prior else None)
            )
        else:
            effective_pickup_raw = pickup_raw or (
                active_prior.pickup_raw if active_prior else None
            )
            effective_dest_raw = dest_raw or (
                active_prior.destination_raw if active_prior else None
            )

        # 6. Resolve structured LocationPoints
        pickup_point: Optional[LocationPoint] = None
        if effective_pickup_raw:
            if (
                active_prior
                and active_prior.pickup_point
                and active_prior.pickup_raw == effective_pickup_raw
            ):
                pickup_point = active_prior.pickup_point
            else:
                pickup_point = await cls.resolve_location_point(
                    effective_pickup_raw,
                    saved_locations=saved_locations,
                    location_resolver=location_resolver,
                    user_id=user_id,
                )

        destination_point: Optional[LocationPoint] = None
        if effective_dest_raw:
            if (
                active_prior
                and active_prior.destination_point
                and active_prior.destination_raw == effective_dest_raw
            ):
                destination_point = active_prior.destination_point
            else:
                destination_point = await cls.resolve_location_point(
                    effective_dest_raw,
                    saved_locations=saved_locations,
                    location_resolver=location_resolver,
                    user_id=user_id,
                )

        # 7. Validate Identical Locations
        if pickup_point and destination_point:
            is_same = False
            if (
                pickup_point.saved_location_id
                and destination_point.saved_location_id
                and pickup_point.saved_location_id
                == destination_point.saved_location_id
            ):
                is_same = True
            elif (
                pickup_point.label
                and destination_point.label
                and pickup_point.label.strip().lower()
                == destination_point.label.strip().lower()
            ):
                is_same = True
            elif (
                pickup_point.address
                and destination_point.address
                and pickup_point.address.strip().lower()
                == destination_point.address.strip().lower()
            ):
                is_same = True

            if is_same:
                lbl = pickup_point.label or effective_pickup_raw
                return RideEntityState(
                    pickup_raw=effective_pickup_raw,
                    destination_raw=None,
                    pickup_point=pickup_point,
                    destination_point=None,
                    status=RideSlotStatus.NEEDS_DESTINATION,
                    clarification_question=f"Pickup and destination cannot both be {lbl}. Where would you like to go from {lbl}?",
                )

        # 8. Determine final slot status and clarification question
        if pickup_point and destination_point:
            return RideEntityState(
                pickup_raw=effective_pickup_raw,
                destination_raw=effective_dest_raw,
                pickup_point=pickup_point,
                destination_point=destination_point,
                status=RideSlotStatus.RESOLVED,
                clarification_question=None,
            )
        elif pickup_point and not destination_point:
            lbl = pickup_point.label or effective_pickup_raw
            return RideEntityState(
                pickup_raw=effective_pickup_raw,
                destination_raw=None,
                pickup_point=pickup_point,
                destination_point=None,
                status=RideSlotStatus.NEEDS_DESTINATION,
                clarification_question=f"Where would you like to go from {lbl}?",
            )
        elif not pickup_point and destination_point:
            lbl = destination_point.label or effective_dest_raw
            return RideEntityState(
                pickup_raw=None,
                destination_raw=effective_dest_raw,
                pickup_point=None,
                destination_point=destination_point,
                status=RideSlotStatus.NEEDS_PICKUP,
                clarification_question=f"Where would you like to be picked up from to go to {lbl}?",
            )
        else:
            return RideEntityState(
                pickup_raw=None,
                destination_raw=None,
                pickup_point=None,
                destination_point=None,
                status=RideSlotStatus.NEEDS_BOTH,
                clarification_question="Where would you like to be picked up and where are you heading?",
            )


class EntityNode(BaseWorkflowNode):
    """Workflow Node extracting ride entities and resolving saved locations."""

    node_name: str = "EntityNode"
    node_type: NodeType = NodeType.GUARDRAIL
    node_category: WorkflowNodeType = WorkflowNodeType.ENTITY
    node_description: str = "Entity extraction and saved location resolution node."

    location_resolver: Optional[Any] = None

    async def execute(
        self, state: ConversationState, context: Optional[NodeExecutionContext] = None
    ) -> ConversationState:
        """Asynchronously extracts and resolves ride entities from state."""
        if not state.conversation.current_message:
            return state

        user_text = state.conversation.current_message.get("content", "")
        user_id_str = state.conversation.user_id
        user_uuid: Optional[uuid.UUID] = None
        if user_id_str:
            try:
                user_uuid = uuid.UUID(str(user_id_str))
            except (ValueError, TypeError):
                user_uuid = None

        prior_ride_dict = state.memory.extracted_entities.get("ride")
        prior_state = (
            RideEntityState.model_validate(prior_ride_dict) if prior_ride_dict else None
        )
        saved_locations = state.memory.short_term_memory.get("saved_locations", [])

        ride_state = await RideEntityResolver.resolve_slots(
            user_text=user_text,
            user_id=user_uuid,
            prior_state=prior_state,
            saved_locations=saved_locations,
            location_resolver=self.location_resolver,
        )

        new_entities = dict(state.memory.extracted_entities)
        new_entities["ride"] = ride_state.model_dump(mode="json")

        new_node_results = dict(state.execution.node_results)
        new_node_results[self.node_id] = new_entities["ride"]

        return state.with_update(
            workflow_step=self.node_id,
            extracted_entities=new_entities,
            node_results=new_node_results,
        )
