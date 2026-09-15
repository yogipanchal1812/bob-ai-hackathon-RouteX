"""
utilization.py — Pure fleet utilization calculation.

Utilization Formula (documented per spec):
    utilization_pct = (in_transit_count / total_count) * 100

Where:
    in_transit_count = vehicles with status == IN_TRANSIT
    total_count      = all vehicles in the fleet

Edge cases:
    - Zero vehicles          → utilization_pct = 0.0  (no division by zero)
    - All MAINTENANCE        → utilization_pct = 0.0
    - All IDLE               → utilization_pct = 0.0
    - All IN_TRANSIT         → utilization_pct = 100.0

"available" here means ready to be dispatched (AVAILABLE or IDLE status).
IDLE vehicles are already on-site but NOT doing useful work — an optimisation opportunity.
"""

from optimization.schemas.fleet import FleetUtilizationReport, Vehicle, VehicleStatus


def calculate_utilization(vehicles: list[Vehicle]) -> FleetUtilizationReport:
    """
    Compute fleet utilization from a list of Vehicle objects.

    Args:
        vehicles: List of Vehicle objects (may be empty).

    Returns:
        FleetUtilizationReport with counts and utilization_pct.

    Raises:
        Never raises — empty list returns zeroed report.
    """
    total = len(vehicles)

    if total == 0:
        return FleetUtilizationReport(
            total_vehicles=0,
            available_vehicles=0,
            idle_vehicles=0,
            in_transit_vehicles=0,
            maintenance_vehicles=0,
            utilization_pct=0.0,
        )

    available_count = sum(
        1 for v in vehicles if v.status == VehicleStatus.AVAILABLE
    )
    idle_count = sum(
        1 for v in vehicles if v.status == VehicleStatus.IDLE
    )
    in_transit_count = sum(
        1 for v in vehicles if v.status == VehicleStatus.IN_TRANSIT
    )
    maintenance_count = sum(
        1 for v in vehicles if v.status == VehicleStatus.MAINTENANCE
    )

    # Utilization = % of fleet actively in transit (the "productive" portion)
    utilization_pct = round((in_transit_count / total) * 100, 2)

    # Guard: clamp to [0.0, 100.0] in case of any floating-point edge case
    utilization_pct = max(0.0, min(100.0, utilization_pct))

    return FleetUtilizationReport(
        total_vehicles=total,
        available_vehicles=available_count,
        idle_vehicles=idle_count,
        in_transit_vehicles=in_transit_count,
        maintenance_vehicles=maintenance_count,
        utilization_pct=utilization_pct,
    )
