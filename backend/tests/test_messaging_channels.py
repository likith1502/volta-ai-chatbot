import hashlib
import hmac
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from app.ai.base import AIProvider
from app.ai.models import AIRequest, AIResponse, AITokenUsage
from app.api.v1.routers.messaging import get_messaging_bridge_service
from app.main import app
from app.messaging.adapters.telegram import TelegramMessagingAdapter
from app.messaging.adapters.whatsapp import WhatsAppMessagingAdapter
from app.messaging.idempotency import IdempotencyState, IdempotencyStore
from app.messaging.identity import ChannelIdentityResolver
from app.messaging.models import ChannelType, InboundMessage
from app.models.user import User
from app.services.chat import ChatService
from app.services.chat_graph import ChatGraphOrchestrator
from fastapi.testclient import TestClient


class MockAIProvider(AIProvider):
    """Deterministic AI provider mock for messaging channel testing."""

    def __init__(self, response_content: str = "Hello from Volta AI!"):
        self.response_content = response_content

    async def generate_response(self, request: AIRequest) -> AIResponse:
        return AIResponse(
            content=self.response_content,
            model_used="gemini-2.5-flash",
            usage=AITokenUsage(prompt_tokens=10, completion_tokens=8, total_tokens=18),
            tool_calls=[],
        )


@pytest.fixture
def client():
    return TestClient(app)


# ============================================================================
# 1. WhatsApp Webhook Verification Challenge (GET) Tests
# ============================================================================


def test_whatsapp_webhook_verification_success(client):
    """Verify WhatsApp GET webhook echoes challenge when verify token matches."""
    bridge_service = MagicMock()
    bridge_service.verify_webhook_request.return_value = "challenge_echo_98765"

    app.dependency_overrides[get_messaging_bridge_service] = lambda: bridge_service
    try:
        response = client.get(
            "/api/v1/messaging/whatsapp/webhook",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "test_token_123",
                "hub.challenge": "challenge_echo_98765",
            },
        )
        assert response.status_code == 200
        assert response.text == "challenge_echo_98765"
    finally:
        app.dependency_overrides.pop(get_messaging_bridge_service, None)


def test_whatsapp_webhook_verification_forbidden():
    """Verify WhatsApp adapter rejects mismatched verify token with HTTP 403."""
    adapter = WhatsAppMessagingAdapter(verify_token="expected_secret_token")
    result = adapter.verify_webhook(
        headers={},
        raw_body=b"",
        query_params={"hub.mode": "subscribe", "hub.verify_token": "wrong_token"},
    )
    assert not result.is_valid
    assert result.status_code == 403


# ============================================================================
# 2. WhatsApp Signature Authentication (POST) Tests
# ============================================================================


def test_whatsapp_signature_verification_success():
    """Verify valid Meta HMAC-SHA256 signature is accepted."""
    app_secret = "meta_app_secret_xyz"
    raw_body = b'{"object": "whatsapp_business_account"}'
    sig = (
        "sha256=" + hmac.new(app_secret.encode(), raw_body, hashlib.sha256).hexdigest()
    )

    adapter = WhatsAppMessagingAdapter(app_secret=app_secret)
    result = adapter.verify_webhook(
        headers={"x-hub-signature-256": sig},
        raw_body=raw_body,
        query_params={},
    )
    assert result.is_valid
    assert result.status_code == 200


def test_whatsapp_signature_verification_failure():
    """Verify invalid or missing Meta HMAC signature is rejected with HTTP 401."""
    app_secret = "meta_app_secret_xyz"
    raw_body = b'{"object": "whatsapp_business_account"}'

    adapter = WhatsAppMessagingAdapter(app_secret=app_secret)
    # 1. Missing header
    res_missing = adapter.verify_webhook(headers={}, raw_body=raw_body, query_params={})
    assert not res_missing.is_valid
    assert res_missing.status_code == 401

    # 2. Wrong signature
    res_wrong = adapter.verify_webhook(
        headers={"x-hub-signature-256": "sha256=invalid_hash"},
        raw_body=raw_body,
        query_params={},
    )
    assert not res_wrong.is_valid
    assert res_wrong.status_code == 401


# ============================================================================
# 3. WhatsApp Payload Normalization & Status Filtering
# ============================================================================


