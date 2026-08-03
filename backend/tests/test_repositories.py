import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from app.models.enums import BookingStatus, ConversationStatus, RecommendationStatus
from app.models.user import User
from app.repositories.base import BaseRepository
from app.repositories.booking import BookingRepository
from app.repositories.conversation import ConversationRepository
from app.repositories.recommendation import RecommendationRepository
from app.repositories.user import UserRepository


@pytest.mark.asyncio
async def test_base_repository_create_and_get():
    """Verify BaseRepository create and get_by_id using an async session."""
    session = AsyncMock()
    session.add = MagicMock()
    repo = BaseRepository(User, session)

    # Test create
    user_id = uuid.uuid4()
    mock_user = User(id=user_id, full_name="Test User", email="test@example.com")

    # Mock execute result for get_by_id
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    session.execute.return_value = mock_result

    fetched = await repo.get_by_id(user_id)
    assert fetched == mock_user
    assert session.execute.called

    # Test create method
    created = await repo.create({"full_name": "New User", "email": "new@example.com"})
    assert isinstance(created, User)
    assert created.full_name == "New User"
    assert session.add.called
    assert session.flush.called
    assert session.refresh.called


@pytest.mark.asyncio
async def test_base_repository_list_and_count():
    """Verify BaseRepository list, count, and exists queries."""
    session = AsyncMock()
    session.add = MagicMock()
    repo = BaseRepository(User, session)

    # Mock count
    count_result = MagicMock()
    count_result.scalar.return_value = 5
    session.execute.return_value = count_result

    cnt = await repo.count()
    assert cnt == 5

    exists = await repo.exists(uuid.uuid4())
    assert exists is True

    # Mock list
    list_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [User(full_name="User 1"), User(full_name="User 2")]
    list_result.scalars.return_value = mock_scalars
    session.execute.return_value = list_result

    items = await repo.list(offset=0, limit=10)
    assert len(items) == 2


@pytest.mark.asyncio
async def test_base_repository_soft_and_hard_delete():
    """Verify soft delete calls soft_delete() and hard delete calls session.delete()."""
    session = AsyncMock()
    session.add = MagicMock()
    repo = BaseRepository(User, session)

    user = User(id=uuid.uuid4(), full_name="Delete Test")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    session.execute.return_value = mock_result

    # Soft delete
    soft_res = await repo.delete(user.id, hard=False)
    assert soft_res is True
    assert user.is_deleted is True

    # Hard delete
    hard_res = await repo.delete(user.id, hard=True)
    assert hard_res is True
    assert session.delete.called


@pytest.mark.asyncio
async def test_user_repository_domain_queries():
    """Verify UserRepository domain methods get_by_email and get_by_phone."""
    session = AsyncMock()
    session.add = MagicMock()
    repo = UserRepository(session)

    mock_user = User(id=uuid.uuid4(), email="john@example.com", phone_number="+15551234567")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    session.execute.return_value = mock_result

    by_email = await repo.get_by_email("john@example.com")
    assert by_email == mock_user

    by_phone = await repo.get_by_phone("+15551234567")
    assert by_phone == mock_user


@pytest.mark.asyncio
async def test_conversation_repository_domain_queries():
    """Verify ConversationRepository domain methods get_latest_active and get_by_session_id."""
    session = AsyncMock()
    session.add = MagicMock()
    repo = ConversationRepository(session)

    mock_conv = MagicMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_conv
    session.execute.return_value = mock_result

    latest = await repo.get_latest_active(uuid.uuid4())
    assert latest == mock_conv

    by_sess = await repo.get_by_session_id("sess_123")
    assert by_sess == mock_conv


@pytest.mark.asyncio
async def test_recommendation_and_booking_repositories():
    """Verify RecommendationRepository and BookingRepository domain queries."""
    session = AsyncMock()
    session.add = MagicMock()
    rec_repo = RecommendationRepository(session)
    bkg_repo = BookingRepository(session)

    # Mock recommendations
    rec_result = MagicMock()
    rec_scalars = MagicMock()
    mock_rec = MagicMock()
    rec_scalars.all.return_value = [mock_rec]
    rec_result.scalars.return_value = rec_scalars
    session.execute.return_value = rec_result

    active_recs = await rec_repo.get_active_recommendations(uuid.uuid4())
    assert active_recs == [mock_rec]

    # Mock booking
    mock_booking = MagicMock()
    bkg_result = MagicMock()
    bkg_result.scalar_one_or_none.return_value = mock_booking
    session.execute.return_value = bkg_result

    by_ref = await bkg_repo.get_by_reference("BK-123")
    assert by_ref == mock_booking
