"""
RouteX AI Module — FastAPI Router.

Exposes REST endpoints:
    POST /api/copilot
    POST /api/recommendation
"""

from fastapi import APIRouter, HTTPException

from ai.copilot.service import CopilotService
from ai.recommendations.recommendation_service import RecommendationService
from ai.schemas.chat import CopilotRequest, CopilotResponse
from ai.schemas.recommendation import RecommendationRequest, RecommendationResponse

router = APIRouter(prefix="/api", tags=["AI Decision Support"])

_copilot_service = CopilotService()
_recommendation_service = RecommendationService()


@router.post("/copilot", response_model=CopilotResponse)
def copilot_endpoint(request: CopilotRequest):
    """
    Enterprise AI Copilot endpoint for supply chain decision makers.
    Answers natural language queries grounded in active RouteX context.
    """
    query = request.question or request.message
    if not query or not query.strip():
        raise HTTPException(status_code=422, detail="Question or message cannot be empty")

    try:
        response = _copilot_service.answer_question(
            question=query,
            extra_context=request.context,
        )
        return response
    except Exception as err:
        raise HTTPException(status_code=500, detail="Internal AI service error occurred.")


@router.post("/recommendation", response_model=RecommendationResponse)
def recommendation_endpoint(request: RecommendationRequest):
    """
    Generate structured operational recommendations for a shipment,
    disruption, or across the active global network.
    """
    try:
        recs = _recommendation_service.generate_recommendations(
            shipment_id=request.shipment_id,
            disruption_id=request.disruption_id,
            max_count=request.max_recommendations,
        )
        return RecommendationResponse(
            success=True,
            count=len(recs),
            data=recs,
        )
    except Exception as err:
        raise HTTPException(status_code=500, detail="Internal recommendation service error occurred.")
