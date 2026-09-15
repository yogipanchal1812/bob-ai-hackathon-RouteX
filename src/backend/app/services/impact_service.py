"""
RouteX Backend — Impact Analysis Service.

Analyses the impact of a disruption on affected shipments:
    • identifies exposed shipments via route matching
    • calculates per-shipment risk scores
    • estimates delay and financial impact
    • aggregates summary statistics

Also provides a global impact summary across all active disruptions.
"""

from typing import Any, Dict, List

from app.models.common import risk_level_from_score
from app.services.data_loader import get_data_store
from app.services.disruption_service import get_disruption_by_id
from app.services.risk_service import calculate_risk, is_route_exposed

# ── Severity → delay multiplier ──────────────────────────────────────────────

SEVERITY_DELAY_MULTIPLIER: Dict[str, float] = {
    "LOW": 0.25,
    "MEDIUM": 0.50,
    "HIGH": 0.75,
    "CRITICAL": 1.0,
}

# Fraction of cargo value considered at risk per delay-day relative to
# the route's estimated transit time.
IMPACT_RATE: float = 0.15


# ── Helpers ───────────────────────────────────────────────────────────────────


def _estimate_delay(duration_days: int, severity: str) -> float:
    """Estimate expected delay based on disruption duration and severity."""
    multiplier = SEVERITY_DELAY_MULTIPLIER.get(severity.upper(), 0.5)
    return round(duration_days * multiplier, 1)


def _estimate_financial_impact(
    cargo_value: float,
    delay_days: float,
    estimated_transit_days: int,
) -> float:
    """
    Estimate financial impact of a delay.

    Formula:  cargo_value × (delay_days / estimated_transit_days) × IMPACT_RATE
    """
    if estimated_transit_days <= 0:
        return 0.0
    impact = cargo_value * (delay_days / estimated_transit_days) * IMPACT_RATE
    return round(impact, 2)


# ── Core analysis ─────────────────────────────────────────────────────────────


def analyze_disruption(disruption_id: str) -> Dict[str, Any]:
    """
    Analyse a single disruption's impact on all shipments.

    Returns a stable response structure with:
        disruption metadata, affected_shipments list, summary object.
    """
    disruption = get_disruption_by_id(disruption_id)  # raises 404 if missing
    store = get_data_store()

    affected_shipments: List[Dict[str, Any]] = []
    total_impact: float = 0.0
    total_delay: float = 0.0
    risk_counts = {
        "low_risk": 0,
        "medium_risk": 0,
        "high_risk": 0,
        "critical_risk": 0,
    }

    for shipment in store.shipments.values():
        route = store.routes.get(shipment.route_id)
        if not route:
            continue
        if not is_route_exposed(route, disruption):
            continue

        # Risk
        risk_result = calculate_risk(shipment, disruption)

        # Delay
        delay_days = _estimate_delay(disruption.duration_days, disruption.severity)

        # Financial impact
        financial_impact = _estimate_financial_impact(
            shipment.cargo_value, delay_days, route.estimated_days
        )

        affected_shipments.append(
            {
                "shipment_id": shipment.shipment_id,
                "origin": shipment.origin,
                "destination": shipment.destination,
                "cargo_type": shipment.cargo_type,
                "cargo_value": shipment.cargo_value,
                "priority": shipment.priority,
                "risk_score": risk_result["risk_score"],
                "risk_level": risk_result["risk_level"],
                "estimated_delay_days": delay_days,
                "estimated_impact": financial_impact,
                "factors": risk_result["factors"],
            }
        )

        total_impact += financial_impact
        total_delay += delay_days

        level = risk_result["risk_level"]
        if level == "LOW":
            risk_counts["low_risk"] += 1
        elif level == "MEDIUM":
            risk_counts["medium_risk"] += 1
        elif level == "HIGH":
            risk_counts["high_risk"] += 1
        elif level == "CRITICAL":
            risk_counts["critical_risk"] += 1

    total_affected = len(affected_shipments)
    avg_delay = round(total_delay / total_affected, 1) if total_affected > 0 else 0.0

    return {
        "disruption_id": disruption.disruption_id,
        "disruption_type": disruption.type,
        "disruption_severity": disruption.severity,
        "disruption_location": disruption.location,
        "affected_shipments": affected_shipments,
        "summary": {
            "total_affected": total_affected,
            "low_risk": risk_counts["low_risk"],
            "medium_risk": risk_counts["medium_risk"],
            "high_risk": risk_counts["high_risk"],
            "critical_risk": risk_counts["critical_risk"],
            "estimated_impact": round(total_impact, 2),
            "estimated_delay_days": avg_delay,
        },
    }


# ── Global summary ────────────────────────────────────────────────────────────


def get_impact_summary() -> Dict[str, Any]:
    """
    Return an aggregated impact summary across **all active disruptions**.
    """
    store = get_data_store()

    active_disruptions = [
        d for d in store.disruptions.values() if d.status == "ACTIVE"
    ]

    disruption_items: List[Dict[str, Any]] = []
    global_affected = 0
    global_impact: float = 0.0
    global_risk = {
        "low_risk": 0,
        "medium_risk": 0,
        "high_risk": 0,
        "critical_risk": 0,
    }

    for disruption in active_disruptions:
        result = analyze_disruption(disruption.disruption_id)
        summary = result["summary"]

        disruption_items.append(
            {
                "disruption_id": disruption.disruption_id,
                "location": disruption.location,
                "type": disruption.type,
                "severity": disruption.severity,
                "total_affected": summary["total_affected"],
                "estimated_impact": summary["estimated_impact"],
                "estimated_delay_days": summary["estimated_delay_days"],
            }
        )

        global_affected += summary["total_affected"]
        global_impact += summary["estimated_impact"]
        for key in global_risk:
            global_risk[key] += summary[key]

    return {
        "total_active_disruptions": len(active_disruptions),
        "total_affected_shipments": global_affected,
        "total_estimated_impact": round(global_impact, 2),
        "risk_distribution": global_risk,
        "disruptions": disruption_items,
    }
