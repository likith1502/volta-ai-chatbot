import uuid

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_conversation_service
from app.schemas.common import ResponseEnvelope
from app.schemas.conversation import ConversationCreate, ConversationResponse
from app.services.conversation import ConversationService
from app.utils.responses import success_response

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.post(
    "",
    response_model=ResponseEnvelope[ConversationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Conversation Session",
    description="Initializes a new dialogue conversation session.",
)
async def create_conversation(
    payload: ConversationCreate,
    service: ConversationService = Depends(get_conversation_service),
):
    conv = await service.create_conversation(
        user_id=payload.user_id,
        session_id=payload.session_id,
        source=payload.source,
        title=payload.title,
    )
    return success_response(
        data=ConversationResponse.model_validate(conv),
        message="Conversation session created successfully.",
    )


@router.get(
    "/latest",
    response_model=ResponseEnvelope[ConversationResponse],
    summary="Get Latest Active Conversation",
    description="Retrieves the most recent active conversation session for a user.",
)
async def get_latest_conversation(
    user_id: uuid.UUID,
    service: ConversationService = Depends(get_conversation_service),
):
    conv = await service.get_latest_active_conversation(user_id)
    return success_response(
        data=ConversationResponse.model_validate(conv),
        message="Latest active conversation retrieved successfully.",
    )


@router.get(
    "/{conversation_id}",
    response_model=ResponseEnvelope[ConversationResponse],
    summary="Get Conversation By ID",
    description="Retrieves a conversation session by primary key UUID.",
)
async def get_conversation(
    conversation_id: uuid.UUID,
    service: ConversationService = Depends(get_conversation_service),
):
    conv = await service.get_conversation(conversation_id)
    return success_response(
        data=ConversationResponse.model_validate(conv),
        message="Conversation session retrieved successfully.",
    )


@router.delete(
    "/{conversation_id}",
    response_model=ResponseEnvelope[ConversationResponse],
    summary="Archive Conversation Session",
    description="Archives an active conversation session.",
)
async def archive_conversation(
    conversation_id: uuid.UUID,
    service: ConversationService = Depends(get_conversation_service),
):
    conv = await service.archive_conversation(conversation_id)
    return success_response(
        data=ConversationResponse.model_validate(conv),
        message="Conversation session archived successfully.",
    )
