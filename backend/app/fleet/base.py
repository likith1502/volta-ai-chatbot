from abc import ABC, abstractmethod

from app.schemas.cab import CabAvailabilityQuote, CabOption, LocationPoint


class BaseFleetPricingProvider(ABC):
    """Abstract interface for fleet availability and dynamic pricing providers.

    Implementations query dispatch telematics, driver positioning, and pricing
    engines to produce vehicle tier options and time-bounded availability quotes.
    Providers are purely domain-focused and decoupled from HTTP, web frameworks,
    and conversational state.
    """

    @abstractmethod
    async def get_available_options(
        self,
        pickup: LocationPoint,
        destination: LocationPoint,
    ) -> list[CabOption]:
        """Queries available vehicle options, fares, and ETAs for given route."""
        pass

    @abstractmethod
    async def get_availability_quote(
        self,
        pickup: LocationPoint,
        destination: LocationPoint,
    ) -> CabAvailabilityQuote:
        """Constructs a time-bounded availability quote for given pickup and destination."""
        pass
