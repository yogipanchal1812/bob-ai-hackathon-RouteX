"""
RouteX AI Module — Recommendation Service.

Generates structured, explainable operational recommendations grounded
in RouteX shipment, disruption, and route data.
"""

from typing import Any, Dict, List, Optional

from ai.recommendations.rules import (
    calculate_confidence,
    determine_recommendation_priority,
    find_alternative_route,
)
from ai.schemas.recommendation import Recommendation


class RecommendationService:
    """Service to produce structured supply-chain recommendations."""

    def __init__(self, data_store=None):
        if data_store:
            self.store = data_store
        else:
            try:
                from app.services.data_loader import get_data_store
                self.store = get_data_store()
            except ImportError:
                self.store = None

    def generate_recommendations(
        self,
        shipment_id: Optional[str] = None,
        disruption_id: Optional[str] = None,
        max_count: int = 5,
    ) -> List[Recommendation]:
        """
        Generate prioritized recommendations for a shipment, a disruption,
        or the top-risk items across the entire network.
        """
        if not self.store:
            return []

        recommendations: List[Recommendation] = []

        if shipment_id:
            rec = self._recommend_for_shipment(shipment_id)
            if rec:
                recommendations.append(rec)
            return recommendations

        if disruption_id:
            return self._recommend_for_disruption(disruption_id, max_count)

        # Global recommendations across active disruptions
        return self._recommend_global(max_count)

    def _recommend_for_shipment(self, shipment_id: str) -> Optional[Recommendation]:
        """Produce a recommendation for a single target shipment."""
        shipment = self.store.shipments.get(shipment_id)
        if not shipment:
            return None

        route = self.store.routes.get(shipment.route_id)
        carrier = self.store.carriers.get(shipment.carrier_id)
        carrier_rel = carrier.reliability_score if carrier else 0.75

        # Check which active disruptions affect this route
        active_disruptions = [d for d in self.store.disruptions.values() if d.status == "ACTIVE"]
        matched_disruption = None

        if route:
            route_text = f"{route.origin} {route.destination} {route.via}".upper()
            for d in active_disruptions:
                if d.location.upper() in route_text:
                    matched_disruption = d
                    break

        if not matched_disruption:
            return Recommendation(
                action="MONITOR",
                priority="LOW",
                shipment_id=shipment.shipment_id,
                reason=f"Shipment {shipment.shipment_id} has no active disruption exposure on corridor {shipment.route_id}.",
                confidence=0.95,
            )

        # Find alternative route
        alt_route = find_alternative_route(
            origin=shipment.origin,
            destination=shipment.destination,
            current_route_id=shipment.route_id,
            disruption_location=matched_disruption.location,
            routes=self.store.routes,
        )

        alt_route_id = alt_route[0] if alt_route else "R002"
        priority = determine_recommendation_priority(
            risk_level=matched_disruption.severity,
            priority=shipment.priority,
            cargo_value=shipment.cargo_value,
            cargo_type=shipment.cargo_type,
        )

        action = "REROUTE" if matched_disruption.duration_days >= 7 else "CARRIER_EXPEDITE"
        confidence = calculate_confidence(
            carrier_reliability=carrier_rel,
            disruption_severity=matched_disruption.severity,
            shipment_priority=shipment.priority,
            alternative_available=bool(alt_route),
        )

        return Recommendation(
            action=action,
            priority=priority,
            shipment_id=shipment.shipment_id,
            recommended_route=alt_route_id,
            carrier_id=shipment.carrier_id,
            reason=(
                f"Exposed to {matched_disruption.location} ({matched_disruption.severity}, "
                f"{matched_disruption.duration_days}d delay). Rerouting via {alt_route_id} "
                f"protects ${shipment.cargo_value:,.0f} of {shipment.cargo_type}."
            ),
            confidence=confidence,
        )

    def _recommend_for_disruption(self, disruption_id: str, max_count: int) -> List[Recommendation]:
        """Produce recommendations for all shipments exposed to a disruption."""
        disruption = self.store.disruptions.get(disruption_id)
        if not disruption:
            return []

        recs: List[Recommendation] = []
        for s in self.store.shipments.values():
            route = self.store.routes.get(s.route_id)
            if not route:
                continue
            corridor = f"{route.origin} {route.destination} {route.via}".upper()
            if disruption.location.upper() in corridor:
                rec = self._recommend_for_shipment(s.shipment_id)
                if rec:
                    recs.append(rec)
            if len(recs) >= max_count:
                break

        # Sort by priority: CRITICAL > HIGH > MEDIUM > LOW
        p_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        recs.sort(key=lambda r: p_order.get(r.priority, 99))
        return recs

    def _recommend_global(self, max_count: int) -> List[Recommendation]:
        """Produce top operational recommendations across the whole network."""
        recs: List[Recommendation] = []
        for s in self.store.shipments.values():
            rec = self._recommend_for_shipment(s.shipment_id)
            if rec and rec.action != "MONITOR":
                recs.append(rec)

        p_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        recs.sort(key=lambda r: p_order.get(r.priority, 99))
        return recs[:max_count]
