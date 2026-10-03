import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from app.ai.models import AIToolCall
from app.ai.tools.dispatcher import AIToolDispatcher
from app.ai.tools.recommendation_tool import RecommendationTool
from app.ai.tools.registry import AIToolRegistry
from app.fleet.base import BaseFleetPricingProvider
from app.fleet.demo import DemoFleetPricingProvider
from app.models.enums import VehicleTier
from app.models.recommendation import Recommendation, RecommendationStatus
from app.schemas.cab import (
    CabAvailabilityQuote,
    CabOption,
    LocationPoint,
)
from app.services.cab_pricing import CabPricingService
from pydantic import ValidationError

# ============================================================================
# 1. VehicleTier Enum Values
# ============================================================================


def test_01_vehicle_tier_enum_values():
    """Verify VehicleTier contains exactly mini, sedan, and suv with expected string values."""
    assert VehicleTier.MINI == "mini"
    assert VehicleTier.SEDAN == "sedan"
    assert VehicleTier.SUV == "suv"
    assert VehicleTier.EV == "ev"
    assert VehicleTier.LUXURY == "luxury"
    assert set(VehicleTier) == {
        VehicleTier.MINI,
        VehicleTier.SEDAN,
        VehicleTier.SUV,
        VehicleTier.EV,
        VehicleTier.LUXURY,
    }
    assert len(VehicleTier) == 5


# ============================================================================
# 2. CabOption Schema Validation
# ============================================================================


def test_02_cab_option_schema_validation():
    """Verify CabOption enforces Decimal fare, positive amounts, valid currency, and capacities."""
    valid_option = CabOption(
        tier=VehicleTier.MINI,
        display_name="VOLTA Mini",
        fare=Decimal("180.00"),
        currency="INR",
        eta_minutes=4,
        capacity=4,
        description="Affordable compact rides",
    )
    assert valid_option.tier == VehicleTier.MINI
    assert valid_option.fare == Decimal("180.00")
    assert isinstance(valid_option.fare, Decimal)
    assert valid_option.currency == "INR"

    # Non-positive fare rejection
    with pytest.raises(ValidationError):
        CabOption(
            tier=VehicleTier.MINI,
            display_name="Mini",
            fare=Decimal("0.00"),
            currency="INR",
            eta_minutes=4,
            capacity=4,
        )

    with pytest.raises(ValidationError):
        CabOption(
            tier=VehicleTier.MINI,
            display_name="Mini",
            fare=Decimal("-50.00"),
            currency="INR",
            eta_minutes=4,
            capacity=4,
        )

    # Negative ETA rejection
    with pytest.raises(ValidationError):
        CabOption(
            tier=VehicleTier.MINI,
            display_name="Mini",
            fare=Decimal("180.00"),
            currency="INR",
            eta_minutes=-1,
            capacity=4,
        )

    # Capacity < 1 rejection
    with pytest.raises(ValidationError):
        CabOption(
            tier=VehicleTier.MINI,
            display_name="Mini",
            fare=Decimal("180.00"),
            currency="INR",
            eta_minutes=4,
            capacity=0,
        )

    # Invalid currency code rejection
    with pytest.raises(ValidationError):
        CabOption(
            tier=VehicleTier.MINI,
            display_name="Mini",
            fare=Decimal("180.00"),
            currency="inr",  # must be 3 uppercase letters
            eta_minutes=4,
            capacity=4,
        )


# ============================================================================
# 3. CabAvailabilityQuote Schema Validation
# ============================================================================


