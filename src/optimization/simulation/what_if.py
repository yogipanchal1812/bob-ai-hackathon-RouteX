"""
what_if.py — What-if simulation orchestrator.

Implements the full POST /api/what-if contract from the shared API spec:

    Input:
        { "disruption_id": "D001", "duration_days": 5 }

    Output:
        {
            "baseline": { "affected_shipments": int, "high_risk": int, "estimated_impact": float },
            "scenario": { "affected_shipments": int, "high_risk": int, "estimated_impact": float },
            "delta":    { "affected_shipments": int, "high_risk": int, "estimated_impact": float },
            "recommended_actions": [ { "action": str, "priority": str, "target": str, "reason": str } ]
        }

Response structure is STABLE — do not change field names.
Recommended action types: REROUTE_SHIPMENT | ASSIGN_VEHICLE | CHANGE_CARRIER |
                           PRIORITIZE_SHIPMENT | MONITOR_ROUTE
"""

import logging

from optimization.data import seed_data
from optimization.routing.carrier_selector import select_alternative_carrier
from optimization.routing.route_selector import get_routes_for_disruption
from optimization.schemas.simulation import (
    RecommendedAction,
    ScenarioSnapshot,
    WhatIfResponse,
)
from optimization.simulation.comparison import compute_delta
from optimization.simulation.scenario import compute_scenario_snapshot

logger = logging.getLogger(__name__)

# Risk score thresholds (shared engineering rules, Rule 13-14)
HIGH_RISK_THRESHOLD: int = 70      # score >= 70 → HIGH or CRITICAL


def _generate_recommended_actions(
    disruption_id: str,
    duration_days: int,
    scenario: ScenarioSnapshot,
    baseline: ScenarioSnapshot,
) -> list[RecommendedAction]:
    """
    Generate structured recommended actions based on scenario severity.

    Rules:
        - Actions are deterministic given the same inputs.
        - Only generates actions for real shipments/routes in the data.
        - Actions are prioritised: HIGH if delta is significant, MEDIUM/LOW otherwise.
        - No fake action targets.
    """
    actions: list[RecommendedAction] = []

    disruption = seed_data.get_disruption_by_id(disruption_id)
    if not disruption:
        # No disruption found — cannot generate meaningful actions
        logger.warning("Disruption %s not found; no actions generated.", disruption_id)
        return []

    affected_shipments = seed_data.get_shipments_by_disruption(disruption_id)
    affected_route_ids: list[str] = disruption.get("affected_routes", [])

    delta_affected = scenario.affected_shipments - baseline.affected_shipments
    severity = disruption.get("severity", "MEDIUM")

    # --- 1. REROUTE_SHIPMENT for routes with high disruption exposure ---
    alternatives = get_routes_for_disruption(disruption_id)
    for alt in alternatives[:2]:  # Cap at 2 reroute actions to avoid noise
        # Find a shipment that uses this route
        for s in affected_shipments:
            if s["route_id"] in affected_route_ids:
                actions.append(
                    RecommendedAction(
                        action="REROUTE_SHIPMENT",
                        priority="HIGH" if severity in ("HIGH", "CRITICAL") else "MEDIUM",
                        target=s["shipment_id"],
                        reason=(
                            f"Primary route {s['route_id']} has high disruption exposure. "
                            f"Alternative route {alt.route.route_id} available via "
                            f"{alt.route.origin} → {alt.route.destination} "
                            f"with {alt.route.disruption_exposure:.0%} exposure."
                        ),
                    )
                )
                break

    # --- 2. ASSIGN_VEHICLE for high-risk shipments without a vehicle ---
    high_risk_shipments = [s for s in affected_shipments if s["risk_score"] >= HIGH_RISK_THRESHOLD]
    for s in high_risk_shipments[:2]:
        actions.append(
            RecommendedAction(
                action="ASSIGN_VEHICLE",
                priority="HIGH",
                target=s["shipment_id"],
                reason=(
                    f"Shipment {s['shipment_id']} has risk score {s['risk_score']} "
                    f"({'CRITICAL' if s['risk_score'] >= 90 else 'HIGH'}) — "
                    f"priority vehicle assignment required to maintain SLA."
                ),
            )
        )

    # --- 3. CHANGE_CARRIER if disruption affects carrier operations ---
    if duration_days >= 3 and affected_shipments:
        # Use the carrier of the most critical shipment
        most_critical = max(affected_shipments, key=lambda s: s["risk_score"])
        alt_carrier = select_alternative_carrier(most_critical["carrier_id"])
        if alt_carrier:
            actions.append(
                RecommendedAction(
                    action="CHANGE_CARRIER",
                    priority="MEDIUM",
                    target=most_critical["shipment_id"],
                    reason=(
                        f"Disruption lasting {duration_days}+ days threatens carrier "
                        f"{most_critical['carrier_id']} reliability. "
                        f"Recommended alternative: {alt_carrier['name']} "
                        f"(reliability score: {alt_carrier['reliability_score']})."
                    ),
                )
            )

    # --- 4. PRIORITIZE_SHIPMENT for high-risk above threshold ---
    for s in high_risk_shipments[:1]:
        actions.append(
            RecommendedAction(
                action="PRIORITIZE_SHIPMENT",
                priority="HIGH",
                target=s["shipment_id"],
                reason=(
                    f"Shipment {s['shipment_id']} is high-risk (score {s['risk_score']}). "
                    f"Move to top of dispatch queue and assign dedicated tracking."
                ),
            )
        )

    # --- 5. MONITOR_ROUTE for routes with moderate exposure ---
    for route_id in affected_route_ids:
        actions.append(
            RecommendedAction(
                action="MONITOR_ROUTE",
                priority="LOW" if duration_days <= 1 else "MEDIUM",
                target=route_id,
                reason=(
                    f"Route {route_id} affected by disruption {disruption_id}. "
                    f"Monitor for changes in disruption status every 6 hours."
                ),
            )
        )

    # De-duplicate by (action, target) — keep first occurrence
    seen: set[tuple[str, str]] = set()
    unique_actions: list[RecommendedAction] = []
    for action in actions:
        key = (action.action, action.target)
        if key not in seen:
            seen.add(key)
            unique_actions.append(action)

    return unique_actions


def run_what_if(disruption_id: str, duration_days: int) -> WhatIfResponse:
    """
    Execute a what-if simulation for a disruption scenario.

    Args:
        disruption_id: The disruption to simulate.
        duration_days: Duration of the disruption in days (must be ≥ 0).

    Returns:
        WhatIfResponse with baseline, scenario, delta, and recommended_actions.
    """
    logger.info(
        "Running what-if simulation: disruption=%s, duration=%d days",
        disruption_id,
        duration_days,
    )

    # Baseline = state if disruption lasts 0 days (current impact only)
    baseline: ScenarioSnapshot = compute_scenario_snapshot(disruption_id, 0)

    # Scenario = projected state after duration_days
    scenario: ScenarioSnapshot = compute_scenario_snapshot(disruption_id, duration_days)

    # Delta = difference (always non-negative)
    delta = compute_delta(baseline, scenario)

    # Recommended actions
    actions = _generate_recommended_actions(disruption_id, duration_days, scenario, baseline)

    return WhatIfResponse(
        baseline=baseline,
        scenario=scenario,
        delta=delta,
        recommended_actions=actions,
    )
