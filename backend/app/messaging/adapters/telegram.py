import logging
from datetime import datetime, timezone
from typing import Any

import httpx

from app.config.settings import settings
from app.messaging.base import BaseMessagingAdapter
from app.messaging.models import (
    ChannelType,
    InboundMessage,
    OutboundMessage,
    WebhookVerificationResult,
)

logger = logging.getLogger("app.messaging.telegram")


class TelegramMessagingAdapter(BaseMessagingAdapter):
    """Channel adapter for Telegram Bot API."""

    channel = ChannelType.TELEGRAM

    def __init__(
        self,
        bot_token: str | None = None,
        webhook_secret: str | None = None,
        api_base_url: str | None = None,
    ) -> None:
        self.bot_token = bot_token or settings.TELEGRAM_BOT_TOKEN
        self.webhook_secret = webhook_secret or settings.TELEGRAM_WEBHOOK_SECRET
        self.api_base_url = api_base_url or settings.TELEGRAM_API_BASE_URL

    def verify_webhook(
        self,
        headers: dict[str, str],
        raw_body: bytes,
        query_params: dict[str, str],
    ) -> WebhookVerificationResult:
        """Verifies Telegram webhook secret token header."""
        if self.webhook_secret:
            normalized_headers = {k.lower(): v for k, v in headers.items()}
            received_secret = normalized_headers.get(
                "x-telegram-bot-api-secret-token",
                "",
            )
            if received_secret != self.webhook_secret:
                logger.warning("Telegram webhook secret token mismatch.")
                return WebhookVerificationResult(
                    is_valid=False,
                    error_message="Invalid Telegram webhook secret token.",
                    status_code=403,
                )

        return WebhookVerificationResult(is_valid=True, status_code=200)

    def parse_inbound(self, payload: dict[str, Any]) -> list[InboundMessage]:
        """Parses Telegram Update payload into normalized InboundMessage items."""
        inbound_messages: list[InboundMessage] = []
        if not isinstance(payload, dict):
            return inbound_messages

        msg_obj = payload.get("message") or payload.get("edited_message")
        if not isinstance(msg_obj, dict):
            logger.debug("Skipping non-message Telegram update.")
            return inbound_messages

        text = (msg_obj.get("text") or "").strip()
        if not text:
            logger.debug("Skipping Telegram message without text.")
            return inbound_messages

        chat_obj = msg_obj.get("chat", {})
        from_obj = msg_obj.get("from", {})
        chat_id = str(chat_obj.get("id") or "")
        user_id = str(from_obj.get("id") or chat_id)
        message_id = str(msg_obj.get("message_id") or "")

        if not chat_id or not message_id:
            return inbound_messages

        # Construct sender display name
        first_name = from_obj.get("first_name", "")
        last_name = from_obj.get("last_name", "")
        username = from_obj.get("username", "")
        full_name = f"{first_name} {last_name}".strip()
        sender_name = full_name or username or f"Telegram User {user_id}"

        timestamp: datetime | None = None
        date_val = msg_obj.get("date")
        if date_val:
            try:
                timestamp = datetime.fromtimestamp(int(date_val), tz=timezone.utc)
            except (ValueError, TypeError, OverflowError):
                timestamp = None

        inbound_messages.append(
            InboundMessage(
                channel=ChannelType.TELEGRAM,
                external_message_id=message_id,
                external_user_id=chat_id,
                sender_name=sender_name,
                content=text,
                timestamp=timestamp,
                raw_payload=payload,
                metadata={"chat_id": chat_id, "user_id": user_id, "username": username},
            )
        )

        return inbound_messages

    def format_outbound(
        self,
        content: str,
        recipient_id: str,
        reply_to_message_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> OutboundMessage:
        """Formats canonical message into OutboundMessage for Telegram with 4096-char safety."""
        safe_content = content
        if len(safe_content) > 4096:
            safe_content = safe_content[:4090] + "..."

        return OutboundMessage(
            channel=ChannelType.TELEGRAM,
            recipient_id=recipient_id,
            content=safe_content,
            reply_to_message_id=reply_to_message_id,
            metadata=metadata or {},
        )

    async def send_outbound(
        self,
        message: OutboundMessage,
        client: Any | None = None,
    ) -> bool:
        """Dispatches outbound message to Telegram Bot API sendMessage."""
        url = f"{self.api_base_url.rstrip('/')}/bot{self.bot_token}/sendMessage"
        payload: dict[str, Any] = {
            "chat_id": message.recipient_id,
            "text": message.content,
            "parse_mode": "Markdown",
        }
        if message.reply_to_message_id:
            try:
                payload["reply_to_message_id"] = int(message.reply_to_message_id)
            except ValueError:
                pass

        def _is_parse_error(response_text: str) -> bool:
            lowered = response_text.lower()
            return any(
                term in lowered
                for term in ["parse", "entity", "can't find end", "markdown"]
            )

        try:
            if client is not None:
                resp = await client.post(url, json=payload)
                if resp.status_code == 400 and _is_parse_error(resp.text):
                    # Robust fallback to plain text if LLM markdown breaks Telegram parser
                    payload.pop("parse_mode", None)
                    resp = await client.post(url, json=payload)
                return resp.status_code == 200

            async with httpx.AsyncClient(timeout=15.0) as async_client:
                resp = await async_client.post(url, json=payload)
                if resp.status_code == 400 and _is_parse_error(resp.text):
                    payload.pop("parse_mode", None)
                    resp = await async_client.post(url, json=payload)
                return resp.status_code == 200
        except Exception as exc:
            logger.error(
                "Failed to send Telegram message to %s: %s",
                message.recipient_id,
                exc,
            )
            return False