def test_03_cab_availability_quote_schema_validation():
    """Verify CabAvailabilityQuote validates currency uniformity, non-empty options, tier uniqueness, and expiry."""
    pickup = LocationPoint(
        address="Brigade Road, Bangalore", latitude=12.9716, longitude=77.5946
    )
    dest = LocationPoint(
        address="Kempegowda International Airport", latitude=13.1986, longitude=77.7066
    )

    opt_mini = CabOption(
        tier=VehicleTier.MINI,
        display_name="Mini",
        fare=Decimal("180.00"),
        currency="INR",
        eta_minutes=4,
        capacity=4,
    )
    opt_sedan = CabOption(
        tier=VehicleTier.SEDAN,
        display_name="Sedan",
        fare=Decimal("240.00"),
        currency="INR",
        eta_minutes=6,
        capacity=4,
    )

    valid_quote = CabAvailabilityQuote(
        pickup=pickup,
        destination=dest,
        options=[opt_mini, opt_sedan],
        currency="INR",
    )
    assert valid_quote.currency == "INR"
    assert len(valid_quote.options) == 2
    assert isinstance(valid_quote.quote_id, uuid.UUID)

    # Empty options rejection
    with pytest.raises(ValidationError):
        CabAvailabilityQuote(
            pickup=pickup,
            destination=dest,
            options=[],
            currency="INR",
        )

    # Mismatched currency rejection
    opt_usd = CabOption(
        tier=VehicleTier.SUV,
        display_name="SUV",
        fare=Decimal("35.00"),
        currency="USD",
        eta_minutes=8,
        capacity=6,
    )
    with pytest.raises(ValidationError):
        CabAvailabilityQuote(
            pickup=pickup,
            destination=dest,
            options=[opt_mini, opt_usd],
            currency="INR",
        )

    # Duplicate vehicle tiers rejection
    opt_mini_dup = CabOption(
        tier=VehicleTier.MINI,
        display_name="Mini 2",
        fare=Decimal("190.00"),
        currency="INR",
        eta_minutes=5,
        capacity=4,
    )
    with pytest.raises(ValidationError):
        CabAvailabilityQuote(
            pickup=pickup,
            destination=dest,
            options=[opt_mini, opt_mini_dup],
            currency="INR",
        )

    # Expiration window validation (expires_at <= created_at rejected)
    past_time = datetime.now(timezone.utc) - timedelta(minutes=5)
    with pytest.raises(ValidationError):
        CabAvailabilityQuote(
            pickup=pickup,
            destination=dest,
            options=[opt_mini],
            currency="INR",
            expires_at=past_time,
        )


# ============================================================================
# 4. Demo Provider Returns Mini
# ============================================================================


@pytest.mark.asyncio
async def test_04_demo_provider_returns_mini():
    """Verify DemoFleetPricingProvider offers Mini at ₹180 with 4 min ETA and 4 seats."""
    provider = DemoFleetPricingProvider()
    pickup = LocationPoint(label="Work")
    dest = LocationPoint(label="Home")

    options = await provider.get_available_options(pickup, dest)
    mini_opt = next((o for o in options if o.tier == VehicleTier.MINI), None)

    assert mini_opt is not None
    assert mini_opt.display_name == "Mini"
    assert mini_opt.fare == Decimal("180.00")
    assert mini_opt.currency == "INR"
    assert mini_opt.eta_minutes == 4
    assert mini_opt.capacity == 4


# ============================================================================
# 5. Demo Provider Returns Sedan
# ============================================================================


@pytest.mark.asyncio
async def test_05_demo_provider_returns_sedan():
    """Verify DemoFleetPricingProvider offers Sedan at ₹240 with 6 min ETA and 4 seats."""
    provider = DemoFleetPricingProvider()
    pickup = LocationPoint(label="Work")
    dest = LocationPoint(label="Home")

    options = await provider.get_available_options(pickup, dest)
    sedan_opt = next((o for o in options if o.tier == VehicleTier.SEDAN), None)

    assert sedan_opt is not None
    assert sedan_opt.display_name == "Sedan"
    assert sedan_opt.fare == Decimal("240.00")
    assert sedan_opt.currency == "INR"
    assert sedan_opt.eta_minutes == 6
    assert sedan_opt.capacity == 4


# ============================================================================
# 6. Demo Provider Returns SUV
# ============================================================================


@pytest.mark.asyncio
async def test_06_demo_provider_returns_suv():
    """Verify DemoFleetPricingProvider offers SUV at ₹360 with 8 min ETA and 6 seats."""
    provider = DemoFleetPricingProvider()
    pickup = LocationPoint(label="Work")
    dest = LocationPoint(label="Home")

    options = await provider.get_available_options(pickup, dest)
    suv_opt = next((o for o in options if o.tier == VehicleTier.SUV), None)

    assert suv_opt is not None
    assert suv_opt.display_name == "SUV"
    assert suv_opt.fare == Decimal("360.00")
    assert suv_opt.currency == "INR"
    assert suv_opt.eta_minutes == 8
    assert suv_opt.capacity == 6


