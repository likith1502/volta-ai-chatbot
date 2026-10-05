import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from app.ai.base import AIProvider
from app.ai.models import AIRequest, AIResponse, AITokenUsage
from app.ai.prompts.prompt_builder import PromptBuilder
from app.api.dependencies.services import get_saved_location_service
from app.exceptions.domain import (
    SavedLocationAlreadyExistsException,
    SavedLocationNotFoundException,
)
from app.main import app
from app.models.saved_location import SavedLocation
from app.models.user import User
from app.schemas.saved_location import (
    SavedLocationCreate,
    normalize_label,
)
from app.services.chat import ChatService
from app.services.saved_location import LocationResolver, SavedLocationService
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def client():
    return TestClient(app)


class MockAIProvider(AIProvider):
    """Deterministic mock AI provider for chat integration tests."""

    def __init__(self, response_content: str = "Certainly! Ride confirmed."):
        self.response_content = response_content

    async def generate_response(self, request: AIRequest) -> AIResponse:
        return AIResponse(
            content=self.response_content,
            model_used="gemini-2.5-flash",
            usage=AITokenUsage(prompt_tokens=15, completion_tokens=10, total_tokens=25),
            tool_calls=[],
        )


# ============================================================================
# 1. Label Normalization & Validation Unit Tests
# ============================================================================


def test_label_normalization_and_canonicalization():
    """Verify label whitespace trimming and canonicalization to 'Home' and 'Work'."""
    assert normalize_label("home") == "Home"
    assert normalize_label("Home") == "Home"
    assert normalize_label("HOME") == "Home"
    assert normalize_label("  Home  ") == "Home"
    assert normalize_label("work") == "Work"
    assert normalize_label("Work") == "Work"
    assert normalize_label("WORK") == "Work"
    assert normalize_label("  work  ") == "Work"
    # Arbitrary labels preserved
    assert normalize_label("  Gym  ") == "Gym"
    assert normalize_label("Downtown Office") == "Downtown Office"

    with pytest.raises(ValueError, match="cannot be empty"):
        normalize_label("   ")


def test_coordinate_and_field_validation():
    """Verify strict validation of latitude, longitude, and non-empty addresses."""
    # Valid
    payload = SavedLocationCreate(
        label="Home",
        address="123 Maple Street",
        latitude=37.7749,
        longitude=-122.4194,
    )
    assert payload.latitude == 37.7749
    assert payload.longitude == -122.4194

    # Invalid latitude
    with pytest.raises(ValidationError):
        SavedLocationCreate(
            label="Home", address="123 Maple", latitude=95.0, longitude=0.0
        )

    with pytest.raises(ValidationError):
        SavedLocationCreate(
            label="Home", address="123 Maple", latitude=-95.0, longitude=0.0
        )

    # Invalid longitude
    with pytest.raises(ValidationError):
        SavedLocationCreate(
            label="Home", address="123 Maple", latitude=0.0, longitude=185.0
        )

    with pytest.raises(ValidationError):
        SavedLocationCreate(
            label="Home", address="123 Maple", latitude=0.0, longitude=-185.0
        )

    # Empty or whitespace-only address
    with pytest.raises(ValidationError):
        SavedLocationCreate(label="Home", address="   ")


# ============================================================================
# 2. Service & Repository Workflows: Home & Work Creation, Listing, Updating, Deleting
# ============================================================================


