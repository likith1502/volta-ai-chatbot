import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import RecommendationStatus


class RecommendationCreate(BaseModel):
    """Payload schema for generating an AI recommendation."""

    conversation_id: uuid.UUID
    recommendation_type: str
    recommendation_data: dict[str, Any]
    confidence_score: float = 1.0
    ranking: int = 1


class RecommendationResponse(BaseModel):
    """Response DTO for Recommendation domain entity."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversation_id: uuid.UUID
    recommendation_type: str
    recommendation_data: dict[str, Any]
    status: RecommendationStatus
    confidence_score: float
    ranking: int
    created_at: Optional[datetime] = None
