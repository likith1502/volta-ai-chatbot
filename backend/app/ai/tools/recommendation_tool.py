import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.models import AIToolResult
from app.ai.tools.base import AITool


class RecommendationTool(AITool):
    """Tool wrapper executing RecommendationService logic for ride & route requests."""

    name: str = "recommendation"
    description: str = "Generates and persists ride/route recommendations for active conversations."

    def __init__(self, session: AsyncSession) -> None:
        from app.services.recommendation import RecommendationService

        self.session = session
        self.recommendation_service = RecommendationService(session)

    async def execute(self, arguments: dict[str, Any]) -> AIToolResult:
        """Executes RecommendationService inside the tool boundary."""
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
            user_query = arguments.get("user_query", "Ride requested")

            rec = await self.recommendation_service.create_recommendation(
                conversation_id=conversation_id,
                recommendation_type="ride",
                recommendation_data={
                    "user_query": user_query,
                    "options": arguments.get(
                        "options",
                        [
                            {"tier": "Standard Sedan", "estimated_price": 24.50, "eta_minutes": 4},
                            {"tier": "Comfort SUV", "estimated_price": 35.00, "eta_minutes": 6},
                        ],
                    ),
                },
            )

            return AIToolResult(
                tool_name=self.name,
                success=True,
                data={
                    "recommendation_id": rec.id,
                    "status": rec.status.value,
                    "type": rec.recommendation_type,
                },
            )
        except Exception as exc:
            return AIToolResult(
                tool_name=self.name,
                success=False,
                error=f"RecommendationTool execution failed: {exc}",
            )
