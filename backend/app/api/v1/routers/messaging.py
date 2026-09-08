import json
import logging
from typing import Any

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)

from app.messaging.models import ChannelType
from app.messaging.service import MessagingBridgeService

logger = logging.getLogger("app.api.v1.routers.messaging")

router = APIRouter(prefix="/messaging", tags=["Messaging Channels"])


def get_messaging_bridge_service() -> MessagingBridgeService:
    """Dependency provider yielding a configured MessagingBridgeService."""
    return MessagingBridgeService()


@router.get(
    "/whatsapp/webhook",
    summary="Verify WhatsApp Webhook Challenge",
    description="Validates Meta hub.verify_token and echoes back hub.challenge.",
    status_code=status.HTTP_200_OK,
)
async def verify_whatsapp_webhook(
    hub_mode: str | None = Query(None, alias="hub.mode"),
    hub_challenge: str | None = Query(None, alias="hub.challenge"),
    hub_verify_token: str | None = Query(None, alias="hub.verify_token"),
    service: MessagingBridgeService = Depends(get_messaging_bridge_service),
) -> Response:
    query_params: dict[str, str] = {}
    if hub_mode:
        query_params["hub.mode"] = hub_mode
    if hub_challenge:
        query_params["hub.challenge"] = hub_challenge
    if hub_verify_token:
        query_params["hub.verify_token"] = hub_verify_token

    challenge = service.verify_webhook_request(
        channel=ChannelType.WHATSAPP,
        headers={},
        raw_body=b"",
        query_params=query_params,
    )
    if challenge is not None:
        return Response(content=challenge, media_type="text/plain")

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid verification challenge parameters.",
    )


MAX_WEBHOOK_BODY_BYTES = 1024 * 1024  # 1 MB maximum payload protection


@router.post(
    "/whatsapp/webhook",
    summary="Receive WhatsApp Inbound Webhook",
    description=(
        "Authenticates Meta HMAC signature, validates message payload, "
        "enqueues background AI processing, and acknowledges delivery immediately."
    ),
    status_code=status.HTTP_200_OK,
)
async def receive_whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    service: MessagingBridgeService = Depends(get_messaging_bridge_service),
) -> dict[str, Any]:
    raw_body = await request.body()
    if len(raw_body) > MAX_WEBHOOK_BODY_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Webhook payload exceeds maximum allowable size (1 MB).",
        )

    try:
        payload = json.loads(raw_body.decode("utf-8") or "{}")
    except Exception as exc:
        logger.warning("Malformed JSON payload in WhatsApp webhook: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed JSON payload.",
        ) from exc

    headers = dict(request.headers)
    return await service.handle_inbound_webhook(
        channel=ChannelType.WHATSAPP,
        headers=headers,
        raw_body=raw_body,
        payload=payload,
        background_tasks=background_tasks,
    )


@router.post(
    "/telegram/webhook",
    summary="Receive Telegram Inbound Webhook",
    description=(
        "Authenticates secret token header, validates update, enqueues "
        "background AI processing, and acknowledges delivery immediately."
    ),
    status_code=status.HTTP_200_OK,
)
async def receive_telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    service: MessagingBridgeService = Depends(get_messaging_bridge_service),
) -> dict[str, Any]:
    raw_body = await request.body()
    if len(raw_body) > MAX_WEBHOOK_BODY_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Webhook payload exceeds maximum allowable size (1 MB).",
        )
    try:
        payload = json.loads(raw_body.decode("utf-8") or "{}")
    except Exception as exc:
        logger.warning("Malformed JSON payload in Telegram webhook: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed JSON payload.",
        ) from exc

    headers = dict(request.headers)
    return await service.handle_inbound_webhook(
        channel=ChannelType.TELEGRAM,
        headers=headers,
        raw_body=raw_body,
        payload=payload,
        background_tasks=background_tasks,
    )
