import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.api.dependencies.services import get_saved_location_service
from app.schemas.common import ResponseEnvelope
from app.schemas.saved_location import (
    SavedLocationCreate,
    SavedLocationResponse,
    SavedLocationUpdate,
)
from app.services.saved_location import SavedLocationService
from app.utils.responses import success_response

router = APIRouter(prefix="/users/{user_id}/saved-locations", tags=["Saved Locations"])


def verify_user_access(
    user_id: uuid.UUID,
    x_user_id: Optional[uuid.UUID] = Header(None, alias="X-User-ID"),
) -> None:
    """Validates user authorization.

    If the client or gateway provides an authenticated caller identity header (X-User-ID),
    it must strictly match the target path user_id to prevent cross-user resource access.
    """
    if x_user_id is not None and x_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Not authorized to access or modify another user's saved locations.",
        )


@router.post(
    "",
    response_model=ResponseEnvelope[SavedLocationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Saved Location",
    description="Registers a new persistent landmark location (e.g. Home, Work) for a user.",
)
async def create_saved_location(
    user_id: uuid.UUID,
    payload: SavedLocationCreate,
    service: SavedLocationService = Depends(get_saved_location_service),
    _: None = Depends(verify_user_access),
):
    saved_loc = await service.create_saved_location(
        user_id=user_id,
        label=payload.label,
        address=payload.address,
        latitude=payload.latitude,
        longitude=payload.longitude,
    )
    return success_response(
        data=SavedLocationResponse.model_validate(saved_loc),
        message="Saved location created successfully.",
    )


@router.get(
    "",
    response_model=ResponseEnvelope[list[SavedLocationResponse]],
    summary="List Saved Locations",
    description="Retrieves all active saved landmark locations for the specified user.",
)
async def list_saved_locations(
    user_id: uuid.UUID,
    service: SavedLocationService = Depends(get_saved_location_service),
    _: None = Depends(verify_user_access),
):
    locations = await service.list_saved_locations(user_id=user_id)
    return success_response(
        data=[SavedLocationResponse.model_validate(loc) for loc in locations],
        message="Saved locations retrieved successfully.",
    )


@router.get(
    "/{location_id}",
    response_model=ResponseEnvelope[SavedLocationResponse],
    summary="Get Saved Location By ID",
    description="Retrieves a specific saved location record scoped to the owning user.",
)
async def get_saved_location(
    user_id: uuid.UUID,
    location_id: uuid.UUID,
    service: SavedLocationService = Depends(get_saved_location_service),
    _: None = Depends(verify_user_access),
):
    loc = await service.get_saved_location(user_id=user_id, location_id=location_id)
    return success_response(
        data=SavedLocationResponse.model_validate(loc),
        message="Saved location retrieved successfully.",
    )


@router.put(
    "/{location_id}",
    response_model=ResponseEnvelope[SavedLocationResponse],
    summary="Update Saved Location",
    description="Updates label, address, or coordinates of an existing user saved location.",
)
async def update_saved_location(
    user_id: uuid.UUID,
    location_id: uuid.UUID,
    payload: SavedLocationUpdate,
    service: SavedLocationService = Depends(get_saved_location_service),
    _: None = Depends(verify_user_access),
):
    update_dict = payload.model_dump(exclude_unset=True)
    loc = await service.update_saved_location(
        user_id=user_id,
        location_id=location_id,
        update_data=update_dict,
    )
    return success_response(
        data=SavedLocationResponse.model_validate(loc),
        message="Saved location updated successfully.",
    )


@router.delete(
    "/{location_id}",
    response_model=ResponseEnvelope[dict[str, Any]],
    summary="Delete Saved Location",
    description="Soft-deletes an active saved location for a user.",
)
async def delete_saved_location(
    user_id: uuid.UUID,
    location_id: uuid.UUID,
    service: SavedLocationService = Depends(get_saved_location_service),
    _: None = Depends(verify_user_access),
):
    await service.delete_saved_location(user_id=user_id, location_id=location_id)
    return success_response(
        data={"location_id": str(location_id), "deleted": True},
        message="Saved location deleted successfully.",
    )