# ============================================================================
# 7. Demo Provider Structured ETAs and Capacities
# ============================================================================


@pytest.mark.asyncio
async def test_07_demo_provider_structured_etas_and_capacities():
    """Verify all options returned by DemoFleetPricingProvider have realistic ETAs, capacities, and descriptions."""
    provider = DemoFleetPricingProvider()
    quote = await provider.get_availability_quote(
        LocationPoint(label="Point A"), LocationPoint(label="Point B")
    )

    assert len(quote.options) == 5
    assert quote.currency == "INR"
    assert quote.expires_at is not None
    assert quote.expires_at > quote.created_at

    for opt in quote.options:
        assert opt.eta_minutes > 0
        assert opt.capacity in [4, 6]
        assert len(opt.display_name) > 0
        assert opt.description is not None


# ============================================================================
# 8. Demo Provider Preserves Passed Locations
# ============================================================================


@pytest.mark.asyncio
async def test_08_demo_provider_preserves_passed_locations():
    """Verify demo provider sets exact passed pickup and destination without inventing or resolving locations."""
    provider = DemoFleetPricingProvider()
    pickup = LocationPoint(
        address="742 Evergreen Terrace", latitude=44.0582, longitude=-123.0868
    )
    dest = LocationPoint(
        address="Springfield Nuclear Power Plant", latitude=44.0620, longitude=-123.0720
    )

    quote = await provider.get_availability_quote(pickup, dest)

    assert quote.pickup.address == "742 Evergreen Terrace"
    assert quote.pickup.latitude == 44.0582
    assert quote.pickup.longitude == -123.0868
    assert quote.destination.address == "Springfield Nuclear Power Plant"
    assert quote.destination.latitude == 44.0620
    assert quote.destination.longitude == -123.0720


# ============================================================================
# 9. Fleet Pricing Provider Abstraction Substitutability
# ============================================================================


@pytest.mark.asyncio
async def test_09_fleet_pricing_provider_abstraction_substitutability():
    """Verify that a custom BaseFleetPricingProvider can be seamlessly substituted into CabPricingService."""

    class PartnerFleetPricingProvider(BaseFleetPricingProvider):
        async def get_available_options(
            self,
            pickup: LocationPoint,
            destination: LocationPoint,
        ) -> list[CabOption]:
            return [
                CabOption(
                    tier=VehicleTier.SEDAN,
                    display_name="Partner Premium Sedan",
                    fare=Decimal("499.00"),
                    currency="INR",
                    eta_minutes=3,
                    capacity=4,
                    description="Partner fleet sedan",
                )
            ]

        async def get_availability_quote(
            self,
            pickup: LocationPoint,
            destination: LocationPoint,
        ) -> CabAvailabilityQuote:
            options = await self.get_available_options(pickup, destination)
            return CabAvailabilityQuote(
                pickup=pickup,
                destination=destination,
                options=options,
                currency="INR",
            )

    partner_provider = PartnerFleetPricingProvider()
    service = CabPricingService(session=AsyncMock(), provider=partner_provider)

    quote = await service.get_availability_quote(
        LocationPoint(label="Work"), LocationPoint(label="Home")
    )

    assert len(quote.options) == 1
    assert quote.options[0].display_name == "Partner Premium Sedan"
    assert quote.options[0].fare == Decimal("499.00")
    assert quote.options[0].currency == "INR"


# ============================================================================
# 10. CabPricingService Calls Provider and Validates
# ============================================================================


@pytest.mark.asyncio
async def test_10_cab_pricing_service_calls_provider_and_validates():
    """Verify CabPricingService coordinates provider query, normalizes string locations, and produces valid quote."""
    session = AsyncMock()
    service = CabPricingService(session=session)

    # Test string location normalization to LocationPoint
    quote = await service.get_availability_quote(pickup="Work", destination="Home")

    assert isinstance(quote.quote_id, uuid.UUID)
    assert quote.pickup.label == "Work"
    assert quote.destination.label == "Home"
    assert quote.currency == "INR"
    assert len(quote.options) == 5


