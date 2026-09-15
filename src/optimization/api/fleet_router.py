"""
fleet_router.py — FastAPI router for fleet endpoints.

Endpoints (stable contract — do not rename without coordinating with Members 2 & 3):
    GET  /api/fleet              → List all fleet vehicles
    GET  /api/fleet/utilization  → Fleet utilization report
    POST /api/optimize-fleet     → Vehicle matching for affected shipments

All endpoints:
  - Return JSON (Rule 18)
  - Return consistent structures (Rule 19)
  - Validate input via Pydantic (Rule 20)
  - Handle empty data gracefully (Rule 21)
  - Return correct HTTP status codes
"""

import logging

from fastapi import APIRouter, HTTPException, Query, status

from optimization.fleet.fleet_service import (
    get_all_vehicles,
    get_fleet_utilization,
    optimize_fleet,
)
from optimization.schemas.fleet import (
    FleetUtilizationReport,
    OptimizeFleetRequest,
    OptimizeFleetResponse,
    Vehicle,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["fleet"])


@router.get(
    "/fleet",
    response_model=list[Vehicle],
    summary="List all fleet vehicles",
    description=(
        "Returns the complete list of fleet assets with their current status, "
        "location, capacity, and carrier association."
    ),
)
def list_fleet(
    status: str | None = Query(
        default=None,
        description="Filter by vehicle status: AVAILABLE | IN_TRANSIT | IDLE | MAINTENANCE",
        alias="status",
    ),
    carrier_id: str | None = Query(default=None, description="Filter by carrier ID"),
) -> list[Vehicle]:
    """
    GET /api/fleet

    Optional query parameters:
        ?status=AVAILABLE   — filter by vehicle status
        ?carrier_id=C001    — filter by carrier
    """
    try:
        vehicles = get_all_vehicles()

        if status:
            status_upper = status.upper()
            valid_statuses = {"AVAILABLE", "IN_TRANSIT", "IDLE", "MAINTENANCE"}
            if status_upper not in valid_statuses:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid status '{status}'. Must be one of: {sorted(valid_statuses)}",
                )
            vehicles = [v for v in vehicles if v.status == status_upper]

        if carrier_id:
            vehicles = [v for v in vehicles if v.carrier_id == carrier_id]

        return vehicles

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error in GET /api/fleet")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve fleet data.",
        ) from exc


@router.get(
    "/fleet/utilization",
    response_model=FleetUtilizationReport,
    summary="Fleet utilization report",
    description=(
        "Returns a breakdown of fleet utilization: total, available, idle, "
        "in-transit, and maintenance vehicle counts, plus the utilization percentage. "
        "Formula: utilization_pct = (in_transit / total) × 100"
    ),
)
def fleet_utilization() -> FleetUtilizationReport:
    """
    GET /api/fleet/utilization

    Returns utilization metrics. If no vehicles exist, returns zeros (no crash).
    """
    try:
        return get_fleet_utilization()
    except Exception as exc:
        logger.exception("Unexpected error in GET /api/fleet/utilization")
        raise HTTPException(
            status_code=500,
            detail="Failed to compute fleet utilization.",
        ) from exc


@router.post(
    "/optimize-fleet",
    response_model=OptimizeFleetResponse,
    summary="Optimize fleet for affected shipments",
    description=(
        "Matches available and idle fleet vehicles to shipments affected by disruptions. "
        "Returns the best vehicle match per shipment along with unmatched shipment IDs. "
        "Match scoring: availability (40pts) + capacity (30pts) + proximity (20pts) + carrier (10pts)."
    ),
    status_code=status.HTTP_200_OK,
)
def optimize_fleet_endpoint(body: OptimizeFleetRequest) -> OptimizeFleetResponse:
    """
    POST /api/optimize-fleet

    Body (all optional):
        {
            "shipment_ids": ["SH001", "SH002"],   // omit to use all affected shipments
            "disruption_id": "D001"               // omit to consider all disruptions
        }
    """
    try:
        result = optimize_fleet(
            shipment_ids=body.shipment_ids,
            disruption_id=body.disruption_id,
        )
        return result
    except Exception as exc:
        logger.exception("Unexpected error in POST /api/optimize-fleet")
        raise HTTPException(
            status_code=500,
            detail="Fleet optimization failed.",
        ) from exc
