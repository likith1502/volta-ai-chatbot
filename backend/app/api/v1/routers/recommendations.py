import uuid

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_recommendation_service
from app.schemas.common import ResponseEnvelope
from app.schemas.recommendation import RecommendationCreate, RecommendationResponse
from app.services.recommendation import RecommendationService
from app.utils.responses import success_response

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.post(
    "",
    response_model=ResponseEnvelope[RecommendationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Recommendation",
    description="Generates and attaches an AI recommendation payload to an active conversation session.",
)
async def create_recommendation(
    payload: RecommendationCreate,
    service: RecommendationService = Depends(get_recommendation_service),
):
    rec = await service.create_recommendation(
        conversation_id=payload.conversation_id,
        recommendation_type=payload.recommendation_type,
        recommendation_data=payload.recommendation_data,
        confidence_score=payload.confidence_score,
        ranking=payload.ranking,
    )
    return success_response(
        data=RecommendationResponse.model_validate(rec),
        message="Recommendation created successfully.",
    )


@router.get(
    "/active",
    response_model=ResponseEnvelope[list[RecommendationResponse]],
    summary="Get Active Recommendations",
    description="Retrieves pending/active recommendations for a conversation session.",
)
async def get_active_recommendations(
    conversation_id: uuid.UUID,
    service: RecommendationService = Depends(get_recommendation_service),
):
    recs = await service.get_active_recommendations(conversation_id)
    return success_response(
        data=[RecommendationResponse.model_validate(r) for r in recs],
        message="Active recommendations retrieved successfully.",
    )


@router.get(
    "/{recommendation_id}",
    response_model=ResponseEnvelope[RecommendationResponse],
    summary="Get Recommendation By ID",
    description="Retrieves a recommendation payload by primary key UUID.",
)
async def get_recommendation(
    recommendation_id: uuid.UUID,
    service: RecommendationService = Depends(get_recommendation_service),
):
    rec = await service.get_recommendation(recommendation_id)
    return success_response(
        data=RecommendationResponse.model_validate(rec),
        message="Recommendation retrieved successfully.",
    )
