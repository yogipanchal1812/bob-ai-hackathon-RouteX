"""RouteX Backend — Disruption API endpoints."""

from typing import Optional

from fastapi import APIRouter, Query

from app.schemas.disruption import DisruptionListResponse, DisruptionResponse
from app.services import disruption_service

router = APIRouter(prefix="/api", tags=["Disruptions"])


@router.get("/disruptions", response_model=DisruptionListResponse)
def list_disruptions(
    status: Optional[str] = Query(
        None, description="Filter by status (ACTIVE, RESOLVED, MONITORING)"
    ),
):
    """Return all disruptions, optionally filtered by status."""
    disruptions = disruption_service.get_all_disruptions(status=status)
    return DisruptionListResponse(
        success=True,
        count=len(disruptions),
        data=[DisruptionResponse(**d.__dict__) for d in disruptions],
    )


@router.get("/disruptions/{disruption_id}")
def get_disruption(disruption_id: str):
    """Return a single disruption by ID."""
    disruption = disruption_service.get_disruption_by_id(disruption_id)
    return {
        "success": True,
        "data": DisruptionResponse(**disruption.__dict__).model_dump(),
    }