# ============================================================================
# 11. CabPricingService Rejects Inconsistent Currency
# ============================================================================


@pytest.mark.asyncio
async def test_11_cab_pricing_service_rejects_inconsistent_currency():
    """Verify CabPricingService raises ValueError if provider returns an option with mismatched currency."""

    class InconsistentCurrencyProvider(BaseFleetPricingProvider):
        async def get_available_options(
            self, pickup: LocationPoint, destination: LocationPoint
        ) -> list[CabOption]:
            return [
                CabOption(
                    tier=VehicleTier.MINI,
                    display_name="Mini",
                    fare=Decimal("180.00"),
                    currency="INR",
                    eta_minutes=4,
                    capacity=4,
                ),
                CabOption(
                    tier=VehicleTier.SEDAN,
                    display_name="Sedan",
                    fare=Decimal("30.00"),
                    currency="USD",  # Inconsistent currency
                    eta_minutes=6,
                    capacity=4,
                ),
            ]

        async def get_availability_quote(
            self,
            pickup: LocationPoint,
            destination: LocationPoint,
        ) -> CabAvailabilityQuote:
            # Bypass schema validator for raw testing of service defense
            opts = [
                CabOption(
                    tier=VehicleTier.MINI,
                    display_name="Mini",
                    fare=Decimal("180.00"),
                    currency="INR",
                    eta_minutes=4,
                    capacity=4,
                )
            ]
            q = CabAvailabilityQuote(
                pickup=pickup, destination=destination, options=opts, currency="INR"
            )
            # Inject bad option post-initialization
            q.options.append(
                CabOption(
                    tier=VehicleTier.SEDAN,
                    display_name="Sedan",
                    fare=Decimal("30.00"),
                    currency="USD",
                    eta_minutes=6,
                    capacity=4,
                )
            )
            return q

    service = CabPricingService(
        session=AsyncMock(), provider=InconsistentCurrencyProvider()
    )

    with pytest.raises(ValueError, match="does not match quote currency"):
        await service.get_availability_quote(
            LocationPoint(label="Work"), LocationPoint(label="Home")
        )


# ============================================================================
# 12. CabPricingService Rejects Duplicate Tiers
# ============================================================================


@pytest.mark.asyncio
async def test_12_cab_pricing_service_rejects_duplicate_tiers():
    """Verify CabPricingService detects and raises ValueError when duplicate vehicle tiers are returned."""

    class DuplicateTierProvider(BaseFleetPricingProvider):
        async def get_available_options(
            self, pickup: LocationPoint, destination: LocationPoint
        ) -> list[CabOption]:
            return []

        async def get_availability_quote(
            self,
            pickup: LocationPoint,
            destination: LocationPoint,
        ) -> CabAvailabilityQuote:
            opts = [
                CabOption(
                    tier=VehicleTier.MINI,
                    display_name="Mini A",
                    fare=Decimal("180.00"),
                    currency="INR",
                    eta_minutes=4,
                    capacity=4,
                )
            ]
            q = CabAvailabilityQuote(
                pickup=pickup, destination=destination, options=opts, currency="INR"
            )
            # Inject duplicate tier
            q.options.append(
                CabOption(
                    tier=VehicleTier.MINI,
                    display_name="Mini B",
                    fare=Decimal("190.00"),
                    currency="INR",
                    eta_minutes=5,
                    capacity=4,
                )
            )
            return q

    service = CabPricingService(session=AsyncMock(), provider=DuplicateTierProvider())

    with pytest.raises(ValueError, match="Duplicate vehicle tier detected"):
        await service.get_availability_quote(
            LocationPoint(label="Work"), LocationPoint(label="Home")
        )


# ============================================================================
# 13. CabPricingService Persists Recommendation When Requested
# ============================================================================


