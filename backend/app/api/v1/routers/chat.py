from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_chat_service
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.common import ResponseEnvelope
from app.services.chat import ChatService
from app.utils.responses import success_response

router = APIRouter(prefix="/chat", tags=["Chat & AI"])


@router.post(
    "",
    response_model=ResponseEnvelope[ChatResponse],
    status_code=status.HTTP_200_OK,
    summary="Process Chat Interaction",
    description="Processes conversational AI interaction for an authenticated user context.",
)
async def process_chat(
    payload: ChatRequest,
    service: ChatService = Depends(get_chat_service),
):
    result = await service.process_chat(
        user_id=payload.user_id,
        session_id=payload.session_id,
        message_text=payload.message,
    )
    return success_response(
        data=ChatResponse.model_validate(result),
        message="Chat message processed successfully.",
    )
