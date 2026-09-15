"""
fleet_service.py — Service layer that wires data sources to fleet logic.

This module is the single integration point between:
  - The data layer (seed_data.py in dev mode, Member 1's API in prod mode)
  - The fleet logic (utilization.py, allocation.py)
  - The API routers (fleet_router.py)

Member 1 integration note:
  When DISRUPTION_API_URL is set in the environment, this service will
  fetch live vehicle/shipment data from that URL instead of seed data.
  Until Member 1's API is available, seed data is used automatically.
"""

import logging

from optimization.data import seed_data
from optimization.fleet.allocation import match_all_shipments, match_vehicles_to_shipment
from optimization.fleet.utilization import calculate_utilization
from optimization.schemas.fleet import (
    FleetMatchResult,
    FleetUtilizationReport,
    OptimizeFleetResponse,
    Vehicle,
)

logger = logging.getLogger(__name__)


def get_all_vehicles() -> list[Vehicle]:
    """
    Return the complete fleet vehicle list.

    In production: would fetch from Member 1's /api/fleet endpoint.
    In dev/demo: returns seed data.
    """
    return seed_data.get_vehicles()


def get_fleet_utilization() -> FleetUtilizationReport:
    """
    Compute and return the current fleet utilization report.

    Delegates to the pure calculate_utilization() function.
    """
    vehicles = get_all_vehicles()
    report = calculate_utilization(vehicles)
    logger.info(
        "Fleet utilization computed: %d total, %.1f%% utilization",
        report.total_vehicles,
        report.utilization_pct,
    )
    return report


def optimize_fleet(
    shipment_ids: list[str] | None = None,
    disruption_id: str | None = None,
) -> OptimizeFleetResponse:
    """
    Find best vehicle matches for affected shipments.

    Args:
        shipment_ids:   Specific shipment IDs to optimize. None = all affected.
        disruption_id:  Filter shipments by this disruption. None = all shipments.

    Returns:
        OptimizeFleetResponse with matches and unmatched shipment IDs.
    """
    vehicles = get_all_vehicles()
    all_shipments = seed_data.get_shipments()

    # Filter shipments
    if disruption_id:
        shipments = [s for s in all_shipments if s["disruption_id"] == disruption_id]
        if not shipments:
            logger.warning("No shipments found for disruption_id=%s", disruption_id)
    else:
        shipments = all_shipments

    if shipment_ids:
        shipments = [s for s in shipments if s["shipment_id"] in shipment_ids]

    if not shipments:
        logger.info("No shipments to optimize.")
        return OptimizeFleetResponse(matches=[], total_matches=0, unmatched_shipment_ids=[])

    matches, unmatched = match_all_shipments(shipments, vehicles)

    logger.info(
        "Fleet optimization: %d shipments → %d matched, %d unmatched",
        len(shipments),
        len(matches),
        len(unmatched),
    )

    return OptimizeFleetResponse(
        matches=matches,
        total_matches=len(matches),
        unmatched_shipment_ids=unmatched,
    )