def test_whatsapp_inbound_normalization():
    """Verify text message payload is normalized into canonical InboundMessage."""
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "1001",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {"phone_number_id": "999888"},
                            "contacts": [
                                {
                                    "profile": {"name": "Alice Green"},
                                    "wa_id": "14155552671",
                                }
                            ],
                            "messages": [
                                {
                                    "from": "14155552671",
                                    "id": "wamid.HBgLMDExMQ==",
                                    "timestamp": "1672531199",
                                    "text": {
                                        "body": "Find EV charging stations near me"
                                    },
                                    "type": "text",
                                }
                            ],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }

    adapter = WhatsAppMessagingAdapter(max_replay_age=None)
    messages = adapter.parse_inbound(payload)

    assert len(messages) == 1
    msg = messages[0]
    assert msg.channel == ChannelType.WHATSAPP
    assert msg.external_message_id == "wamid.HBgLMDExMQ=="
    assert msg.external_user_id == "14155552671"
    assert msg.sender_name == "Alice Green"
    assert msg.content == "Find EV charging stations near me"
    assert msg.metadata.get("phone_number_id") == "999888"


def test_whatsapp_status_receipt_ignored():
    """Verify delivery and read status receipts yield 0 normalized messages."""
    status_payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "statuses": [
                                {
                                    "id": "wamid.HBgLMDExMQ==",
                                    "status": "delivered",
                                    "timestamp": "1672531200",
                                    "recipient_id": "14155552671",
                                }
                            ],
                        }
                    }
                ]
            }
        ],
    }

    adapter = WhatsAppMessagingAdapter()
    messages = adapter.parse_inbound(status_payload)
    assert messages == []


def test_whatsapp_interactive_button_reply():
    """Verify interactive button replies are correctly extracted."""
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "contacts": [{"profile": {"name": "Bob"}, "wa_id": "1999"}],
                            "messages": [
                                {
                                    "from": "1999",
                                    "id": "wamid.BTN001",
                                    "type": "interactive",
                                    "interactive": {
                                        "type": "button_reply",
                                        "button_reply": {
                                            "id": "btn_confirm",
                                            "title": "Confirm Booking",
                                        },
                                    },
                                }
                            ],
                        }
                    }
                ]
            }
        ],
    }
    adapter = WhatsAppMessagingAdapter()
    messages = adapter.parse_inbound(payload)
    assert len(messages) == 1
    assert messages[0].content == "Confirm Booking"


# ============================================================================
# 4. Telegram Webhook Secret & Payload Normalization
# ============================================================================


def test_telegram_webhook_secret_success():
    """Verify Telegram webhook secret token header matches configured secret."""
    adapter = TelegramMessagingAdapter(webhook_secret="tg_secret_token_abc")
    result = adapter.verify_webhook(
        headers={"x-telegram-bot-api-secret-token": "tg_secret_token_abc"},
        raw_body=b"{}",
        query_params={},
    )
    assert result.is_valid
    assert result.status_code == 200


def test_telegram_webhook_secret_failure():
    """Verify invalid Telegram webhook secret token returns HTTP 403."""
    adapter = TelegramMessagingAdapter(webhook_secret="tg_secret_token_abc")
    result = adapter.verify_webhook(
        headers={"x-telegram-bot-api-secret-token": "wrong_secret"},
        raw_body=b"{}",
        query_params={},
    )
    assert not result.is_valid
    assert result.status_code == 403


def test_telegram_inbound_normalization():
    """Verify Telegram message update is normalized into canonical InboundMessage."""
    payload = {
        "update_id": 987654321,
        "message": {
            "message_id": 4201,
            "from": {
                "id": 554433221,
                "first_name": "Carol",
                "last_name": "Danvers",
                "username": "captain_carol",
            },
            "chat": {
                "id": 554433221,
                "first_name": "Carol",
                "type": "private",
            },
            "date": 1672531199,
            "text": "Book an electric cab to the airport",
        },
    }

    adapter = TelegramMessagingAdapter()
    messages = adapter.parse_inbound(payload)

    assert len(messages) == 1
    msg = messages[0]
    assert msg.channel == ChannelType.TELEGRAM
    assert msg.external_message_id == "4201"
    assert msg.external_user_id == "554433221"
    assert msg.sender_name == "Carol Danvers"
    assert msg.content == "Book an electric cab to the airport"


# ============================================================================
# 5. Immediate Webhook Acknowledgement (Decoupled Flow) Tests
# ============================================================================