@pytest.mark.asyncio
async def test_saved_location_service_workflows():
    """Verify complete service workflow: create Home, create Work, retrieve, update, and delete."""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    service = SavedLocationService(session)
    user_id = uuid.uuid4()
    mock_user = User(id=user_id, full_name="John Doe", email="john@example.com")
    service.user_repo.get_by_id = AsyncMock(return_value=mock_user)

    # 1. Create Home Location
    service.saved_location_repo.get_by_user_and_label = AsyncMock(return_value=None)
    mock_home = SavedLocation(
        id=uuid.uuid4(),
        user_id=user_id,
        label="Home",
        address="123 Maple Street",
        latitude=37.7749,
        longitude=-122.4194,
    )
    service.saved_location_repo.create = AsyncMock(return_value=mock_home)

    home_loc = await service.create_saved_location(
        user_id=user_id,
        label=" home ",
        address=" 123 Maple Street ",
        latitude=37.7749,
        longitude=-122.4194,
    )
    assert home_loc.label == "Home"
    assert home_loc.address == "123 Maple Street"
    assert session.commit.called

    # 2. Create Work Location
    mock_work = SavedLocation(
        id=uuid.uuid4(),
        user_id=user_id,
        label="Work",
        address="456 Tech Boulevard",
        latitude=37.7833,
        longitude=-122.4167,
    )
    service.saved_location_repo.create = AsyncMock(return_value=mock_work)
    work_loc = await service.create_saved_location(
        user_id=user_id,
        label="WORK",
        address="456 Tech Boulevard",
        latitude=37.7833,
        longitude=-122.4167,
    )
    assert work_loc.label == "Work"

    # 3. Retrieve Saved Locations
    service.saved_location_repo.list_by_user = AsyncMock(
        return_value=[mock_home, mock_work]
    )
    locations = await service.list_saved_locations(user_id=user_id)
    assert len(locations) == 2
    assert locations[0].label == "Home"
    assert locations[1].label == "Work"

    # 4. Update Saved Location
    service.saved_location_repo.get_by_id_and_user = AsyncMock(return_value=mock_home)
    updated = await service.update_saved_location(
        user_id=user_id,
        location_id=mock_home.id,
        update_data={"address": "789 Pine Street", "latitude": 37.8000},
    )
    assert updated.address == "789 Pine Street"
    assert updated.latitude == 37.8000

    # 5. Delete Saved Location (Soft Delete)
    deleted = await service.delete_saved_location(
        user_id=user_id, location_id=mock_home.id
    )
    assert deleted is True
    assert mock_home.is_deleted is True


# ============================================================================
# 3. Duplicate Active Label & Concurrency Protection
# ============================================================================


@pytest.mark.asyncio
async def test_duplicate_active_label_rejection():
    """Verify attempting to create a duplicate active label for the same user is rejected."""
    session = AsyncMock()
    service = SavedLocationService(session)
    user_id = uuid.uuid4()
    mock_user = User(id=user_id, full_name="John Doe", email="john@example.com")
    service.user_repo.get_by_id = AsyncMock(return_value=mock_user)

    # Existing active "Home" location
    mock_existing = SavedLocation(
        id=uuid.uuid4(),
        user_id=user_id,
        label="Home",
        address="Existing Address",
    )
    service.saved_location_repo.get_by_user_and_label = AsyncMock(
        return_value=mock_existing
    )

    with pytest.raises(SavedLocationAlreadyExistsException):
        await service.create_saved_location(
            user_id=user_id,
            label="HOME",
            address="New Address",
        )


@pytest.mark.asyncio
async def test_concurrent_duplicate_catches_integrity_error():
    """Verify database-level integrity error on concurrent race translates to SavedLocationAlreadyExistsException."""
    session = AsyncMock()
    session.add = MagicMock()
    session.rollback = AsyncMock()
    service = SavedLocationService(session)
    user_id = uuid.uuid4()
    mock_user = User(id=user_id, full_name="John Doe", email="john@example.com")
    service.user_repo.get_by_id = AsyncMock(return_value=mock_user)

    service.saved_location_repo.get_by_user_and_label = AsyncMock(return_value=None)
    service.saved_location_repo.create = AsyncMock(
        side_effect=IntegrityError("duplicate", {}, Exception())
    )

    with pytest.raises(SavedLocationAlreadyExistsException):
        await service.create_saved_location(
            user_id=user_id,
            label="Home",
            address="123 Street",
        )
    assert session.rollback.called


# ============================================================================
# 4. Soft-Delete + Recreate Support
# ============================================================================


