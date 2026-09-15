"""RouteX Backend — Impact Analysis API endpoints."""

from fastapi import APIRouter

from app.schemas.analysis import DisruptionAnalysisRequest
from app.services import impact_service

router = APIRouter(prefix="/api", tags=["Impact Analysis"])


@router.post("/analyze-disruption")
def analyze_disruption(request: DisruptionAnalysisRequest):
    """
    Analyse a specific disruption's impact on all shipments.

    Returns affected shipments with risk scores, delay estimates,
    financial impact, and an aggregated summary.
    """
    result = impact_service.analyze_disruption(request.disruption_id)
    return {"success": True, "data": result}


@router.get("/impact-summary")
def impact_summary():
    """
    Return an aggregated impact summary across all active disruptions.
    """
    result = impact_service.get_impact_summary()
    return {"success": True, "data": result}
