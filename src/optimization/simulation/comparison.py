"""
comparison.py — Delta computation between baseline and scenario snapshots.

Rules:
  - Delta values are always ≥ 0 (disruptions make things worse, not better).
  - Uses max(0, scenario - baseline) to prevent negative deltas from floating-point drift.
  - No random values. Fully deterministic.
"""

import math

from optimization.schemas.simulation import ScenarioSnapshot, WhatIfDelta


def compute_delta(baseline: ScenarioSnapshot, scenario: ScenarioSnapshot) -> WhatIfDelta:
    """
    Compute the difference between a scenario and a baseline snapshot.

    Args:
        baseline: The current/unaffected state (typically duration_days=0).
        scenario: The projected state under the simulated disruption duration.

    Returns:
        WhatIfDelta with non-negative values only.
    """
    delta_affected = max(0, scenario.affected_shipments - baseline.affected_shipments)
    delta_high_risk = max(0, scenario.high_risk - baseline.high_risk)
    delta_impact = max(0.0, scenario.estimated_impact - baseline.estimated_impact)

    return WhatIfDelta(
        affected_shipments=delta_affected,
        high_risk=delta_high_risk,
        estimated_impact=round(delta_impact, 2),
    )
