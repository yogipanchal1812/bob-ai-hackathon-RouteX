"""
carrier_selector.py — Carrier recommendation for shipment rerouting.

Selection criteria (deterministic):
    1. Carrier must NOT be the same as the disrupted carrier (avoid same issue)
    2. Highest reliability_score wins
    3. Tie-break: lowest cost_index

Returns None if no alternative carriers are available (no crash).
"""

import logging

from optimization.data import seed_data

logger = logging.getLogger(__name__)


def select_alternative_carrier(
    current_carrier_id: str,
) -> dict | None:
    """
    Recommend an alternative carrier avoiding the current one.

    Args:
        current_carrier_id: The carrier ID currently assigned to the shipment.

    Returns:
        Carrier dict with carrier_id, name, reliability_score, cost_index.
        None if no alternatives exist.
    """
    carriers = seed_data.get_carriers()

    alternatives = [c for c in carriers if c["carrier_id"] != current_carrier_id]

    if not alternatives:
        logger.warning(
            "No alternative carriers available besides %s.", current_carrier_id
        )
        return None

    # Sort: highest reliability first, lowest cost_index second
    alternatives.sort(key=lambda c: (-c["reliability_score"], c["cost_index"]))

    best = alternatives[0]
    logger.info(
        "Recommended carrier: %s (reliability=%d, cost_index=%.2f)",
        best["carrier_id"],
        best["reliability_score"],
        best["cost_index"],
    )
    return best


def get_carrier_by_id(carrier_id: str) -> dict | None:
    """Look up a carrier by ID. Returns None if not found."""
    for carrier in seed_data.get_carriers():
        if carrier["carrier_id"] == carrier_id:
            return carrier
    return None
