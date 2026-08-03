import uuid

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_user_service
from app.schemas.common import ResponseEnvelope
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user import UserService
from app.utils.responses import success_response

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    response_model=ResponseEnvelope[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create User Account",
    description="Registers a new user account in the Volta platform.",
)
async def create_user(
    payload: UserCreate,
    service: UserService = Depends(get_user_service),
):
    user = await service.create_user(
        full_name=payload.full_name,
        email=payload.email,
        phone_number=payload.phone_number,
        preferred_language=payload.preferred_language,
    )
    return success_response(
        data=UserResponse.model_validate(user),
        message="User account created successfully.",
    )


@router.get(
    "/{user_id}",
    response_model=ResponseEnvelope[UserResponse],
    summary="Get User By ID",
    description="Retrieves a user profile by primary key UUID.",
)
async def get_user(
    user_id: uuid.UUID,
    service: UserService = Depends(get_user_service),
):
    user = await service.get_user_by_id(user_id)
    return success_response(
        data=UserResponse.model_validate(user),
        message="User profile retrieved successfully.",
    )


@router.put(
    "/{user_id}",
    response_model=ResponseEnvelope[UserResponse],
    summary="Update User Profile",
    description="Updates attributes of an existing user profile.",
)
async def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    service: UserService = Depends(get_user_service),
):
    update_data = payload.model_dump(exclude_unset=True)
    user = await service.update_profile(user_id, update_data)
    return success_response(
        data=UserResponse.model_validate(user),
        message="User profile updated successfully.",
    )


@router.delete(
    "/{user_id}",
    response_model=ResponseEnvelope[dict],
    summary="Deactivate User Account",
    description="Deactivates (soft-deletes) a user account.",
)
async def deactivate_user(
    user_id: uuid.UUID,
    service: UserService = Depends(get_user_service),
):
    await service.deactivate_user(user_id)
    return success_response(
        data={"user_id": str(user_id), "deactivated": True},
        message="User account deactivated successfully.",
    )
