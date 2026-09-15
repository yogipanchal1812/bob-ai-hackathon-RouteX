"""
RouteX Backend — Risk Engine.

Deterministic, explainable, weighted-factor risk scoring.
No fake ML — every factor is transparent and reproducible.

Weights:
    Disruption severity   30 %
    Route exposure        25 %
    Disruption duration   15 %
    Shipment priority     15 %
    Cargo value           10 %
    Carrier reliability    5 %

Risk level boundaries:
    0–39   LOW
    40–69  MEDIUM
    70–89  HIGH
    90–100 CRITICAL
"""

from typing import Any, Dict

from app.models.carrier import Carrier
from app.models.common import risk_level_from_score
from app.models.disruption import Disruption
from app.models.route import Route
from app.models.shipment import Shipment
from app.services.data_loader import get_data_store

# ── Severity / Priority → normalised score ────────────────────────────────────

SEVERITY_SCORES: Dict[str, float] = {
    "LOW": 20.0,
    "MEDIUM": 45.0,
    "HIGH": 75.0,
    "CRITICAL": 100.0,
}

PRIORITY_SCORES: Dict[str, float] = {
    "LOW": 20.0,
    "MEDIUM": 40.0,
    "HIGH": 70.0,
    "CRITICAL": 100.0,
}

# ── Weights ───────────────────────────────────────────────────────────────────

WEIGHT_SEVERITY: float = 0.30
WEIGHT_ROUTE_EXPOSURE: float = 0.25
WEIGHT_DURATION: float = 0.15
WEIGHT_PRIORITY: float = 0.15
WEIGHT_CARGO_VALUE: float = 0.10
WEIGHT_CARRIER_RELIABILITY: float = 0.05

# ── Normalisation caps ────────────────────────────────────────────────────────

MAX_DURATION_DAYS: int = 30
MAX_CARGO_VALUE: float = 5_000_000.0


# ── Helpers ───────────────────────────────────────────────────────────────────


def _impact_label(score: float) -> str:
    """Map a normalised factor score to a human-readable impact label."""
    if score >= 70:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    else:
        return "LOW"


def is_route_exposed(route: Route, disruption: Disruption) -> bool:
    """
    Determine whether *route* passes through the disruption's location.

    Checks if the disruption location string appears anywhere in the
    route's origin, destination, or via fields (case-insensitive).
    """
    disruption_loc = disruption.location.upper()
    searchable = f"{route.origin} {route.destination} {route.via}".upper()
    return disruption_loc in searchable


# ── Core risk calculation ─────────────────────────────────────────────────────


def calculate_risk(
    shipment: Shipment,
    disruption: Disruption,
) -> Dict[str, Any]:
    """
    Calculate a deterministic risk score for *shipment* given *disruption*.

    Returns a dict containing:
        shipment_id  – echoed back for convenience
        risk_score   – integer 0–100
        risk_level   – LOW | MEDIUM | HIGH | CRITICAL
        factors      – list of explainable factor dicts
    """
    store = get_data_store()
    route: Route | None = store.routes.get(shipment.route_id)
    carrier: Carrier | None = store.carriers.get(shipment.carrier_id)

    # Factor 1 — Disruption severity
    severity_score = SEVERITY_SCORES.get(disruption.severity.upper(), 0.0)

    # Factor 2 — Route exposure (binary: exposed or not)
    route_exposure = 0.0
    if route and is_route_exposed(route, disruption):
        route_exposure = 100.0

    # Factor 3 — Disruption duration (normalised, capped)
    duration_days = max(disruption.duration_days, 0)
    duration_score = min(duration_days / MAX_DURATION_DAYS, 1.0) * 100.0

    # Factor 4 — Shipment priority
    priority_score = PRIORITY_SCORES.get(shipment.priority.upper(), 20.0)

    # Factor 5 — Cargo value (normalised, capped)
    cargo_value = max(shipment.cargo_value, 0.0)
    value_score = min(cargo_value / MAX_CARGO_VALUE, 1.0) * 100.0

    # Factor 6 — Carrier reliability (inverted: low reliability → high risk)
    reliability = carrier.reliability_score if carrier else 0.5
    carrier_score = (1.0 - reliability) * 100.0

    # Weighted sum
    raw_score = (
        severity_score * WEIGHT_SEVERITY
        + route_exposure * WEIGHT_ROUTE_EXPOSURE
        + duration_score * WEIGHT_DURATION
        + priority_score * WEIGHT_PRIORITY
        + value_score * WEIGHT_CARGO_VALUE
        + carrier_score * WEIGHT_CARRIER_RELIABILITY
    )

    risk_score = max(0, min(100, round(raw_score)))
    risk_level = risk_level_from_score(risk_score)

    factors = [
        {
            "factor": "Disruption severity",
            "score": round(severity_score, 1),
            "weight": WEIGHT_SEVERITY,
            "impact": _impact_label(severity_score),
        },
        {
            "factor": "Route exposure",
            "score": round(route_exposure, 1),
            "weight": WEIGHT_ROUTE_EXPOSURE,
            "impact": _impact_label(route_exposure),
        },
        {
            "factor": "Disruption duration",
            "score": round(duration_score, 1),
            "weight": WEIGHT_DURATION,
            "impact": _impact_label(duration_score),
        },
        {
            "factor": "Shipment priority",
            "score": round(priority_score, 1),
            "weight": WEIGHT_PRIORITY,
            "impact": _impact_label(priority_score),
        },
        {
            "factor": "Cargo value",
            "score": round(value_score, 1),
            "weight": WEIGHT_CARGO_VALUE,
            "impact": _impact_label(value_score),
        },
        {
            "factor": "Carrier reliability",
            "score": round(carrier_score, 1),
            "weight": WEIGHT_CARRIER_RELIABILITY,
            "impact": _impact_label(carrier_score),
        },
    ]

    return {
        "shipment_id": shipment.shipment_id,
        "risk_score": risk_score,
        "risk_level": risk_level.value,
        "factors": factors,
    }
