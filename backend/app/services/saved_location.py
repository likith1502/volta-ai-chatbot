import logging
import uuid
from typing import Any, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.domain import (
    SavedLocationAlreadyExistsException,
    SavedLocationNotFoundException,
    UserNotFoundException,
)
from app.models.saved_location import SavedLocation
from app.repositories.saved_location import SavedLocationRepository
from app.repositories.user import UserRepository
from app.schemas.saved_location import normalize_label
from app.services.base import BaseService

logger = logging.getLogger("app.services.saved_location")


class SavedLocationService(BaseService):
    """Application service for managing user saved locations and address resolution."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.saved_location_repo = SavedLocationRepository(session)
        self.user_repo = UserRepository(session)

    async def create_saved_location(
        self,
        user_id: uuid.UUID,
        label: str,
        address: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> SavedLocation:
        """Creates and persists a canonical saved location for a verified user."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"User with ID '{user_id}' not found.")

        normalized_label = normalize_label(label)
        cleaned_address = address.strip()
        if not cleaned_address:
            raise ValueError("Address cannot be empty or whitespace-only.")

        if latitude is not None and not (-90.0 <= latitude <= 90.0):
            raise ValueError(f"Latitude '{latitude}' out of valid range [-90.0, 90.0].")
        if longitude is not None and not (-180.0 <= longitude <= 180.0):
            raise ValueError(
                f"Longitude '{longitude}' out of valid range [-180.0, 180.0]."
            )

        # Application-level duplicate check
        existing = await self.saved_location_repo.get_by_user_and_label(
            user_id=user_id,
            label=normalized_label,
            include_deleted=False,
        )
        if existing:
            raise SavedLocationAlreadyExistsException(
                f"A saved location with label '{normalized_label}' already exists for this user."
            )

        try:
            saved_loc = await self.saved_location_repo.create(
                {
                    "user_id": user_id,
                    "label": normalized_label,
                    "address": cleaned_address,
                    "latitude": latitude,
                    "longitude": longitude,
                }
            )
            await self.commit()
            return saved_loc
        except IntegrityError as exc:
            await self.rollback()
            logger.warning(
                "Database unique constraint caught duplicate saved location: %s", exc
            )
            raise SavedLocationAlreadyExistsException(
                f"A saved location with label '{normalized_label}' already exists for this user."
            ) from exc

    async def list_saved_locations(self, user_id: uuid.UUID) -> list[SavedLocation]:
        """Lists all active saved locations for a specific user."""
        return await self.saved_location_repo.list_by_user(user_id=user_id)

    async def get_saved_location(
        self,
        user_id: uuid.UUID,
        location_id: uuid.UUID,
    ) -> SavedLocation:
        """Retrieves a single saved location scoped strictly to the owning user."""
        loc = await self.saved_location_repo.get_by_id_and_user(
            id=location_id,
            user_id=user_id,
            include_deleted=False,
        )
        if not loc:
            raise SavedLocationNotFoundException(
                f"Saved location '{location_id}' not found for user '{user_id}'."
            )
        return loc

    async def update_saved_location(
        self,
        user_id: uuid.UUID,
        location_id: uuid.UUID,
        update_data: dict[str, Any],
    ) -> SavedLocation:
        """Updates attributes of a user's saved location with validation and uniqueness checks."""
        loc = await self.get_saved_location(user_id=user_id, location_id=location_id)

        clean_updates: dict[str, Any] = {}

        if "label" in update_data and update_data["label"] is not None:
            new_label = normalize_label(update_data["label"])
            if new_label.lower() != loc.label.lower():
                existing = await self.saved_location_repo.get_by_user_and_label(
                    user_id=user_id,
                    label=new_label,
                    include_deleted=False,
                )
                if existing and existing.id != loc.id:
                    raise SavedLocationAlreadyExistsException(
                        f"A saved location with label '{new_label}' already exists for this user."
                    )
            clean_updates["label"] = new_label

        if "address" in update_data and update_data["address"] is not None:
            cleaned_addr = update_data["address"].strip()
            if not cleaned_addr:
                raise ValueError("Address cannot be empty or whitespace-only.")
            clean_updates["address"] = cleaned_addr

        if "latitude" in update_data:
            lat = update_data["latitude"]
            if lat is not None and not (-90.0 <= lat <= 90.0):
                raise ValueError(f"Latitude '{lat}' out of valid range [-90.0, 90.0].")
            clean_updates["latitude"] = lat

        if "longitude" in update_data:
            lon = update_data["longitude"]
            if lon is not None and not (-180.0 <= lon <= 180.0):
                raise ValueError(
                    f"Longitude '{lon}' out of valid range [-180.0, 180.0]."
                )
            clean_updates["longitude"] = lon

        for key, val in clean_updates.items():
            setattr(loc, key, val)

        try:
            await self.commit()
            await self.session.refresh(loc)
            return loc
        except IntegrityError as exc:
            await self.rollback()
            raise SavedLocationAlreadyExistsException(
                "Updating saved location caused a conflict with another active location."
            ) from exc

    async def delete_saved_location(
        self,
        user_id: uuid.UUID,
        location_id: uuid.UUID,
    ) -> bool:
        """Performs logical soft-delete archiving of a saved location."""
        loc = await self.get_saved_location(user_id=user_id, location_id=location_id)
        loc.soft_delete()
        await self.commit()
        return True

    async def resolve_location(
        self,
        user_id: uuid.UUID,
        query_label: str,
    ) -> SavedLocation | None:
        """Resolves a user-specific location query deterministically without LLM inference."""
        cleaned = query_label.strip()
        if not cleaned:
            return None
        return await self.saved_location_repo.get_by_user_and_label(
            user_id=user_id,
            label=cleaned,
            include_deleted=False,
        )


class LocationResolver:
    """Deterministic resolver bridging conversational intents to user saved location records."""

    def __init__(self, service: SavedLocationService) -> None:
        self.service = service

    async def resolve(
        self,
        user_id: uuid.UUID,
        label_query: str,
    ) -> SavedLocation | None:
        """Resolves a label query (e.g. 'work', 'HOME', ' Home ') to a SavedLocation domain entity."""
        return await self.service.resolve_location(
            user_id=user_id, query_label=label_query
        )

    async def resolve_known_locations(
        self,
        user_id: uuid.UUID,
    ) -> dict[str, SavedLocation]:
        """Returns a normalized lowercase-mapped dictionary of all active locations for the user."""
        locations = await self.service.list_saved_locations(user_id=user_id)
        return {loc.label.strip().lower(): loc for loc in locations}
