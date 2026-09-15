"""
allocation.py — Vehicle-to-shipment matching engine.

Matching is DETERMINISTIC — no random values.

Score components (total max = 100):
    +40  Vehicle status is AVAILABLE or IDLE (can be dispatched)
    +30  Vehicle capacity_tons >= shipment weight_tons
    +20  Vehicle location matches shipment origin region (categorical)
    +10  Vehicle carrier_id matches shipment carrier_id

Returns results sorted by match_score descending.
Vehicles with score == 0 are excluded from results.

If no vehicles are available → returns empty list (no crash).
If no shipment data found → returns empty list (no crash).
"""

from optimization.schemas.fleet import FleetMatchResult, Vehicle, VehicleStatus


# Categorical region groupings — used for proximity scoring.
# Without real GPS, we group cities into regions.
_REGION_MAP: dict[str, str] = {
    "Mumbai":    "WEST",
    "Pune":      "WEST",
    "Surat":     "WEST",
    "Ahmedabad": "WEST",
    "Delhi":     "NORTH",
    "Jaipur":    "NORTH",
    "Lucknow":   "NORTH",
    "Kolkata":   "EAST",
    "Chennai":   "SOUTH",
    "Bangalore": "SOUTH",
    "Hyderabad": "SOUTH",
}


def _get_region(location: str) -> str:
    """Return the region code for a city. Unknown cities → 'UNKNOWN'."""
    return _REGION_MAP.get(location, "UNKNOWN")


def _score_vehicle(
    vehicle: Vehicle,
    weight_tons: float,
    shipment_origin: str,
    shipment_carrier_id: str,
) -> tuple[int, list[str]]:
    """
    Score a single vehicle against a shipment's requirements.

    Returns:
        (score: int, reasons: list[str])
    """
    score = 0
    reasons: list[str] = []

    # --- Availability (+40) ---
    if vehicle.status in (VehicleStatus.AVAILABLE, VehicleStatus.IDLE):
        score += 40
        status_label = "available" if vehicle.status == VehicleStatus.AVAILABLE else "idle (dispatchable)"
        reasons.append(f"Vehicle is {status_label}")
    else:
        reasons.append(f"Vehicle is {vehicle.status} (not dispatchable — excluded from score)")

    # --- Capacity (+30) ---
    if vehicle.capacity_tons >= weight_tons:
        score += 30
        reasons.append(
            f"Capacity sufficient ({vehicle.capacity_tons}t ≥ {weight_tons}t required)"
        )
    else:
        reasons.append(
            f"Insufficient capacity ({vehicle.capacity_tons}t < {weight_tons}t required)"
        )

    # --- Location proximity (+20) ---
    vehicle_region = _get_region(vehicle.location)
    shipment_region = _get_region(shipment_origin)
    if vehicle_region != "UNKNOWN" and vehicle_region == shipment_region:
        score += 20
        reasons.append(
            f"Vehicle is in the same region as shipment origin ({vehicle.location} → {shipment_origin})"
        )
    elif vehicle.location == shipment_origin:
        score += 20
        reasons.append(f"Vehicle is at the shipment origin ({shipment_origin})")
    else:
        reasons.append(
            f"Vehicle location ({vehicle.location}) is in a different region from origin ({shipment_origin})"
        )

    # --- Carrier compatibility (+10) ---
    if vehicle.carrier_id == shipment_carrier_id:
        score += 10
        reasons.append(f"Vehicle carrier matches shipment carrier ({vehicle.carrier_id})")
    else:
        reasons.append(
            f"Carrier mismatch (vehicle: {vehicle.carrier_id}, shipment: {shipment_carrier_id})"
        )

    return score, reasons


def match_vehicles_to_shipment(
    shipment: dict,
    vehicles: list[Vehicle],
) -> list[FleetMatchResult]:
    """
    Match available vehicles to a single shipment.

    Args:
        shipment: Dict with keys shipment_id, origin, weight_tons, carrier_id.
        vehicles: Full fleet vehicle list.

    Returns:
        List of FleetMatchResult sorted by match_score descending.
        Empty list if no suitable vehicles found.
    """
    shipment_id: str = shipment.get("shipment_id", "")
    weight_tons: float = float(shipment.get("weight_tons", 0.0))
    origin: str = shipment.get("origin", "")
    carrier_id: str = shipment.get("carrier_id", "")

    results: list[FleetMatchResult] = []

    for vehicle in vehicles:
        score, reasons = _score_vehicle(vehicle, weight_tons, origin, carrier_id)

        # Only return vehicles that are at least dispatchable (score > 0 from availability)
        # A vehicle that is IN_TRANSIT or MAINTENANCE cannot be recommended.
        if vehicle.status not in (VehicleStatus.AVAILABLE, VehicleStatus.IDLE):
            continue

        results.append(
            FleetMatchResult(
                vehicle_id=vehicle.vehicle_id,
                shipment_id=shipment_id,
                match_score=min(score, 100),  # cap at 100
                reason=reasons,
            )
        )

    # Sort best match first
    results.sort(key=lambda r: r.match_score, reverse=True)
    return results


def match_all_shipments(
    shipments: list[dict],
    vehicles: list[Vehicle],
) -> tuple[list[FleetMatchResult], list[str]]:
    """
    Run vehicle matching across multiple shipments.

    Returns:
        (all_matches, unmatched_shipment_ids)
    """
    all_matches: list[FleetMatchResult] = []
    unmatched: list[str] = []

    for shipment in shipments:
        matches = match_vehicles_to_shipment(shipment, vehicles)
        if matches:
            # Return only the best match per shipment to keep response concise
            all_matches.append(matches[0])
        else:
            unmatched.append(shipment.get("shipment_id", ""))

    return all_matches, unmatched
