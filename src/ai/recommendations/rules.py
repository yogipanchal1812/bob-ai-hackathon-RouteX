"""
RouteX AI Module — Decision Rules and Confidence Scoring.

Implements domain-specific, explainable operational logic for generating
supply-chain mitigation recommendations.
"""

from typing import Any, Dict, List, Optional, Tuple


def calculate_confidence(
    carrier_reliability: float,
    disruption_severity: str,
    shipment_priority: str,
    alternative_available: bool,
) -> float:
    """
    Calculate an explainable, deterministic confidence score (0.0 – 1.0).

    Weights:
        Carrier performance: 40%
        Disruption certainty: 30%
        Alternative route viability: 20%
        Shipment priority: 10%
    """
    severity_weights = {
        "CRITICAL": 1.0,
        "HIGH": 0.85,
        "MEDIUM": 0.65,
        "LOW": 0.40,
    }
    priority_weights = {
        "CRITICAL": 1.0,
        "HIGH": 0.80,
        "MEDIUM": 0.50,
        "LOW": 0.30,
    }

    w_carrier = max(0.0, min(1.0, carrier_reliability)) * 0.40
    w_severity = severity_weights.get(disruption_severity.upper(), 0.5) * 0.30
    w_alt = (1.0 if alternative_available else 0.4) * 0.20
    w_priority = priority_weights.get(shipment_priority.upper(), 0.5) * 0.10

    raw_score = w_carrier + w_severity + w_alt + w_priority
    return max(0.10, min(0.99, round(raw_score, 2)))


def determine_recommendation_priority(
    risk_level: str,
    priority: str,
    cargo_value: float,
    cargo_type: str,
) -> str:
    """
    Determine priority for an operational recommendation:
    CRITICAL | HIGH | MEDIUM | LOW
    """
    is_sensitive = any(
        kw in cargo_type.lower()
        for kw in ["pharmaceutical", "medical", "perishable", "chemical"]
    )

    if risk_level == "CRITICAL" or priority == "CRITICAL" or (cargo_value >= 4_000_000 and is_sensitive):
        return "CRITICAL"
    elif risk_level == "HIGH" or priority == "HIGH" or cargo_value >= 2_000_000 or is_sensitive:
        return "HIGH"
    elif risk_level == "MEDIUM" or priority == "MEDIUM":
        return "MEDIUM"
    else:
        return "LOW"


def find_alternative_route(
    origin: str,
    destination: str,
    current_route_id: str,
    disruption_location: str,
    routes: Dict[str, Any],
) -> Optional[Tuple[str, str]]:
    """
    Identify a viable alternative route that does not pass through the disruption.
    Returns (route_id, reason) or None.
    """
    disruption_loc = disruption_location.upper()

    for r_id, route in routes.items():
        if r_id == current_route_id:
            continue
        # Check if route connects same corridor or compatible destination
        if route.origin.lower() == origin.lower() and route.destination.lower() == destination.lower():
            route_corridors = f"{route.origin} {route.destination} {route.via}".upper()
            if disruption_loc not in route_corridors:
                return (r_id, f"Direct alternative via {route.via} bypassing {disruption_location}")

    # If no exact origin-destination match, check general corridor alternatives
    for r_id, route in routes.items():
        if r_id != current_route_id and route.status == "ACTIVE":
            route_corridors = f"{route.origin} {route.destination} {route.via}".upper()
            if disruption_loc not in route_corridors:
                return (r_id, f"Contingency lane via {route.via}")

    return None
