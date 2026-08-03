import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.services import (
    get_booking_service,
    get_conversation_service,
    get_notification_service,
    get_recommendation_service,
    get_user_service,
)
from app.exceptions.domain import UserAlreadyExistsException, UserNotFoundException
from app.main import app
from app.models.booking import Booking
from app.models.conversation import Conversation
from app.models.enums import BookingStatus, ConversationSource, ConversationStatus, NotificationType, RecommendationStatus
from app.models.notification import Notification
from app.models.recommendation import Recommendation
from app.models.user import User

client = TestClient(app)


def test_users_api_endpoints():
    """Verify Users REST API endpoints and envelope format."""
    mock_user_service = MagicMock()
    user_id = uuid.uuid4()
    mock_user = User(
        id=user_id,
        full_name="API User",
        email="api_user@example.com",
        phone_number="+15550001111",
        preferred_language="en",
        is_active=True,
    )

    # 1. Create User (201 Created)
    mock_user_service.create_user = AsyncMock(return_value=mock_user)
    app.dependency_overrides[get_user_service] = lambda: mock_user_service

    res = client.post(
        "/api/v1/users",
        json={"full_name": "API User", "email": "api_user@example.com"},
    )
    assert res.status_code == 201
    payload = res.json()
    assert payload["success"] is True
    assert payload["data"]["email"] == "api_user@example.com"

    # 2. Get User By ID
    mock_user_service.get_user_by_id = AsyncMock(return_value=mock_user)
    res = client.get(f"/api/v1/users/{user_id}")
    assert res.status_code == 200
    payload = res.json()
    assert payload["data"]["id"] == str(user_id)

    # 3. Update User Profile
    mock_user_service.update_profile = AsyncMock(return_value=mock_user)
    res = client.put(f"/api/v1/users/{user_id}", json={"full_name": "Updated Name"})
    assert res.status_code == 200

    # 4. Deactivate User
    mock_user_service.deactivate_user = AsyncMock(return_value=True)
    res = client.delete(f"/api/v1/users/{user_id}")
    assert res.status_code == 200
    assert res.json()["data"]["deactivated"] is True

    # 5. Validation Error (Invalid Email -> 422)
    res = client.post("/api/v1/users", json={"full_name": "Bad", "email": "invalid-email-str"})
    assert res.status_code == 422

    # Cleanup overrides
    app.dependency_overrides.clear()


def test_domain_exception_translation():
    """Verify domain exceptions raised by services map to correct HTTP envelope status codes."""
    mock_user_service = MagicMock()
    mock_user_service.get_user_by_id = AsyncMock(side_effect=UserNotFoundException("User not found"))
    mock_user_service.create_user = AsyncMock(side_effect=UserAlreadyExistsException("User exists"))
    app.dependency_overrides[get_user_service] = lambda: mock_user_service

    # 404 Not Found
    res = client.get(f"/api/v1/users/{uuid.uuid4()}")
    assert res.status_code == 404
    assert res.json()["success"] is False

    # 409 Conflict
    res = client.post("/api/v1/users", json={"full_name": "Dup", "email": "dup@example.com"})
    assert res.status_code == 409
    assert res.json()["success"] is False

    app.dependency_overrides.clear()


def test_conversations_api_endpoints():
    """Verify Conversations REST API endpoints."""
    mock_service = MagicMock()
    conv_id = uuid.uuid4()
    user_id = uuid.uuid4()
    mock_conv = Conversation(
        id=conv_id,
        user_id=user_id,
        session_id="sess_api_99",
        source=ConversationSource.WEB,
        status=ConversationStatus.ACTIVE,
    )

    mock_service.create_conversation = AsyncMock(return_value=mock_conv)
    mock_service.get_conversation = AsyncMock(return_value=mock_conv)
    mock_service.get_latest_active_conversation = AsyncMock(return_value=mock_conv)
    mock_service.archive_conversation = AsyncMock(return_value=mock_conv)
    app.dependency_overrides[get_conversation_service] = lambda: mock_service

    # POST Create
    res = client.post(
        "/api/v1/conversations",
        json={"user_id": str(user_id), "session_id": "sess_api_99"},
    )
    assert res.status_code == 201

    # GET By ID
    res = client.get(f"/api/v1/conversations/{conv_id}")
    assert res.status_code == 200

    # GET Latest
    res = client.get(f"/api/v1/conversations/latest?user_id={user_id}")
    assert res.status_code == 200

    # DELETE Archive
    res = client.delete(f"/api/v1/conversations/{conv_id}")
    assert res.status_code == 200

    app.dependency_overrides.clear()