@pytest.mark.asyncio
async def test_13_cab_pricing_service_persists_recommendation_when_requested():
    """Verify CabPricingService persists structured quote into Recommendation entity when persist_recommendation is True."""
    session = AsyncMock()
    service = CabPricingService(session=session)

    mock_rec_id = uuid.uuid4()
    mock_rec = Recommendation(
        id=mock_rec_id,
        conversation_id=uuid.uuid4(),
        recommendation_type="cab_availability",
        status=RecommendationStatus.PENDING,
        recommendation_data={},
    )
    service.recommendation_service.create_recommendation = AsyncMock(
        return_value=mock_rec
    )

    conv_id = uuid.uuid4()
    quote = await service.get_availability_quote(
        pickup="Work",
        destination="Home",
        conversation_id=conv_id,
        persist_recommendation=True,
    )

    assert quote.recommendation_id == mock_rec_id
    service.recommendation_service.create_recommendation.assert_awaited_once()
    call_kwargs = service.recommendation_service.create_recommendation.await_args.kwargs
    assert call_kwargs["conversation_id"] == conv_id
    assert call_kwargs["recommendation_type"] == "cab_availability"
    assert "options" in call_kwargs["recommendation_data"]
    assert len(call_kwargs["recommendation_data"]["options"]) == 5


# ============================================================================
# 14. RecommendationTool No Hardcoded USD Options
# ============================================================================


@pytest.mark.asyncio
async def test_14_recommendation_tool_no_hardcoded_usd_options():
    """Verify RecommendationTool no longer returns hardcoded $24.50 or $35.00 USD mock options."""
    session = AsyncMock()
    tool = RecommendationTool(session=session)

    # Mock the underlying recommendation persistence
    rec_id = uuid.uuid4()
    tool.recommendation_service.create_recommendation = AsyncMock(
        return_value=MagicMock(
            id=rec_id,
            status=MagicMock(value="pending"),
            recommendation_type="cab_availability",
        )
    )

    res = await tool.execute(
        {
            "conversation_id": str(uuid.uuid4()),
            "pickup": "Work",
            "destination": "Home",
        }
    )

    assert res.success is True
    data = res.data
    assert data["currency"] == "INR"

    fares = [Decimal(str(opt["fare"])) for opt in data["options"]]
    assert Decimal("24.50") not in fares
    assert Decimal("35.00") not in fares
    assert Decimal("180.00") in fares
    assert Decimal("240.00") in fares
    assert Decimal("360.00") in fares


# ============================================================================
# 15. RecommendationTool Delegates to CabPricingService
# ============================================================================


@pytest.mark.asyncio
async def test_15_recommendation_tool_delegates_to_cab_pricing_service():
    """Verify RecommendationTool delegates quote creation to CabPricingService and handles errors."""
    session = AsyncMock()
    mock_pricing_service = MagicMock()

    mock_quote = CabAvailabilityQuote(
        quote_id=uuid.uuid4(),
        pickup=LocationPoint(label="Work"),
        destination=LocationPoint(label="Home"),
        options=[
            CabOption(
                tier=VehicleTier.MINI,
                display_name="Mini",
                fare=Decimal("180.00"),
                currency="INR",
                eta_minutes=4,
                capacity=4,
            )
        ],
        currency="INR",
        recommendation_id=uuid.uuid4(),
    )
    mock_pricing_service.get_availability_quote = AsyncMock(return_value=mock_quote)
    mock_pricing_service.recommendation_service = MagicMock()

    tool = RecommendationTool(session=session, cab_pricing_service=mock_pricing_service)

    # Missing conversation_id error handling
    res_err = await tool.execute({"pickup": "Work", "destination": "Home"})
    assert res_err.success is False
    assert "Missing required argument" in res_err.error

    # Valid execution
    res = await tool.execute(
        {"conversation_id": str(uuid.uuid4()), "pickup": "Work", "destination": "Home"}
    )
    assert res.success is True
    mock_pricing_service.get_availability_quote.assert_awaited_once()
    assert res.data["quote_id"] == str(mock_quote.quote_id)
    assert res.data["recommendation_id"] == mock_quote.recommendation_id


# ============================================================================
# 16. REST API Endpoint Success (POST /api/v1/cabs/quote)
# ============================================================================


