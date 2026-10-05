import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.models import AIToolResult
from app.ai.tools.base import AITool
from app.exceptions.domain import (
    InvalidBookingStatusException,
    RecommendationExpiredException,
    RecommendationNotFoundException,
)
from app.models.booking import Booking
from app.models.enums import RecommendationStatus
from app.services.booking import BookingService

logger = logging.getLogger("app.ai.tools.booking")


class BookingTool(AITool):
    """Tool wrapper executing ride booking creation via BookingService."""

    name: str = "booking"
    description: str = (
        "Creates a confirmed ride booking reservation from an active recommendation."
    )

    def __init__(
        self,
        session: AsyncSession,
        booking_service: Optional[BookingService] = None,
    ) -> None:
        self.session = session
        self.booking_service = booking_service or BookingService(session)

    def _build_replay_result(
        self,
        existing_booking: Booking,
        currency: Optional[str] = None,
    ) -> AIToolResult:
        """Constructs a safe duplicate-replay response without guessing unpersisted tier or fare."""
        return AIToolResult(
            tool_name=self.name,
            success=True,
            data={
                "booking_id": str(existing_booking.id),
                "booking_reference": existing_booking.booking_reference,
                "booking_status": existing_booking.booking_status.value,
                "tier": None,
                "fare": None,
                "currency": currency,
                "booked_at": (
                    existing_booking.booked_at.isoformat()
                    if existing_booking.booked_at
                    else None
                ),
                "is_duplicate_replay": True,
            },
        )

    async def execute(self, arguments: dict[str, Any]) -> AIToolResult:
        """Executes BookingService inside the tool boundary with strict validation."""
        rec_id: Optional[uuid.UUID] = None
        selected_tier: Optional[str] = None
        try:
            rec_id_raw = arguments.get("recommendation_id")
            if not rec_id_raw:
                return AIToolResult(
                    tool_name=self.name,
                    success=False,
                    error="Missing required argument 'recommendation_id'",
                )

            try:
                rec_id = (
                    uuid.UUID(str(rec_id_raw))
                    if not isinstance(rec_id_raw, uuid.UUID)
                    else rec_id_raw
                )
            except (ValueError, TypeError):
                return AIToolResult(
                    tool_name=self.name,
                    success=False,
                    error=f"Invalid 'recommendation_id': '{rec_id_raw}' is not a valid UUID.",
                )

            conv_id_raw = arguments.get("conversation_id")
            if not conv_id_raw:
                return AIToolResult(
                    tool_name=self.name,
                    success=False,
                    error="Missing required argument 'conversation_id'",
                )

            try:
                conv_id = (
                    uuid.UUID(str(conv_id_raw))
                    if not isinstance(conv_id_raw, uuid.UUID)
                    else conv_id_raw
                )
            except (ValueError, TypeError):
                return AIToolResult(
                    tool_name=self.name,
                    success=False,
                    error=f"Invalid 'conversation_id': '{conv_id_raw}' is not a valid UUID.",
                )

            user_id_raw = arguments.get("user_id")
            if not user_id_raw:
                return AIToolResult(
                    tool_name=self.name,
                    success=False,
                    error="Missing required argument 'user_id'",
                )

            try:
                user_id = (
                    uuid.UUID(str(user_id_raw))
                    if not isinstance(user_id_raw, uuid.UUID)
                    else user_id_raw
                )
            except (ValueError, TypeError):
                return AIToolResult(
                    tool_name=self.name,
                    success=False,
                    error=f"Invalid 'user_id': '{user_id_raw}' is not a valid UUID.",
                )

            selected_tier = arguments.get("selected_tier")

            # 1. Fetch and validate recommendation
            recommendation = await self.booking_service.recommendation_repo.get_by_id(
                rec_id
            )
            if not recommendation:
                return AIToolResult(
                    tool_name=self.name,
                    success=False,
                    error=f"Recommendation with ID '{rec_id}' not found.",
                )

            # 2. Mandatory Conversation and User Ownership Validation
            if recommendation.conversation_id != conv_id:
                return AIToolResult(
                    tool_name=self.name,
                    success=False,
                    error="Recommendation does not belong to the active conversation.",
                )

            conv = await self.booking_service.conversation_repo.get_by_id(conv_id)
            if not conv or not conv.user_id or conv.user_id != user_id:
                return AIToolResult(
                    tool_name=self.name,
                    success=False,
                    error="User does not have authorization to book this recommendation.",
                )

            # 3. Check for Existing Booking (Idempotency / Retry Replay)
            if recommendation.status == RecommendationStatus.ACCEPTED:
                stmt = select(Booking).where(
                    Booking.recommendation_id == rec_id,
                    Booking.is_deleted == False,  # noqa: E712
                )
                res = await self.session.execute(stmt)
                existing_booking = res.scalar_one_or_none()
                if existing_booking:
                    rec_currency = (
                        recommendation.recommendation_data or {}
                    ).get("currency")
                    return self._build_replay_result(
                        existing_booking, currency=rec_currency
                    )

            # 4. Check for Expiration
            if recommendation.status == RecommendationStatus.EXPIRED:
                return AIToolResult(
                    tool_name=self.name,
                    success=False,
                    error="Cannot create booking: recommendation has expired.",
                )

            rec_data = recommendation.recommendation_data or {}
            expires_at_str = rec_data.get("expires_at")
            if expires_at_str:
                try:
                    exp_dt = datetime.fromisoformat(expires_at_str)
                    if exp_dt.tzinfo is None:
                        exp_dt = exp_dt.replace(tzinfo=timezone.utc)
                    if datetime.now(timezone.utc) > exp_dt:
                        return AIToolResult(
                            tool_name=self.name,
                            success=False,
                            error="Cannot create booking: quote has expired.",
                        )
                except Exception:
                    pass

            # 5. Check recommendation is PENDING
            if recommendation.status != RecommendationStatus.PENDING:
                return AIToolResult(
                    tool_name=self.name,
                    success=False,
                    error=f"Recommendation status is '{recommendation.status}', must be PENDING.",
                )

            # 6. Execute Booking Creation via BookingService
            # Important: Do not store selected_tier in external_booking_id per operational boundary
            booking = (
                await self.booking_service.create_booking_from_recommendation(
                    recommendation_id=rec_id,
                    provider="volta_fleet",
                    external_booking_id=None,
                )
            )

            # Extract fare and display name from quote options
            options = rec_data.get("options", [])
            fare = None
            currency = rec_data.get("currency", "INR")
            display_name = selected_tier
            for opt in options:
                opt_tier = opt.get("tier", "").lower()
                if selected_tier and opt_tier == selected_tier.lower():
                    fare = opt.get("fare")
                    display_name = opt.get("display_name", selected_tier)
                    break

            return AIToolResult(
                tool_name=self.name,
                success=True,
                data={
                    "booking_id": str(booking.id),
                    "booking_reference": booking.booking_reference,
                    "booking_status": booking.booking_status.value,
                    "tier": display_name or selected_tier,
                    "fare": fare,
                    "currency": currency,
                    "booked_at": (
                        booking.booked_at.isoformat()
                        if booking.booked_at
                        else None
                    ),
                    "is_duplicate_replay": False,
                },
            )

        except InvalidBookingStatusException as status_err:
            try:
                await self.session.rollback()
            except Exception:
                pass
            if rec_id:
                try:
                    stmt = select(Booking).where(
                        Booking.recommendation_id == rec_id,
                        Booking.is_deleted == False,  # noqa: E712
                    )
                    res = await self.session.execute(stmt)
                    existing_booking = res.scalar_one_or_none()
                    if existing_booking:
                        logger.info(
                            "Concurrent booking resolved via existing booking %s for recommendation %s",
                            existing_booking.booking_reference,
                            rec_id,
                        )
                        return self._build_replay_result(existing_booking)
                except Exception as query_err:
                    logger.error(
                        "Failed to query existing booking after InvalidBookingStatusException: %s",
                        query_err,
                    )
            return AIToolResult(
                tool_name=self.name,
                success=False,
                error=str(status_err),
            )
        except IntegrityError as integ_err:
            logger.warning(
                "Database integrity conflict during booking creation for recommendation %s: %s",
                rec_id,
                integ_err,
            )
            try:
                await self.session.rollback()
            except Exception:
                pass
            if rec_id:
                try:
                    stmt = select(Booking).where(
                        Booking.recommendation_id == rec_id,
                        Booking.is_deleted == False,  # noqa: E712
                    )
                    res = await self.session.execute(stmt)
                    existing_booking = res.scalar_one_or_none()
                    if existing_booking:
                        logger.info(
                            "Database integrity collision resolved via existing booking %s for recommendation %s",
                            existing_booking.booking_reference,
                            rec_id,
                        )
                        return self._build_replay_result(existing_booking)
                except Exception as query_err:
                    logger.error(
                        "Failed to query existing booking after IntegrityError: %s",
                        query_err,
                    )
            return AIToolResult(
                tool_name=self.name,
                success=False,
                error=f"Booking creation failed due to database integrity conflict: {integ_err}",
            )
        except (
            RecommendationExpiredException,
            RecommendationNotFoundException,
        ) as dom_err:
            try:
                await self.session.rollback()
            except Exception:
                pass
            return AIToolResult(
                tool_name=self.name,
                success=False,
                error=str(dom_err),
            )
        except Exception as exc:
            try:
                await self.session.rollback()
            except Exception:
                pass
            logger.exception(
                "BookingTool execution encountered unexpected error: %s", exc
            )
            return AIToolResult(
                tool_name=self.name,
                success=False,
                error=f"BookingTool execution failed: {exc}",
            )
