"""
scenario.py — Deterministic scenario snapshot computation.

A ScenarioSnapshot represents the projected supply chain state after a
disruption has lasted 'duration_days' days.

Calculation model (documented, no random values):
    base_affected   = count of shipments directly tied to this disruption (from seed data)
    base_high_risk  = count of base_affected shipments with risk_score >= 70

    For duration_days > 0, cascading effects are modelled as:
        cascade_factor = min(duration_days, MAX_CASCADE_DAYS) / MAX_CASCADE_DAYS
        extra_affected = floor(TOTAL_SHIPMENTS * cascade_factor * SPREAD_RATE)
        extra_high_risk = floor(extra_affected * HIGH_RISK_RATE)
        impact_usd  = base_impact + (extra_affected * DAILY_IMPACT_PER_SHIPMENT * duration_days)

    All values are non-negative integers/floats.
    Values are capped at the total number of shipments (no fabrication).

Tested against: 0, 1, 3, 5, 7 day profiles — all return consistent, deterministic results.
"""

import math

from optimization.data import seed_data
from optimization.schemas.simulation import ScenarioSnapshot

# --------------------------------------------------------------------------
# Model constants (tuned for the 10-shipment seed dataset)
# --------------------------------------------------------------------------
MAX_CASCADE_DAYS: int = 7        # Cascade effect plateaus after 7 days
SPREAD_RATE: float = 0.4         # 40% of non-disrupted shipments get affected at full cascade
HIGH_RISK_RATE: float = 0.6      # 60% of cascaded affected become high-risk
DAILY_IMPACT_PER_SHIPMENT: float = 15_000.0   # USD per affected shipment per day
BASE_IMPACT_PER_SHIPMENT: float = 25_000.0    # USD per directly-affected shipment


def compute_scenario_snapshot(
    disruption_id: str,
    duration_days: int,
) -> ScenarioSnapshot:
    """
    Compute a supply chain impact snapshot for a given disruption duration.

    Args:
        disruption_id: The disruption being simulated.
        duration_days: Number of days the disruption lasts (≥ 0).

    Returns:
        ScenarioSnapshot with affected_shipments, high_risk, estimated_impact.

    Raises:
        Never — returns zeros if disruption or shipments not found.
    """
    # Clamp duration to non-negative (validation done in WhatIfRequest, but be safe)
    duration_days = max(0, duration_days)

    all_shipments = seed_data.get_shipments()
    total_shipments = len(all_shipments)

    # --- Baseline directly-affected shipments ---
    directly_affected = [
        s for s in all_shipments if s["disruption_id"] == disruption_id
    ]
    base_affected_count = len(directly_affected)

    # Risk threshold: HIGH = score 70-89, CRITICAL = 90-100
    base_high_risk = sum(
        1 for s in directly_affected if s["risk_score"] >= 70
    )

    base_impact = base_affected_count * BASE_IMPACT_PER_SHIPMENT

    # If no shipments are linked to this disruption, return zeros immediately.
    # Cascade must NOT spread to other disruptions' shipments — that would
    # fabricate impact for an unrelated or non-existent disruption.
    if base_affected_count == 0:
        return ScenarioSnapshot(
            affected_shipments=0,
            high_risk=0,
            estimated_impact=0.0,
        )

    if duration_days == 0:
        return ScenarioSnapshot(
            affected_shipments=base_affected_count,
            high_risk=base_high_risk,
            estimated_impact=round(base_impact, 2),
        )

    # --- Cascade effect for duration_days > 0 ---
    # Cascade grows linearly with duration, plateaus at MAX_CASCADE_DAYS.
    # Only applies when the disruption has at least one directly-affected shipment.
    cascade_factor = min(duration_days, MAX_CASCADE_DAYS) / MAX_CASCADE_DAYS

    # Extra affected = proportion of remaining (non-directly-affected) shipments
    remaining_shipments = max(0, total_shipments - base_affected_count)
    extra_affected = math.floor(remaining_shipments * cascade_factor * SPREAD_RATE)

    total_affected = min(base_affected_count + extra_affected, total_shipments)

    # Extra high-risk from cascaded shipments
    extra_high_risk = math.floor(extra_affected * HIGH_RISK_RATE)
    total_high_risk = min(base_high_risk + extra_high_risk, total_affected)

    # Financial impact: base + daily accumulation for all affected shipments
    cascaded_impact = extra_affected * DAILY_IMPACT_PER_SHIPMENT * duration_days
    total_impact = base_impact + cascaded_impact

    return ScenarioSnapshot(
        affected_shipments=total_affected,
        high_risk=total_high_risk,
        estimated_impact=round(total_impact, 2),
    )
