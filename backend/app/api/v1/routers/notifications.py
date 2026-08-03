import uuid

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_notification_service
from app.schemas.common import ResponseEnvelope
from app.schemas.notification import NotificationCreate, NotificationResponse
from app.services.notification import NotificationService
from app.utils.responses import success_response

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post(
    "",
    response_model=ResponseEnvelope[NotificationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Dispatch Notification",
    description="Dispatches a user notification.",
)
async def create_notification(
    payload: NotificationCreate,
    service: NotificationService = Depends(get_notification_service),
):
    notif = await service.create_notification(
        user_id=payload.user_id,
        notification_type=payload.notification_type,
        title=payload.title,
        body=payload.body,
    )
    return success_response(
        data=NotificationResponse.model_validate(notif),
        message="Notification dispatched successfully.",
    )


@router.patch(
    "/{notification_id}/read",
    response_model=ResponseEnvelope[NotificationResponse],
    summary="Mark Notification Read",
    description="Marks a user notification as read.",
)
async def mark_read(
    notification_id: uuid.UUID,
    service: NotificationService = Depends(get_notification_service),
):
    notif = await service.mark_as_read(notification_id)
    return success_response(
        data=NotificationResponse.model_validate(notif),
        message="Notification marked as read.",
    )
