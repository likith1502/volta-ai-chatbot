import asyncio
import logging
from typing import Any

from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_sessionmaker
from app.messaging.adapters.telegram import TelegramMessagingAdapter
from app.messaging.adapters.whatsapp import WhatsAppMessagingAdapter
from app.messaging.base import BaseMessagingAdapter
from app.messaging.idempotency import IdempotencyStore, get_idempotency_store
from app.messaging.identity import ChannelIdentityResolver
from app.messaging.models import ChannelType, InboundMessage
from app.models.enums import ConversationSource
from app.services.chat import ChatService

logger = logging.getLogger("app.messaging.service")


class MessagingBridgeService:
    """Orchestrates channel webhooks, authentication, idempotency, and background AI execution."""

    def __init__(
        self,
        adapters: dict[ChannelType, BaseMessagingAdapter] | None = None,
        idempotency_store: IdempotencyStore | None = None,
        http_client: Any | None = None,
    ) -> None:
        self.adapters: dict[ChannelType, BaseMessagingAdapter] = adapters or {
            ChannelType.WHATSAPP: WhatsAppMessagingAdapter(),
            ChannelType.TELEGRAM: TelegramMessagingAdapter(),
        }
        self.idempotency_store = idempotency_store or get_idempotency_store()
        self.http_client = http_client

    def get_adapter(self, channel: ChannelType) -> BaseMessagingAdapter:
        """Retrieves registered channel adapter."""
        adapter = self.adapters.get(channel)
        if not adapter:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported channel: {channel}",
            )
        return adapter

    def verify_webhook_request(
        self,
        channel: ChannelType,
        headers: dict[str, str],
        raw_body: bytes,
        query_params: dict[str, str],
    ) -> str | None:
        """Verifies webhook authentication. Returns challenge string if applicable, or raises HTTPException."""
        adapter = self.get_adapter(channel)
        result = adapter.verify_webhook(headers, raw_body, query_params)

        if not result.is_valid:
            logger.warning(
                "Webhook verification failed for %s: %s",
                channel.value,
                result.error_message,
            )
            raise HTTPException(
                status_code=result.status_code,
                detail=result.error_message or "Webhook verification failed.",
            )

        return result.challenge_response

    async def handle_inbound_webhook(
        self,
        channel: ChannelType,
        headers: dict[str, str],
        raw_body: bytes,
        payload: dict[str, Any],
        background_tasks: BackgroundTasks | None = None,
        await_completion: bool = False,
    ) -> dict[str, Any]:
        """Authenticates, validates, normalizes, and enqueues inbound messages for background processing."""
        # 1. Authenticate webhook signature / secret token
        adapter = self.get_adapter(channel)
        verification = adapter.verify_webhook(headers, raw_body, {})
        if not verification.is_valid:
            logger.warning(
                "Webhook auth failed for %s: %s",
                channel.value,
                verification.error_message,
            )
            raise HTTPException(
                status_code=verification.status_code,
                detail=verification.error_message or "Webhook authentication failed.",
            )

        # 2. Normalize payload into canonical InboundMessage objects
        messages = adapter.parse_inbound(payload)
        if not messages:
            logger.info("Acknowledged non-message/status event for %s", channel.value)
            return {
                "status": "acknowledged",
                "channel": channel.value,
                "processed": 0,
            }

        # 3. Enqueue or execute background processing
        for msg in messages:
            if await_completion:
                # Direct execution mode for tests / synchronous execution
                await self.process_inbound_message(msg)
            elif background_tasks is not None:
                # FastAPI BackgroundTasks queue
                background_tasks.add_task(self.process_inbound_message, msg)
            else:
                # Asyncio background task
                asyncio.create_task(self.process_inbound_message(msg))

        # 4. Immediate provider-required acknowledgement
        if channel == ChannelType.TELEGRAM:
            return {"ok": True, "result": "accepted", "count": len(messages)}
        return {"status": "accepted", "channel": channel.value, "count": len(messages)}

    async def process_inbound_message(
        self,
        message: InboundMessage,
        session: AsyncSession | None = None,
        chat_service: ChatService | None = None,
    ) -> dict[str, Any]:
        """Background worker executing identity resolution, ChatService, and outbound reply."""
        # 1. Atomic Idempotency Acquisition (NEW -> PROCESSING)
        acquired = await self.idempotency_store.try_acquire(
            message.channel,
            message.external_message_id,
        )
        if not acquired:
            logger.info(
                "Duplicate/in-flight message detected for %s message ID %s, skipping.",
                message.channel.value,
                message.external_message_id,
            )
            return {"status": "duplicate", "message_id": message.external_message_id}

        try:
            # 2. Execution with isolated session boundary
            if session is not None:
                result = await self._execute_chat_turn(message, session, chat_service)
            else:
                sessionmaker = get_sessionmaker()
                async with sessionmaker() as db_session:
                    try:
                        result = await self._execute_chat_turn(message, db_session, chat_service)
                        await db_session.commit()
                    except Exception as exc:
                        await db_session.rollback()
                        logger.error(
                            "Error executing background chat turn for %s: %s",
                            message.channel.value,
                            exc,
                            exc_info=True,
                        )
                        raise

            # 3. Transition to COMPLETED
            await self.idempotency_store.mark_completed(
                message.channel,
                message.external_message_id,
            )
            return result
        except Exception:
            # On failure, release processing lock so retry can proceed
            await self.idempotency_store.mark_failed(
                message.channel,
                message.external_message_id,
            )
            raise

    async def _execute_chat_turn(
        self,
        message: InboundMessage,
        session: AsyncSession,
        chat_service: ChatService | None = None,
    ) -> dict[str, Any]:
        """Executes the pipeline within an active AsyncSession."""
        # A. Identity Resolution
        resolver = ChannelIdentityResolver(session)
        user = await resolver.resolve_or_create_user(
            channel=message.channel,
            external_user_id=message.external_user_id,
            sender_name=message.sender_name,
        )
        session_id = resolver.get_session_id(
            channel=message.channel,
            external_user_id=message.external_user_id,
        )

        # B. Resolve Conversation Source
        source = (
            ConversationSource.WHATSAPP
            if message.channel == ChannelType.WHATSAPP
            else ConversationSource.TELEGRAM
        )

        # C. Execute ChatService -> Graph Runtime
        service = chat_service or ChatService(session)
        chat_result = await service.process_chat(
            user_id=user.id,
            session_id=session_id,
            message_text=message.content,
            source=source,
        )

        # D. Format Outbound Message
        reply_message = chat_result["message"]
        adapter = self.get_adapter(message.channel)
        outbound = adapter.format_outbound(
            content=reply_message.content,
            recipient_id=message.external_user_id,
            reply_to_message_id=message.external_message_id,
            metadata=message.metadata,
        )

        # E. Send Outbound Message to Channel Provider
        dispatch_success = await adapter.send_outbound(
            outbound,
            client=self.http_client,
        )

        return {
            "status": "success",
            "conversation_id": chat_result["conversation_id"],
            "session_id": session_id,
            "response_text": reply_message.content,
            "outbound_dispatched": dispatch_success,
            "recommendation_id": chat_result.get("recommendation_id"),
        }