@pytest.mark.asyncio
async def test_soft_delete_and_recreate_lifecycle():
    """Verify full database lifecycle: create Home -> soft-delete Home -> recreate Home with new address."""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    service = SavedLocationService(session)

    user_id = uuid.uuid4()
    mock_user = User(
        id=user_id, full_name="Lifecycle User", email="lifecycle@example.com"
    )
    service.user_repo.get_by_id = AsyncMock(return_value=mock_user)

    stored_locations: dict[uuid.UUID, SavedLocation] = {}

    async def mock_create(data):
        loc = SavedLocation(
            id=uuid.uuid4(),
            user_id=data["user_id"],
            label=data["label"],
            address=data["address"],
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            is_deleted=False,
        )
        stored_locations[loc.id] = loc
        return loc

    async def mock_get_by_label(*args, **kwargs):
        uid = kwargs.get("user_id") or (args[0] if args else None)
        label = kwargs.get("label") or (args[1] if len(args) > 1 else "")
        inc_del = kwargs.get("include_deleted", False)
        if uid != user_id:
            return None
        cleaned = label.strip().lower()
        for loc in stored_locations.values():
            if loc.user_id == uid and loc.label.strip().lower() == cleaned:
                if inc_del or not loc.is_deleted:
                    return loc
        return None

    async def mock_get_by_id(*args, **kwargs):
        loc_id = kwargs.get("id") or (args[0] if args else None)
        inc_del = kwargs.get("include_deleted", False)
        loc = stored_locations.get(loc_id)
        if loc and (inc_del or not loc.is_deleted):
            return loc
        return None

    async def mock_get_by_id_and_user(*args, **kwargs):
        loc_id = kwargs.get("id") or (args[0] if args else None)
        uid = kwargs.get("user_id") or (args[1] if len(args) > 1 else None)
        inc_del = kwargs.get("include_deleted", False)
        loc = stored_locations.get(loc_id)
        if loc and loc.user_id == uid and (inc_del or not loc.is_deleted):
            return loc
        return None

    async def mock_list_by_user(*args, **kwargs):
        uid = kwargs.get("user_id") or (args[0] if args else None)
        inc_del = kwargs.get("include_deleted", False)
        return [
            loc
            for loc in stored_locations.values()
            if loc.user_id == uid and (inc_del or not loc.is_deleted)
        ]

    service.saved_location_repo.create = AsyncMock(side_effect=mock_create)
    service.saved_location_repo.get_by_user_and_label = AsyncMock(
        side_effect=mock_get_by_label
    )
    service.saved_location_repo.get_by_id_and_user = AsyncMock(
        side_effect=mock_get_by_id_and_user
    )
    service.saved_location_repo.get_by_id = AsyncMock(side_effect=mock_get_by_id)
    service.saved_location_repo.list_by_user = AsyncMock(side_effect=mock_list_by_user)

    # 1. Create Home
    home_1 = await service.create_saved_location(
        user_id=user_id,
        label="Home",
        address="100 First St",
    )
    assert home_1.id is not None
    assert home_1.is_deleted is False

    # 2. Soft-delete Home
    await service.delete_saved_location(user_id=user_id, location_id=home_1.id)
    assert home_1.is_deleted is True

    # 3. Recreate Home with new address
    home_2 = await service.create_saved_location(
        user_id=user_id,
        label="home",
        address="200 Second St",
    )
    assert home_2.id != home_1.id
    assert home_2.label == "Home"
    assert home_2.address == "200 Second St"
    assert home_2.is_deleted is False

    # 4. Verify Active List contains only the new Home
    active_locations = await service.list_saved_locations(user_id=user_id)
    assert len(active_locations) == 1
    assert active_locations[0].id == home_2.id

    # 5. Verify Old Home remains archived in database
    archived_home = await service.saved_location_repo.get_by_id(
        home_1.id, include_deleted=True
    )
    assert archived_home is not None
    assert archived_home.is_deleted is True
    assert archived_home.address == "100 First St"


# ============================================================================
# 5. Deterministic Resolver Tests: Phrases, Case-Insensitivity, Unrelated Labels
# ============================================================================


@pytest.mark.asyncio
async def test_deterministic_location_resolver():
    """Verify resolver handles 'home', 'HOME', ' Home ', 'work', 'WORK', and missing/unrelated queries."""
    session = AsyncMock()
    service = SavedLocationService(session)
    resolver = LocationResolver(service)
    user_id = uuid.uuid4()

    mock_home = SavedLocation(
        id=uuid.uuid4(), user_id=user_id, label="Home", address="123 Home St"
    )
    mock_work = SavedLocation(
        id=uuid.uuid4(), user_id=user_id, label="Work", address="456 Work Blvd"
    )

    async def mock_get_by_label(*args, **kwargs):
        uid = kwargs.get("user_id") or (args[0] if args else None)
        label = kwargs.get("label") or (args[1] if len(args) > 1 else "")
        if uid != user_id:
            return None
        cleaned = label.strip().lower()
        if cleaned == "home":
            return mock_home
        if cleaned == "work":
            return mock_work
        return None

    service.saved_location_repo.get_by_user_and_label = AsyncMock(
        side_effect=mock_get_by_label
    )

    # 1. Resolve 'home'
    loc = await resolver.resolve(user_id, "home")
    assert loc == mock_home

    # 2. Resolve 'HOME'
    loc = await resolver.resolve(user_id, "HOME")
    assert loc == mock_home

    # 3. Resolve '  Home  ' (with whitespace)
    loc = await resolver.resolve(user_id, "  Home  ")
    assert loc == mock_home

    # 4. Resolve 'work'
    loc = await resolver.resolve(user_id, "work")
    assert loc == mock_work

    # 5. Resolve 'WORK'
    loc = await resolver.resolve(user_id, "WORK")
    assert loc == mock_work

    # 6. Unrelated label 'office' -> returns None (does not hallucinate)
    loc = await resolver.resolve(user_id, "office")
    assert loc is None

    # 7. Unrelated label 'gym' -> returns None
    loc = await resolver.resolve(user_id, "gym")
    assert loc is None

    # 8. Empty query -> returns None
    assert await resolver.resolve(user_id, "   ") is None