def test_whatsapp_immediate_acknowledgement_endpoint(client):
    """Verify WhatsApp POST webhook returns immediate HTTP 200 OK without blocking."""
    mock_service = MagicMock()
    mock_service.handle_inbound_webhook = AsyncMock(
        return_value={"status": "accepted", "channel": "whatsapp", "count": 1}
    )
    app.dependency_overrides[get_messaging_bridge_service] = lambda: mock_service

    try:
        response = client.post(
            "/api/v1/messaging/whatsapp/webhook",
            json={"object": "whatsapp_business_account"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "accepted"
        assert mock_service.handle_inbound_webhook.called
    finally:
        app.dependency_overrides.pop(get_messaging_bridge_service, None)


def test_telegram_immediate_acknowledgement_endpoint(client):
    """Verify Telegram POST webhook returns immediate HTTP 200 OK without blocking."""
    mock_service = MagicMock()
    mock_service.handle_inbound_webhook = AsyncMock(
        return_value={"ok": True, "result": "accepted", "count": 1}
    )
    app.dependency_overrides[get_messaging_bridge_service] = lambda: mock_service

    try:
        response = client.post(
            "/api/v1/messaging/telegram/webhook",
            json={"update_id": 12345},
        )
        assert response.status_code == 200
        assert response.json()["ok"] is True
        assert mock_service.handle_inbound_webhook.called
    finally:
        app.dependency_overrides.pop(get_messaging_bridge_service, None)


# ============================================================================
# 6. Channel Identity Resolution & Session Continuity Tests
# ============================================================================


@pytest.mark.asyncio
async def test_channel_identity_resolution_whatsapp():
    """Verify WhatsApp identity creates new user with phone number and reuses on turn 2."""
    session = AsyncMock()
    resolver = ChannelIdentityResolver(session)

    # First turn: user not found, created
    resolver.user_repo.get_by_phone = AsyncMock(return_value=None)
    resolver.user_repo.get_by_email = AsyncMock(return_value=None)
    created_user = User(
        id=uuid.uuid4(),
        full_name="Alice Green",
        email="wa_14155552671@volta.internal",
        phone_number="14155552671",
    )
    resolver.user_repo.create = AsyncMock(return_value=created_user)

    user1 = await resolver.resolve_or_create_user(
        ChannelType.WHATSAPP,
        "14155552671",
        "Alice Green",
    )
    assert user1.id == created_user.id
    assert user1.phone_number == "14155552671"
    assert resolver.user_repo.create.called

    # Second turn: user found by phone, not recreated
    resolver.user_repo.get_by_phone = AsyncMock(return_value=created_user)
    resolver.user_repo.create.reset_mock()

    user2 = await resolver.resolve_or_create_user(
        ChannelType.WHATSAPP,
        "14155552671",
        "Alice Green",
    )
    assert user2.id == created_user.id
    assert not resolver.user_repo.create.called

    session_id = resolver.get_session_id(ChannelType.WHATSAPP, "14155552671")
    assert session_id == "whatsapp_14155552671"


@pytest.mark.asyncio
async def test_channel_identity_resolution_telegram():
    """Verify Telegram identity creates user with internal email and generates session."""
    session = AsyncMock()
    resolver = ChannelIdentityResolver(session)

    created_user = User(
        id=uuid.uuid4(),
        full_name="Carol Danvers",
        email="tg_554433221@volta.internal",
        phone_number=None,
    )
    resolver.user_repo.get_by_email = AsyncMock(return_value=None)
    resolver.user_repo.create = AsyncMock(return_value=created_user)

    user = await resolver.resolve_or_create_user(
        ChannelType.TELEGRAM,
        "554433221",
        "Carol Danvers",
    )
    assert user.id == created_user.id
    assert user.email == "tg_554433221@volta.internal"

    session_id = resolver.get_session_id(ChannelType.TELEGRAM, "554433221")
    assert session_id == "telegram_554433221"


# ============================================================================
# 7. Idempotency Deduplication Tests
# ============================================================================


@pytest.mark.asyncio
async def test_idempotency_store():
    """Verify idempotency store detects duplicate external message IDs within TTL."""
    store = IdempotencyStore(ttl_seconds=60)
    msg_id = "wamid.TEST_IDEMPOTENCY_01"

    # Initial check: not duplicate
    assert not await store.is_duplicate(ChannelType.WHATSAPP, msg_id)

    # Mark processed
    await store.mark_processed(ChannelType.WHATSAPP, msg_id)

    # Subsequent check: is duplicate
    assert await store.is_duplicate(ChannelType.WHATSAPP, msg_id)

    # Different channel or message ID: not duplicate
    assert not await store.is_duplicate(ChannelType.TELEGRAM, msg_id)
    assert not await store.is_duplicate(ChannelType.WHATSAPP, "wamid.OTHER_02")


# ============================================================================
# 8. End-to-End Messaging Traversal to Graph Runtime Tests
# ============================================================================


@pytest.mark.asyncio
async def test_end_to_end_messaging_traversal_to_graph_runtime():
    """Verify WhatsApp inbound message traverses ChatService and Graph Runtime."""
    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    session_id = "whatsapp_14155552671"
    message_text = "I need an electric cab to Koramangala"

    # Mock DB Session
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.execute = AsyncMock(
        return_value=MagicMock(
            scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))
        )
    )

    # Mock AI Provider & Graph Orchestrator
    provider = MockAIProvider(response_content="Electric cab confirmed to Koramangala.")
    graph_orchestrator = ChatGraphOrchestrator(provider=provider)

    # Construct ChatService
    chat_service = ChatService(session=session, provider=provider)
    chat_service.graph_orchestrator = graph_orchestrator

    mock_user = User(
        id=user_id,
        full_name="Alice Green",
        email="wa_14155552671@volta.internal",
        phone_number="14155552671",
    )
    chat_service.user_repo.get_by_id = AsyncMock(return_value=mock_user)

    mock_conv = MagicMock(id=conv_id, session_id=session_id, user_id=user_id)
    chat_service.conversation_repo.get_by_session_id = AsyncMock(return_value=mock_conv)

    mock_user_msg = MagicMock(id=uuid.uuid4(), role="user", content=message_text)
    mock_asst_msg = MagicMock(
        id=uuid.uuid4(),
        role="assistant",
        content="Electric cab confirmed to Koramangala.",
    )
    chat_service.message_repo.count = AsyncMock(return_value=0)
    chat_service.message_repo.create = AsyncMock(
        side_effect=[mock_user_msg, mock_asst_msg]
    )

    # Mock Outbound Dispatch
    mock_wa_adapter = WhatsAppMessagingAdapter()
    mock_wa_adapter.send_outbound = AsyncMock(return_value=True)

    from app.messaging.service import MessagingBridgeService

    bridge = MessagingBridgeService(
        adapters={ChannelType.WHATSAPP: mock_wa_adapter},
        idempotency_store=IdempotencyStore(),
    )

    inbound = InboundMessage(
        channel=ChannelType.WHATSAPP,
        external_message_id="wamid.HBgLMDExMQ==",
        external_user_id="14155552671",
        sender_name="Alice Green",
        content=message_text,
    )

    # Execute end-to-end background turn
    bridge.get_adapter = MagicMock(return_value=mock_wa_adapter)
    result = await bridge._execute_chat_turn(
        message=inbound,
        session=session,
        chat_service=chat_service,
    )

    assert result["status"] == "success"
    assert result["conversation_id"] == conv_id
    assert result["session_id"] == session_id
    assert result["response_text"] == "Electric cab confirmed to Koramangala."
    assert result["outbound_dispatched"] is True
    assert mock_wa_adapter.send_outbound.called


