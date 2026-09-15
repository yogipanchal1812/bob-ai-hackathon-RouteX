"""
route_selector.py — Alternative route ranking logic.

Rules:
  - Only routes present in the seed/supplied data are returned.
  - No roads are invented.
  - Ranking is deterministic: lowest disruption_exposure first, then cost, then duration.
  - A primary route is identified, then alternatives are ranked against it.

If no alternative routes exist → returns empty list (no crash).
If primary route not found    → returns all matching origin/destination routes.
"""

import logging

from optimization.data import seed_data
from optimization.schemas.routes import AlternativeRouteResult, Route

logger = logging.getLogger(__name__)

# Routes with disruption_exposure above this threshold are considered "disrupted"
DEFAULT_EXPOSURE_THRESHOLD: float = 0.60


def _build_alternative_reasons(
    candidate: Route,
    primary: Route | None,
) -> list[str]:
    """Generate human-readable reasons for why a route is recommended."""
    reasons: list[str] = []

    if candidate.disruption_exposure < DEFAULT_EXPOSURE_THRESHOLD:
        reasons.append(
            f"Low disruption exposure ({candidate.disruption_exposure:.0%})"
        )

    if primary:
        if candidate.cost_usd < primary.cost_usd:
            reasons.append(
                f"Cheaper than primary route (${candidate.cost_usd:,.0f} vs ${primary.cost_usd:,.0f})"
            )
        elif candidate.cost_usd == primary.cost_usd:
            reasons.append("Same cost as primary route")
        else:
            reasons.append(
                f"Higher cost than primary (${candidate.cost_usd:,.0f} vs ${primary.cost_usd:,.0f}) — worth it for safety"
            )

        if candidate.duration_hours < primary.duration_hours:
            reasons.append(
                f"Faster than primary ({candidate.duration_hours}h vs {primary.duration_hours}h)"
            )
        elif candidate.duration_hours > primary.duration_hours:
            reasons.append(
                f"Slightly longer than primary ({candidate.duration_hours}h vs {primary.duration_hours}h)"
            )

    if "alternative" in candidate.tags:
        reasons.append("Designated alternative corridor")
    if "bypass" in candidate.tags:
        reasons.append("Bypass route avoiding disruption zone")
    if "inland" in candidate.tags:
        reasons.append("Inland route avoiding coastal/port disruption")

    if not reasons:
        reasons.append("Available route with acceptable disruption exposure")

    return reasons


def get_alternative_routes(
    primary_route_id: str,
    exposure_threshold: float = DEFAULT_EXPOSURE_THRESHOLD,
) -> list[AlternativeRouteResult]:
    """
    Return ranked alternative routes for a given primary route.

    Ranking criteria (in order):
        1. Lowest disruption_exposure
        2. Lowest cost_usd
        3. Lowest duration_hours

    Args:
        primary_route_id:   The route ID of the disrupted primary route.
        exposure_threshold: Routes with exposure ≥ this are considered disrupted.

    Returns:
        Sorted list of AlternativeRouteResult (rank 1 = best). Empty if none found.
    """
    all_routes = seed_data.get_routes()

    # Find the primary route
    primary: Route | None = next(
        (r for r in all_routes if r.route_id == primary_route_id), None
    )

    if primary is None:
        logger.warning("Primary route %s not found. Cannot rank alternatives.", primary_route_id)
        return []

    # Find alternative routes: same origin/destination, not the primary, below exposure threshold
    candidates: list[Route] = [
        r
        for r in all_routes
        if r.route_id != primary_route_id
        and r.origin == primary.origin
        and r.destination == primary.destination
        and r.disruption_exposure < exposure_threshold
    ]

    if not candidates:
        logger.info(
            "No alternative routes found for %s (origin=%s, destination=%s).",
            primary_route_id,
            primary.origin,
            primary.destination,
        )
        return []

    # Sort: disruption_exposure ASC, cost ASC, duration ASC
    candidates.sort(
        key=lambda r: (r.disruption_exposure, r.cost_usd, r.duration_hours)
    )

    results: list[AlternativeRouteResult] = []
    for rank, candidate in enumerate(candidates, start=1):
        savings = max(0.0, primary.cost_usd - candidate.cost_usd)
        time_delta = candidate.duration_hours - primary.duration_hours  # positive = slower
        reasons = _build_alternative_reasons(candidate, primary)

        results.append(
            AlternativeRouteResult(
                rank=rank,
                route=candidate,
                reason=reasons,
                savings_usd=round(savings, 2),
                time_delta_hours=round(time_delta, 2),
            )
        )

    return results


def get_routes_for_disruption(disruption_id: str) -> list[AlternativeRouteResult]:
    """
    Return alternative route suggestions for all routes affected by a disruption.

    Looks up the disruption's affected_routes, then finds alternatives for each.
    """
    disruption = seed_data.get_disruption_by_id(disruption_id)
    if not disruption:
        logger.warning("Disruption %s not found.", disruption_id)
        return []

    affected_route_ids: list[str] = disruption.get("affected_routes", [])
    all_alternatives: list[AlternativeRouteResult] = []

    for route_id in affected_route_ids:
        alternatives = get_alternative_routes(route_id)
        all_alternatives.extend(alternatives)

    return all_alternatives