# ============================================================================
# 6. User Isolation & Security Tests
# ============================================================================


@pytest.mark.asyncio
async def test_user_isolation_prevent_cross_user_access():
    """Verify User A cannot resolve, get, or manipulate User B's saved locations."""
    session = AsyncMock()
    service = SavedLocationService(session)
    user_a = uuid.uuid4()
    user_b = uuid.uuid4()

    mock_user_b_home = SavedLocation(
        id=uuid.uuid4(),
        user_id=user_b,
        label="Home",
        address="User B Home Address",
    )

    # If queried under User A's ID, repository returns None
    service.saved_location_repo.get_by_id_and_user = AsyncMock(return_value=None)
    service.saved_location_repo.get_by_user_and_label = AsyncMock(return_value=None)

    # User A tries to get User B's location by ID -> 404
    with pytest.raises(SavedLocationNotFoundException):
        await service.get_saved_location(
            user_id=user_a, location_id=mock_user_b_home.id
        )

    # User A tries to resolve User B's home -> returns None
    resolved = await service.resolve_location(user_id=user_a, query_label="home")
    assert resolved is None


def test_api_security_authorization_header_mismatch(client):
    """Verify X-User-ID header mismatch against path user_id returns HTTP 403 Forbidden."""
    user_a = uuid.uuid4()
    user_b = uuid.uuid4()

    # Caller passes User A in X-User-ID, but tries to access User B's path
    resp = client.get(
        f"/api/v1/users/{user_b}/saved-locations",
        headers={"X-User-ID": str(user_a)},
    )
    assert resp.status_code == 403
    assert "Forbidden" in resp.json()["message"]


# ============================================================================
# 7. REST API Endpoints Tests
# ============================================================================


def test_saved_locations_api_crud_endpoints(client):
    """Verify complete REST API CRUD operations under /api/v1/users/{user_id}/saved-locations."""
    mock_service = MagicMock()
    user_id = uuid.uuid4()
    location_id = uuid.uuid4()

    mock_loc = SavedLocation(
        id=location_id,
        user_id=user_id,
        label="Home",
        address="123 Maple Street",
        latitude=37.7749,
        longitude=-122.4194,
    )

    # 1. POST / (Create)
    mock_service.create_saved_location = AsyncMock(return_value=mock_loc)
    app.dependency_overrides[get_saved_location_service] = lambda: mock_service

    try:
        res = client.post(
            f"/api/v1/users/{user_id}/saved-locations",
            json={
                "label": "home",
                "address": "123 Maple Street",
                "latitude": 37.7749,
                "longitude": -122.4194,
            },
        )
        assert res.status_code == 201
        assert res.json()["success"] is True
        assert res.json()["data"]["label"] == "Home"

        # 2. GET / (List)
        mock_service.list_saved_locations = AsyncMock(return_value=[mock_loc])
        res = client.get(f"/api/v1/users/{user_id}/saved-locations")
        assert res.status_code == 200
        assert len(res.json()["data"]) == 1

        # 3. GET /{location_id} (Get by ID)
        mock_service.get_saved_location = AsyncMock(return_value=mock_loc)
        res = client.get(f"/api/v1/users/{user_id}/saved-locations/{location_id}")
        assert res.status_code == 200
        assert res.json()["data"]["id"] == str(location_id)

        # 4. PUT /{location_id} (Update)
        updated_mock = SavedLocation(
            id=location_id,
            user_id=user_id,
            label="Home",
            address="789 New Address",
            latitude=37.8000,
            longitude=-122.4000,
        )
        mock_service.update_saved_location = AsyncMock(return_value=updated_mock)
        res = client.put(
            f"/api/v1/users/{user_id}/saved-locations/{location_id}",
            json={"address": "789 New Address", "latitude": 37.8000},
        )
        assert res.status_code == 200
        assert res.json()["data"]["address"] == "789 New Address"

        # 5. DELETE /{location_id} (Soft Delete)
        mock_service.delete_saved_location = AsyncMock(return_value=True)
        res = client.delete(f"/api/v1/users/{user_id}/saved-locations/{location_id}")
        assert res.status_code == 200
        assert res.json()["data"]["deleted"] is True
    finally:
        app.dependency_overrides.pop(get_saved_location_service, None)


# ============================================================================
# 8. Privacy-Preserving Prompt & Chat Integration Tests
# ============================================================================