# ============================================================================
# 9. Outbound Payload Formatting Tests
# ============================================================================


def test_whatsapp_outbound_formatting():
    """Verify WhatsApp outbound message formatting."""
    adapter = WhatsAppMessagingAdapter()
    outbound = adapter.format_outbound(
        content="Your cab is arriving in 5 minutes.",
        recipient_id="14155552671",
        reply_to_message_id="wamid.12345",
    )
    assert outbound.channel == ChannelType.WHATSAPP
    assert outbound.recipient_id == "14155552671"
    assert outbound.content == "Your cab is arriving in 5 minutes."
    assert outbound.reply_to_message_id == "wamid.12345"


def test_telegram_outbound_formatting():
    """Verify Telegram outbound message formatting."""
    adapter = TelegramMessagingAdapter()
    outbound = adapter.format_outbound(
        content="*Volta AI:* Ride scheduled.",
        recipient_id="554433221",
        reply_to_message_id="4201",
    )
    assert outbound.channel == ChannelType.TELEGRAM
    assert outbound.recipient_id == "554433221"
    assert outbound.content == "*Volta AI:* Ride scheduled."
    assert outbound.reply_to_message_id == "4201"


# ============================================================================
# 10. Hardening Review & Resilience Tests
# ============================================================================


@pytest.mark.asyncio
async def test_idempotency_state_transitions():
    """Verify atomic state transitions NEW -> PROCESSING -> COMPLETED."""
    store = IdempotencyStore(ttl_seconds=60)
    msg_id = "wamid.HARDEN_STATE_01"

    # NEW: state is None
    assert await store.get_state(ChannelType.WHATSAPP, msg_id) is None

    # NEW -> PROCESSING
    acquired = await store.try_acquire(ChannelType.WHATSAPP, msg_id)
    assert acquired is True
    assert (
        await store.get_state(ChannelType.WHATSAPP, msg_id)
        == IdempotencyState.PROCESSING
    )

    # Duplicate acquisition while PROCESSING must be rejected
    dup_acquired = await store.try_acquire(ChannelType.WHATSAPP, msg_id)
    assert dup_acquired is False

    # PROCESSING -> COMPLETED
    await store.mark_completed(ChannelType.WHATSAPP, msg_id)
    assert (
        await store.get_state(ChannelType.WHATSAPP, msg_id)
        == IdempotencyState.COMPLETED
    )

    # Acquisition after COMPLETED must also be rejected
    completed_acquired = await store.try_acquire(ChannelType.WHATSAPP, msg_id)
    assert completed_acquired is False


