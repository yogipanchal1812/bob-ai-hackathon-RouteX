"""
simulation_router.py — FastAPI router for what-if simulation endpoint.

Endpoints (stable contract):
    POST /api/what-if  → Run a disruption duration scenario and compare to baseline

Input validation:
    - disruption_id: must be a non-empty string
    - duration_days:  must be ≥ 0 (negative rejected with HTTP 422)

Output is always the WhatIfResponse structure from the shared spec.
"""

import logging

from fastapi import APIRouter, HTTPException, status

from optimization.schemas.simulation import WhatIfRequest, WhatIfResponse
from optimization.simulation.what_if import run_what_if

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["simulation"])


@router.post(
    "/what-if",
    response_model=WhatIfResponse,
    summary="Run a what-if disruption scenario",
    description=(
        "Simulates the impact of a disruption lasting 'duration_days' days and compares "
        "it to the current baseline. Returns affected shipment counts, high-risk counts, "
        "estimated financial impact, and recommended operational actions.\n\n"
        "**Endpoint contract is stable** — do not change field names."
    ),
    status_code=status.HTTP_200_OK,
)
def what_if_simulation(body: WhatIfRequest) -> WhatIfResponse:
    """
    POST /api/what-if

    Request body:
        {
            "disruption_id": "D001",
            "duration_days": 5
        }

    Response:
        {
            "baseline":  { "affected_shipments": int, "high_risk": int, "estimated_impact": float },
            "scenario":  { "affected_shipments": int, "high_risk": int, "estimated_impact": float },
            "delta":     { "affected_shipments": int, "high_risk": int, "estimated_impact": float },
            "recommended_actions": [
                { "action": str, "priority": str, "target": str, "reason": str }
            ]
        }

    Error cases:
        - duration_days < 0 → HTTP 422 (Pydantic validation)
        - disruption_id not found → valid response with zeros (graceful)
        - Server error → HTTP 500 with detail message
    """
    try:
        logger.info(
            "What-if request: disruption_id=%s, duration_days=%d",
            body.disruption_id,
            body.duration_days,
        )
        result = run_what_if(
            disruption_id=body.disruption_id,
            duration_days=body.duration_days,
        )
        return result

    except Exception as exc:
        logger.exception(
            "Unexpected error in POST /api/what-if: disruption_id=%s, duration_days=%d",
            body.disruption_id,
            body.duration_days,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="What-if simulation failed. Please check inputs and try again.",
        ) from exc