def test_recommendations_and_bookings_api_endpoints():
    """Verify Recommendations and Bookings REST API endpoints."""
    rec_service = MagicMock()
    bkg_service = MagicMock()
    rec_id = uuid.uuid4()
    conv_id = uuid.uuid4()

    mock_rec = Recommendation(
        id=rec_id,
        conversation_id=conv_id,
        recommendation_type="ride",
        recommendation_data={"tier": "sedan"},
        status=RecommendationStatus.PENDING,
        confidence_score=0.95,
        ranking=1,
    )
    rec_service.create_recommendation = AsyncMock(return_value=mock_rec)
    rec_service.get_active_recommendations = AsyncMock(return_value=[mock_rec])
    rec_service.get_recommendation = AsyncMock(return_value=mock_rec)
    app.dependency_overrides[get_recommendation_service] = lambda: rec_service

    # Create Recommendation
    res = client.post(
        "/api/v1/recommendations",
        json={
            "conversation_id": str(conv_id),
            "recommendation_type": "ride",
            "recommendation_data": {"tier": "sedan"},
        },
    )
    assert res.status_code == 201

    # Get Active Recommendations
    res = client.get(f"/api/v1/recommendations/active?conversation_id={conv_id}")
    assert res.status_code == 200

    # Booking Service
    bkg_id = uuid.uuid4()
    mock_bkg = Booking(
        id=bkg_id,
        recommendation_id=rec_id,
        booking_reference="BK-API-100",
        booking_status=BookingStatus.CONFIRMED,
        provider="volta_fleet",
    )
    bkg_service.create_booking_from_recommendation = AsyncMock(return_value=mock_bkg)
    bkg_service.get_booking_by_reference = AsyncMock(return_value=mock_bkg)
    bkg_service.cancel_booking = AsyncMock(return_value=mock_bkg)
    app.dependency_overrides[get_booking_service] = lambda: bkg_service

    # Create Booking
    res = client.post("/api/v1/bookings", json={"recommendation_id": str(rec_id)})
    assert res.status_code == 201

    # Get Booking by reference
    res = client.get("/api/v1/bookings/BK-API-100")
    assert res.status_code == 200

    # Cancel Booking
    res = client.patch(f"/api/v1/bookings/{bkg_id}/cancel")
    assert res.status_code == 200

    app.dependency_overrides.clear()


def test_notifications_api_endpoints():
    """Verify Notifications REST API endpoints."""
    notif_service = MagicMock()
    notif_id = uuid.uuid4()
    user_id = uuid.uuid4()

    mock_notif = Notification(
        id=notif_id,
        user_id=user_id,
        notification_type=NotificationType.SYSTEM,
        title="Alert",
        body="Message body",
        is_read=False,
        delivery_status="sent",
    )
    notif_service.create_notification = AsyncMock(return_value=mock_notif)
    notif_service.mark_as_read = AsyncMock(return_value=mock_notif)
    app.dependency_overrides[get_notification_service] = lambda: notif_service

    # Dispatch Notification
    res = client.post(
        "/api/v1/notifications",
        json={
            "user_id": str(user_id),
            "notification_type": "system",
            "title": "Alert",
            "body": "Message body",
        },
    )
    assert res.status_code == 201

    # Mark as Read
    res = client.patch(f"/api/v1/notifications/{notif_id}/read")
    assert res.status_code == 200

    app.dependency_overrides.clear()