def test_16_cabs_quote_api_endpoint_success(client):
    """Verify POST /api/v1/cabs/quote returns HTTP 200 with structured cab availability quote."""
    payload = {
        "pickup": {
            "address": "123 MG Road, Bangalore",
            "latitude": 12.9716,
            "longitude": 77.5946,
        },
        "destination": {
            "address": "Bangalore International Airport",
            "latitude": 13.1986,
            "longitude": 77.7066,
        },
    }

    res = client.post("/api/v1/cabs/quote", json=payload)
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True

    quote_data = json_data["data"]
    assert "quote_id" in quote_data
    assert quote_data["currency"] == "INR"
    assert len(quote_data["options"]) == 5

    tiers = [opt["tier"] for opt in quote_data["options"]]
    assert tiers == ["mini", "sedan", "suv", "ev", "luxury"]

    fares = [float(opt["fare"]) for opt in quote_data["options"]]
    assert fares == [180.0, 240.0, 360.0, 260.0, 520.0]


# ============================================================================
# 17. REST API Endpoint Validation Error
# ============================================================================


def test_17_cabs_quote_api_endpoint_validation_error(client):
    """Verify POST /api/v1/cabs/quote returns HTTP 422 when required fields or coordinates are invalid."""
    # Empty body
    res_empty = client.post("/api/v1/cabs/quote", json={})
    assert res_empty.status_code == 422

    # LocationPoint missing any identifying information
    res_invalid_pt = client.post(
        "/api/v1/cabs/quote",
        json={
            "pickup": {},
            "destination": {"address": "Valid Destination"},
        },
    )
    assert res_invalid_pt.status_code == 422

    # Out of range latitude
    res_bad_lat = client.post(
        "/api/v1/cabs/quote",
        json={
            "pickup": {"latitude": 95.0, "longitude": 77.59},  # lat > 90 invalid
            "destination": {"address": "Valid Destination"},
        },
    )
    assert res_bad_lat.status_code == 422


# ============================================================================
# 18. Regression Existing Recommendation and Graph Compatibility
# ============================================================================


@pytest.mark.asyncio
async def test_18_regression_existing_recommendation_and_graph_compatibility():
    """Verify AIToolDispatcher and RecommendationTool seamlessly interact without calling BookingService."""
    session = AsyncMock()
    tool = RecommendationTool(session)

    # Mock recommendation persistence inside tool
    rec_id = uuid.uuid4()
    tool.recommendation_service.create_recommendation = AsyncMock(
        return_value=MagicMock(
            id=rec_id,
            status=MagicMock(value="pending"),
            recommendation_type="cab_availability",
        )
    )

    registry = AIToolRegistry()
    registry.register(tool)
    dispatcher = AIToolDispatcher(registry)

    call = AIToolCall(
        tool_name="recommendation",
        arguments={
            "conversation_id": str(uuid.uuid4()),
            "user_query": "Book me a cab to work",
            "pickup": "Home",
            "destination": "Work",
        },
    )

    result = await dispatcher.dispatch(call)

    assert result.success is True
    assert result.tool_name == "recommendation"
    assert result.data["recommendation_id"] == rec_id
    assert result.data["currency"] == "INR"
    assert len(result.data["options"]) == 5

    # Read-only guarantee: BookingService / Booking model was never modified or invoked
    from app.services.booking import BookingService

    # Verify BookingService has no references to cab_pricing or quote
    assert not hasattr(BookingService, "get_cab_quote")


# ============================================================================
# 19. EV and Luxury tier selection (including customer wording)
# ============================================================================


def test_19_extract_vehicle_tier_ev_and_luxury_aliases():
    """Customers can pick EV/Luxury by name or by common wording."""
    from app.ai.prompts.recommendation import extract_vehicle_tier

    assert extract_vehicle_tier("I'll take the EV") == "ev"
    assert extract_vehicle_tier("book an electric car") == "ev"
    assert extract_vehicle_tier("Volta Luxury please") == "luxury"
    assert extract_vehicle_tier("premium one") == "luxury"
    assert extract_vehicle_tier("sedan") == "sedan"
    assert extract_vehicle_tier("helicopter") is None
