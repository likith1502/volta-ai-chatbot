import hashlib
import hmac
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

logger = logging.getLogger("app.messaging.whatsapp")


class WhatsAppMessagingAdapter(BaseMessagingAdapter):
    """Channel adapter for WhatsApp Business Cloud API."""

    channel = ChannelType.WHATSAPP

    def __init__(
        self,
        api_token: str | None = None,
        phone_number_id: str | None = None,
        verify_token: str | None = None,
        app_secret: str | None = None,
        api_base_url: str | None = None,
        max_replay_age: int | None = 86400,
    ) -> None:
        self.api_token = api_token or settings.WHATSAPP_API_TOKEN
        self.phone_number_id = phone_number_id or settings.WHATSAPP_PHONE_NUMBER_ID
        self.verify_token = verify_token or settings.WHATSAPP_VERIFY_TOKEN
        self.app_secret = app_secret or settings.WHATSAPP_APP_SECRET
        self.api_base_url = api_base_url or settings.WHATSAPP_API_BASE_URL
        self.max_replay_age = max_replay_age

    def verify_webhook(
        self,
        headers: dict[str, str],
        raw_body: bytes,
        query_params: dict[str, str],
    ) -> WebhookVerificationResult:
        """Verifies WhatsApp verification challenge (GET) or HMAC-SHA256 signature (POST)."""
        # 1. Meta Webhook Verification Challenge (GET)
        mode = query_params.get("hub.mode")
        token = query_params.get("hub.verify_token")
        challenge = query_params.get("hub.challenge")

        if mode or token or challenge:
            if mode == "subscribe" and token and (token == self.verify_token):
                logger.info("WhatsApp webhook challenge verification succeeded.")
                return WebhookVerificationResult(
                    is_valid=True,
                    challenge_response=challenge,
                    status_code=200,
                )
            logger.warning("WhatsApp webhook challenge verification failed.")
            return WebhookVerificationResult(
                is_valid=False,
                error_message="Verification token mismatch or invalid mode.",
                status_code=403,
            )

        # 2. Meta Inbound Webhook Signature Verification (POST)
        if self.app_secret:
            normalized_headers = {k.lower(): v for k, v in headers.items()}
            sig_header = normalized_headers.get("x-hub-signature-256", "")
            if not sig_header:
                logger.warning("Missing X-Hub-Signature-256 header on WhatsApp POST.")
                return WebhookVerificationResult(
                    is_valid=False,
                    error_message="Missing X-Hub-Signature-256 header.",
                    status_code=401,
                )

            expected_sig = "sha256=" + hmac.new(
                self.app_secret.encode("utf-8"),
                raw_body,
                hashlib.sha256,
            ).hexdigest()

            if not hmac.compare_digest(sig_header, expected_sig):
                logger.warning("WhatsApp HMAC-SHA256 signature mismatch.")
                return WebhookVerificationResult(
                    is_valid=False,
                    error_message="Invalid webhook signature.",
                    status_code=401,
                )

        return WebhookVerificationResult(is_valid=True, status_code=200)

    def parse_inbound(self, payload: dict[str, Any]) -> list[InboundMessage]:
        """Parses Meta Cloud API payload into normalized InboundMessage items."""
        inbound_messages: list[InboundMessage] = []
        entries = payload.get("entry", [])
        if not isinstance(entries, list):
            return inbound_messages

        for entry in entries:
            changes = entry.get("changes", []) if isinstance(entry, dict) else []
            for change in changes:
                value = change.get("value", {}) if isinstance(change, dict) else {}
                if not isinstance(value, dict):
                    continue

                # Map contacts wa_id to profile names
                contacts_map: dict[str, str] = {}
                for contact in value.get("contacts", []):
                    wa_id = contact.get("wa_id")
                    name = contact.get("profile", {}).get("name")
                    if wa_id and name:
                        contacts_map[str(wa_id)] = str(name)

                messages = value.get("messages", [])
                for msg in messages:
                    if not isinstance(msg, dict):
                        continue

                    sender_id = msg.get("from")
                    msg_id = msg.get("id")
                    if not sender_id or not msg_id:
                        continue

                    content = ""
                    msg_type = msg.get("type", "text")

                    if msg_type == "text":
                        content = msg.get("text", {}).get("body", "").strip()
                    elif msg_type == "interactive":
                        interactive = msg.get("interactive", {})
                        btn_reply = interactive.get("button_reply", {})
                        list_reply = interactive.get("list_reply", {})
                        content = (
                            btn_reply.get("title")
                            or list_reply.get("title")
                            or ""
                        ).strip()

                    if not content:
                        logger.debug("Skipping non-text or empty WhatsApp message: %s", msg_id)
                        continue

                    ts_val = msg.get("timestamp")
                    timestamp: datetime | None = None
                    if ts_val:
                        try:
                            timestamp = datetime.fromtimestamp(int(ts_val), tz=timezone.utc)
                            # Replay protection: skip messages older than 24 hours
                            age_seconds = (datetime.now(timezone.utc) - timestamp).total_seconds()
                            if (
                                self.max_replay_age is not None
                                and age_seconds > self.max_replay_age
                            ):
                                logger.warning(
                                    "Ignoring stale WhatsApp message %s with age %.0fs",
                                    msg_id,
                                    age_seconds,
                                )
                                continue
                        except (ValueError, TypeError, OverflowError):
                            timestamp = None

                    sender_name = contacts_map.get(str(sender_id))
                    inbound_messages.append(
                        InboundMessage(
                            channel=ChannelType.WHATSAPP,
                            external_message_id=str(msg_id),
                            external_user_id=str(sender_id),
                            sender_name=sender_name,
                            content=content,
                            timestamp=timestamp,
                            raw_payload=msg,
                            metadata={"phone_number_id": value.get("metadata", {}).get("phone_number_id")},
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
        """Formats canonical message into OutboundMessage for WhatsApp with 4096-char safety."""
        safe_content = content
        if len(safe_content) > 4096:
            safe_content = safe_content[:4090] + "..."

        return OutboundMessage(
            channel=ChannelType.WHATSAPP,
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
        """Dispatches outbound message to Meta WhatsApp Cloud API."""
        phone_number_id = (
            message.metadata.get("phone_number_id")
            or self.phone_number_id
        )
        url = f"{self.api_base_url.rstrip('/')}/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": message.recipient_id,
            "type": "text",
            "text": {"preview_url": False, "body": message.content},
        }

        try:
            if client is not None:
                resp = await client.post(url, headers=headers, json=payload)
                return resp.status_code in [200, 201]

            async with httpx.AsyncClient(timeout=15.0) as async_client:
                resp = await async_client.post(url, headers=headers, json=payload)
                return resp.status_code in [200, 201]
        except Exception as exc:
            logger.error("Failed to send WhatsApp message to %s: %s", message.recipient_id, exc)
            return False
