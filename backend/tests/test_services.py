import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from app.exceptions.domain import (
    BookingNotFoundError,
    ConversationClosedError,
    ConversationNotFoundError,
    InvalidBookingStatusError,
    NotificationNotFoundError,
    RecommendationExpiredError,
    RecommendationNotFoundError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.models.booking import Booking
from app.models.conversation import Conversation
from app.models.enums import BookingStatus, ConversationSource, ConversationStatus, NotificationType, RecommendationStatus
from app.models.notification import Notification
from app.models.recommendation import Recommendation
from app.models.user import User
from app.services.booking import BookingService
from app.services.conversation import ConversationService
from app.services.notification import NotificationService
from app.services.recommendation import RecommendationService
from app.services.user import UserService


@pytest.mark.asyncio
async def test_user_service_workflows():
    """Verify UserService create_user, duplicate email validation, get, update, and deactivation."""
    session = AsyncMock()
    session.add = MagicMock()
    service = UserService(session)

    # 1. Create User
    email = f"service_user_{uuid.uuid4()}@example.com"
    service.user_repo.get_by_email = AsyncMock(return_value=None)
    mock_user = User(id=uuid.uuid4(), full_name="Service User", email=email)
    service.user_repo.create = AsyncMock(return_value=mock_user)

    user = await service.create_user(full_name="Service User", email=email)
    assert user.email == email
    assert session.commit.called

    # 2. Duplicate Email Error
    service.user_repo.get_by_email = AsyncMock(return_value=mock_user)
    with pytest.raises(UserAlreadyExistsError):
        await service.create_user(full_name="Duplicate User", email=email)

    # 3. Get User By ID (Found & Not Found)
    service.user_repo.get_by_id = AsyncMock(return_value=mock_user)
    fetched = await service.get_user_by_id(mock_user.id)
    assert fetched == mock_user

    service.user_repo.get_by_id = AsyncMock(return_value=None)
    with pytest.raises(UserNotFoundError):
        await service.get_user_by_id(uuid.uuid4())

    # 4. Deactivate User
    service.user_repo.get_by_id = AsyncMock(return_value=mock_user)
    service.user_repo.delete = AsyncMock(return_value=True)
    res = await service.deactivate_user(mock_user.id)
    assert res is True


@pytest.mark.asyncio
async def test_conversation_service_workflows():
    """Verify ConversationService create, archive, and user verification."""
    session = AsyncMock()
    session.add = MagicMock()
    service = ConversationService(session)

    user_id = uuid.uuid4()
    mock_user = User(id=user_id, full_name="Conv User")
    service.user_repo.get_by_id = AsyncMock(return_value=mock_user)
    service.conversation_repo.get_by_session_id = AsyncMock(return_value=None)

    mock_conv = Conversation(
        id=uuid.uuid4(),
        user_id=user_id,
        session_id="sess_service_1",
        status=ConversationStatus.ACTIVE,
    )
    service.conversation_repo.create = AsyncMock(return_value=mock_conv)

    conv = await service.create_conversation(user_id, "sess_service_1", ConversationSource.WEB)
    assert conv.session_id == "sess_service_1"
    assert session.commit.called

    # Archive conversation
    service.conversation_repo.get_by_id = AsyncMock(return_value=mock_conv)
    mock_archived = Conversation(id=mock_conv.id, status=ConversationStatus.ARCHIVED)
    service.conversation_repo.update = AsyncMock(return_value=mock_archived)

    archived = await service.archive_conversation(mock_conv.id)
    assert archived.status == ConversationStatus.ARCHIVED


@pytest.mark.asyncio
async def test_recommendation_service_workflows():
    """Verify RecommendationService recommendation creation and closed session validation."""
    session = AsyncMock()
    session.add = MagicMock()
    service = RecommendationService(session)

    conv_id = uuid.uuid4()
    mock_active_conv = Conversation(id=conv_id, status=ConversationStatus.ACTIVE)
    service.conversation_repo.get_by_id = AsyncMock(return_value=mock_active_conv)

    mock_rec = Recommendation(id=uuid.uuid4(), conversation_id=conv_id, status=RecommendationStatus.PENDING)
    service.recommendation_repo.create = AsyncMock(return_value=mock_rec)

    rec = await service.create_recommendation(
        conversation_id=conv_id,
        recommendation_type="ride",
        recommendation_data={"option": "Comfort"},
    )
    assert rec.status == RecommendationStatus.PENDING

    # Attempt to create recommendation on archived conversation
    mock_closed_conv = Conversation(id=conv_id, status=ConversationStatus.ARCHIVED)
    service.conversation_repo.get_by_id = AsyncMock(return_value=mock_closed_conv)

    with pytest.raises(ConversationClosedError):
        await service.create_recommendation(
            conversation_id=conv_id,
            recommendation_type="ride",
            recommendation_data={},
        )


@pytest.mark.asyncio
async def test_booking_service_transaction_orchestration():
    """Verify BookingService orchestration across recommendations, bookings, notifications, and transactions."""
    session = AsyncMock()
    session.add = MagicMock()
    service = BookingService(session)

    rec_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    user_id = uuid.uuid4()

    mock_rec = Recommendation(
        id=rec_id,
        conversation_id=conv_id,
        status=RecommendationStatus.PENDING,
    )
    service.recommendation_repo.get_by_id = AsyncMock(return_value=mock_rec)
    service.recommendation_repo.update = AsyncMock(return_value=mock_rec)

    mock_booking = Booking(id=uuid.uuid4(), recommendation_id=rec_id, booking_reference="BK-12345678")
    service.booking_repo.create = AsyncMock(return_value=mock_booking)

    mock_conv = Conversation(id=conv_id, user_id=user_id)
    service.conversation_repo.get_by_id = AsyncMock(return_value=mock_conv)
    service.notification_repo.create = AsyncMock(return_value=MagicMock())

    # 1. Successful Booking Orchestration
    booking = await service.create_booking_from_recommendation(rec_id)
    assert booking.booking_reference == "BK-12345678"
    assert service.recommendation_repo.update.called
    assert service.notification_repo.create.called
    assert session.commit.called

    # 2. Expired Recommendation Error
    mock_expired_rec = Recommendation(id=rec_id, status=RecommendationStatus.EXPIRED)
    service.recommendation_repo.get_by_id = AsyncMock(return_value=mock_expired_rec)
    with pytest.raises(RecommendationExpiredError):
        await service.create_booking_from_recommendation(rec_id)

    # 3. Cancel Booking
    service.booking_repo.get_by_id = AsyncMock(return_value=mock_booking)
    mock_cancelled = Booking(id=mock_booking.id, booking_status=BookingStatus.CANCELLED)
    service.booking_repo.update = AsyncMock(return_value=mock_cancelled)

    cancelled = await service.cancel_booking(mock_booking.id)
    assert cancelled.booking_status == BookingStatus.CANCELLED


@pytest.mark.asyncio
async def test_notification_service_workflows():
    """Verify NotificationService notification creation and mark as read."""
    session = AsyncMock()
    session.add = MagicMock()
    service = NotificationService(session)

    user_id = uuid.uuid4()
    mock_user = User(id=user_id)
    service.user_repo.get_by_id = AsyncMock(return_value=mock_user)

    mock_notif = Notification(id=uuid.uuid4(), user_id=user_id, is_read=False)
    service.notification_repo.create = AsyncMock(return_value=mock_notif)

    notif = await service.create_notification(
        user_id=user_id,
        notification_type=NotificationType.SYSTEM,
        title="Welcome",
        body="Welcome to Volta",
    )
    assert notif.is_read is False

    # Mark as read
    service.notification_repo.get_by_id = AsyncMock(return_value=mock_notif)
    mock_read = Notification(id=mock_notif.id, is_read=True)
    service.notification_repo.update = AsyncMock(return_value=mock_read)

    read_notif = await service.mark_as_read(mock_notif.id)
    assert read_notif.is_read is True
