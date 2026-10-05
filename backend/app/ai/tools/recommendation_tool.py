import uuid
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.models import AIToolResult
from app.ai.tools.base import AITool


class RecommendationTool(AITool):
    """Tool wrapper executing cab availability and pricing via CabPricingService."""

    name: str = "recommendation"
    description: str = (
        "Generates and persists ride/route recommendations for active conversations."
    )

    def __init__(
        self,
        session: AsyncSession,
        cab_pricing_service: Optional[Any] = None,
    ) -> None:
        from app.services.cab_pricing import CabPricingService

        self.session = session
        self.cab_pricing_service = cab_pricing_service or CabPricingService(session)
        self.recommendation_service = self.cab_pricing_service.recommendation_service

    async def execute(self, arguments: dict[str, Any]) -> AIToolResult:
        """Executes CabPricingService inside the tool boundary."""
        try:
            conversation_id_raw = arguments.get("conversation_id")
            if not conversation_id_raw:
                return AIToolResult(
                    tool_name=self.name,
                    success=False,
                    error="Missing required argument 'conversation_id'",
                )

            conversation_id = (
                uuid.UUID(conversation_id_raw)
                if isinstance(conversation_id_raw, str)
                else conversation_id_raw
            )
            user_query = arguments.get("user_query") or "Ride requested"
            pickup = arguments.get("pickup") or user_query
            destination = arguments.get("destination") or "Destination"

            quote = await self.cab_pricing_service.get_availability_quote(
                pickup=pickup,
                destination=destination,
                conversation_id=conversation_id,
                persist_recommendation=True,
            )

            rec_id = quote.recommendation_id or quote.quote_id

            return AIToolResult(
                tool_name=self.name,
                success=True,
                data={
                    "recommendation_id": rec_id,
                    "quote_id": str(quote.quote_id),
                    "status": "pending",
                    "type": "cab_availability",
                    "currency": quote.currency,
                    "options": [opt.model_dump(mode="json") for opt in quote.options],
                },
            )
        except Exception as exc:
            return AIToolResult(
                tool_name=self.name,
                success=False,
                error=f"RecommendationTool execution failed: {exc}",
            )