def test_prompt_builder_injects_only_labels_for_privacy():
    """Verify PromptBuilder formats only labels into user context without raw addresses or coordinates."""
    builder = PromptBuilder()
    home = SavedLocation(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        label="Home",
        address="123 Secret St",
        latitude=10.0,
        longitude=20.0,
    )
    work = SavedLocation(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        label="Work",
        address="456 Private Ave",
        latitude=11.0,
        longitude=21.0,
    )

    ai_request = builder.build(
        user_input="Book me a cab from work to home",
        conversation_history=[],
        memories=[],
        saved_locations=[home, work],
    )

    user_msg = ai_request.messages[-1].content
    assert "[Saved Locations]" in user_msg
    assert "- Home" in user_msg
    assert "- Work" in user_msg
    # Ensure sensitive address and coordinates are NOT exposed to the LLM
    assert "123 Secret St" not in user_msg
    assert "456 Private Ave" not in user_msg
    assert "10.0" not in user_msg


@pytest.mark.asyncio
async def test_chat_service_saved_location_resolution():
    """Verify ChatService resolves 'work' and 'home' deterministically into structured domain records."""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    provider = MockAIProvider(
        response_content="Looking for available electric cabs from Work to Home."
    )
    chat_service = ChatService(session=session, provider=provider)

    user_id = uuid.uuid4()
    mock_user = User(id=user_id, full_name="Alice", email="alice@example.com")
    chat_service.user_repo.get_by_id = AsyncMock(return_value=mock_user)

    mock_home = SavedLocation(
        id=uuid.uuid4(),
        user_id=user_id,
        label="Home",
        address="100 Maple St",
        latitude=37.77,
        longitude=-122.42,
    )
    mock_work = SavedLocation(
        id=uuid.uuid4(),
        user_id=user_id,
        label="Work",
        address="200 Tech Blvd",
        latitude=37.78,
        longitude=-122.41,
    )

    async def mock_resolve_location(*args, **kwargs):
        q = (kwargs.get("query_label") or (args[1] if len(args) > 1 else "")).lower()
        if q == "work":
            return mock_work
        if q == "home":
            return mock_home
        return None

    chat_service.saved_location_service.resolve_location = AsyncMock(
        side_effect=mock_resolve_location
    )

    # 1. Resolve 'work' deterministically
    resolved_work = await chat_service.resolve_user_location(user_id, "work")
    assert resolved_work is not None
    assert resolved_work.label == "Work"
    assert resolved_work.address == "200 Tech Blvd"
    assert resolved_work.latitude == 37.78

    # 2. Resolve 'home' deterministically
    resolved_home = await chat_service.resolve_user_location(user_id, "home")
    assert resolved_home is not None
    assert resolved_home.label == "Home"
    assert resolved_home.address == "100 Maple St"

    # 3. Missing location returns None without error
    resolved_gym = await chat_service.resolve_user_location(user_id, "gym")
    assert resolved_gym is None


# ============================================================================
# 9. Integration Contract Test
# ============================================================================


@pytest.mark.asyncio
async def test_saved_location_integration_contract():
    """Verify integration contract: user_id -> saved location lookup -> structured location object."""
    session = AsyncMock()
    service = SavedLocationService(session)
    resolver = LocationResolver(service)

    contract_user_id = uuid.uuid4()
    expected_location_id = uuid.uuid4()
    contract_location = SavedLocation(
        id=expected_location_id,
        user_id=contract_user_id,
        label="Work",
        address="456 Innovation Way, Suite 300",
        latitude=12.9716,
        longitude=77.5946,
    )

    service.saved_location_repo.get_by_user_and_label = AsyncMock(
        return_value=contract_location
    )

    # Execute contract lookup
    resolved = await resolver.resolve(contract_user_id, "Work")

    # Verify structured location object guarantees
    assert resolved is not None
    assert resolved.id == expected_location_id
    assert resolved.user_id == contract_user_id
    assert resolved.label == "Work"
    assert resolved.address == "456 Innovation Way, Suite 300"
    assert resolved.latitude == 12.9716
    assert resolved.longitude == 77.5946

    # Verify downstream booking payload compatibility
    booking_pickup_payload = {
        "pickup_location_id": str(resolved.id),
        "pickup_address": resolved.address,
        "pickup_coordinates": (resolved.latitude, resolved.longitude),
    }
    assert booking_pickup_payload["pickup_location_id"] == str(expected_location_id)
    assert booking_pickup_payload["pickup_address"] == "456 Innovation Way, Suite 300"
    assert booking_pickup_payload["pickup_coordinates"] == (12.9716, 77.5946)