@pytest.mark.asyncio
async def test_idempotency_failure_resets_for_retry():
    """Verify failed processing resets state so duplicate/retry can be attempted."""
    store = IdempotencyStore(ttl_seconds=60)
    msg_id = "wamid.HARDEN_FAIL_02"

    acquired = await store.try_acquire(ChannelType.WHATSAPP, msg_id)
    assert acquired is True

    # Processing fails -> reset
    await store.mark_failed(ChannelType.WHATSAPP, msg_id)
    assert await store.get_state(ChannelType.WHATSAPP, msg_id) is None

    # Subsequent retry attempt must succeed
    retry_acquired = await store.try_acquire(ChannelType.WHATSAPP, msg_id)
    assert retry_acquired is True


def test_webhook_body_size_protection(client):
    """Verify payloads exceeding 1MB are rejected with HTTP 413 Payload Too Large."""
    huge_body = b"{" + b"a" * (1024 * 1024 + 10) + b"}"
    response = client.post(
        "/api/v1/messaging/whatsapp/webhook",
        content=huge_body,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 413
    error_msg = response.json().get("detail") or response.json().get("message", "")
    assert "exceeds maximum allowable size" in error_msg


def test_whatsapp_stale_replay_skipped():
    """Verify WhatsApp messages with timestamps older than 24 hours are skipped."""
    adapter = WhatsAppMessagingAdapter()
    stale_payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "contacts": [
                                {"profile": {"name": "Old User"}, "wa_id": "111"}
                            ],
                            "messages": [
                                {
                                    "from": "111",
                                    "id": "wamid.OLD_MSG_99",
                                    "timestamp": "1500000000",  # Year 2017
                                    "text": {"body": "Old stale message"},
                                    "type": "text",
                                }
                            ],
                        }
                    }
                ]
            }
        ],
    }
    messages = adapter.parse_inbound(stale_payload)
    assert messages == []


def test_whatsapp_outbound_truncation():
    """Verify outbound messages exceeding 4096 characters are clamped safely."""
    adapter = WhatsAppMessagingAdapter()
    long_content = "X" * 5000
    outbound = adapter.format_outbound(content=long_content, recipient_id="111")
    assert len(outbound.content) <= 4096
    assert outbound.content.endswith("...")


def test_telegram_outbound_truncation():
    """Verify Telegram messages exceeding 4096 characters are clamped safely."""
    adapter = TelegramMessagingAdapter()
    long_content = "Y" * 5000
    outbound = adapter.format_outbound(content=long_content, recipient_id="222")
    assert len(outbound.content) <= 4096
    assert outbound.content.endswith("...")


@pytest.mark.asyncio
async def test_telegram_markdown_error_fallback():
    """Verify Telegram markdown parse error falls back safely to plain text."""
    adapter = TelegramMessagingAdapter(bot_token="test_token")
    mock_client = AsyncMock()

    # First call returns 400 with Markdown parse error; second call succeeds with 200
    mock_resp_fail = MagicMock(
        status_code=400, text="Bad Request: can't parse entities"
    )
    mock_resp_success = MagicMock(status_code=200, text="ok")
    mock_client.post = AsyncMock(side_effect=[mock_resp_fail, mock_resp_success])

    outbound = adapter.format_outbound(
        content="*Hello _broken markdown",
        recipient_id="222",
    )
    result = await adapter.send_outbound(outbound, client=mock_client)
    assert result is True
    assert mock_client.post.call_count == 2
    # Verify second call stripped parse_mode
    second_call_payload = mock_client.post.call_args_list[1].kwargs["json"]
    assert "parse_mode" not in second_call_payload
