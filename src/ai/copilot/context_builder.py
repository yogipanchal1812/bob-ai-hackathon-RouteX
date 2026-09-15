"""
RouteX AI Module — Controlled Context Builder.

Extracts targeted, relevant supply-chain context based on the user's query.
Prevents arbitrary dumping of large raw data dumps into LLM prompts.
Enforces strict anti-hallucination tracking for unrecognized entity IDs.
"""

import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Ensure backend package is accessible for data store
_backend_path = Path(__file__).resolve().parent.parent.parent / "backend"
if _backend_path.exists() and str(_backend_path) not in sys.path:
    sys.path.insert(0, str(_backend_path))

try:
    from app.services.data_loader import get_data_store
    from app.services.impact_service import analyze_disruption
    from app.services.risk_service import is_route_exposed
except ImportError:
    # Graceful fallback if data store unavailable
    get_data_store = None
    analyze_disruption = None
    is_route_exposed = None


class ContextBuilder:
    """Selectively extracts and packages context for a given query."""

    ENTITY_REGEX = {
        "shipment": re.compile(r"\bSH\d{3,4}\b", re.IGNORECASE),
        "disruption": re.compile(r"\bD\d{3,4}\b", re.IGNORECASE),
        "route": re.compile(r"\bR\d{3,4}\b", re.IGNORECASE),
        "carrier": re.compile(r"\bC\d{3,4}\b", re.IGNORECASE),
    }

    LOCATION_KEYWORDS = [
        "suez", "malacca", "panama", "mumbai", "shanghai",
        "los angeles", "pacific", "mediterranean", "singapore", "rotterdam"
    ]

    def __init__(self, data_store=None):
        if data_store:
            self.store = data_store
        elif get_data_store:
            self.store = get_data_store()
        else:
            self.store = None

    def extract_entity_ids(self, text: str) -> Dict[str, List[str]]:
        """Find explicit entity IDs mentioned in text."""
        matches = {}
        for entity_type, pattern in self.ENTITY_REGEX.items():
            found = pattern.findall(text)
            matches[entity_type] = [item.upper() for item in found]
        return matches

    def build_context(self, query: str, extra_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Build a concise, structured context payload for the query.
        Guarantees:
        - No full CSV dumps
        - Precise identification of targeted entities
        - Clear notation of missing/unknown entity IDs to prevent hallucination
        """
        extracted = self.extract_entity_ids(query)
        shipment_ids = extracted.get("shipment", [])
        disruption_ids = extracted.get("disruption", [])
        route_ids = extracted.get("route", [])
        carrier_ids = extracted.get("carrier", [])

        query_lower = query.lower()
        mentioned_locations = [loc for loc in self.LOCATION_KEYWORDS if loc in query_lower]

        unknown_entities: List[str] = []
        target_shipments: List[Dict[str, Any]] = []
        target_disruptions: List[Dict[str, Any]] = []
        sources: Set[str] = set()

        if not self.store:
            return {
                "error": "Data store is currently unavailable",
                "sources": [],
                "target_shipments": [],
                "target_disruptions": [],
                "unknown_entities": [],
            }

        # 1. Resolve requested shipments
        for s_id in shipment_ids:
            shipment = self.store.shipments.get(s_id)
            if shipment:
                route = self.store.routes.get(shipment.route_id)
                carrier = self.store.carriers.get(shipment.carrier_id)
                target_shipments.append({
                    "shipment_id": shipment.shipment_id,
                    "origin": shipment.origin,
                    "destination": shipment.destination,
                    "route_id": shipment.route_id,
                    "route_via": route.via if route else "Unknown",
                    "carrier_id": shipment.carrier_id,
                    "carrier_name": carrier.name if carrier else "Unknown",
                    "carrier_reliability": carrier.reliability_score if carrier else 0.5,
                    "cargo_type": shipment.cargo_type,
                    "cargo_value": shipment.cargo_value,
                    "priority": shipment.priority,
                    "status": shipment.status,
                    "eta": shipment.eta,
                })
                sources.add(f"shipment:{s_id}")
            else:
                unknown_entities.append(f"shipment:{s_id}")

        # 2. Resolve requested disruptions
        for d_id in disruption_ids:
            disruption = self.store.disruptions.get(d_id)
            if disruption:
                target_disruptions.append({
                    "disruption_id": disruption.disruption_id,
                    "location": disruption.location,
                    "type": disruption.type,
                    "severity": disruption.severity,
                    "duration_days": disruption.duration_days,
                    "status": disruption.status,
                    "description": disruption.description,
                })
                sources.add(f"disruption:{d_id}")
            else:
                unknown_entities.append(f"disruption:{d_id}")

        # 3. Match location keywords if no explicit disruption IDs given
        if not target_disruptions and mentioned_locations:
            for d in self.store.disruptions.values():
                d_loc = d.location.lower()
                if any(loc in d_loc for loc in mentioned_locations):
                    target_disruptions.append({
                        "disruption_id": d.disruption_id,
                        "location": d.location,
                        "type": d.type,
                        "severity": d.severity,
                        "duration_days": d.duration_days,
                        "status": d.status,
                        "description": d.description,
                    })
                    sources.add(f"disruption:{d.disruption_id}")

        # 4. Extract active disruptions & impact summary for general queries
        active_disruptions = [
            {
                "disruption_id": d.disruption_id,
                "location": d.location,
                "severity": d.severity,
                "duration_days": d.duration_days,
            }
            for d in self.store.disruptions.values()
            if d.status == "ACTIVE"
        ]

        # 5. Extract available alternative routes for bypass consideration
        available_routes = [
            {
                "route_id": r.route_id,
                "origin": r.origin,
                "destination": r.destination,
                "via": r.via,
                "distance_km": r.distance_km,
                "estimated_days": r.estimated_days,
                "status": r.status,
            }
            for r in self.store.routes.values()
            if r.status == "ACTIVE"
        ]

        # 6. Extract high-performing carriers for fleet utilization
        active_carriers = [
            {
                "carrier_id": c.carrier_id,
                "name": c.name,
                "capacity": c.capacity,
                "reliability_score": c.reliability_score,
            }
            for c in self.store.carriers.values()
            if c.status == "ACTIVE"
        ]

        return {
            "query": query,
            "target_shipments": target_shipments,
            "target_disruptions": target_disruptions,
            "active_disruptions": active_disruptions[:4],
            "available_routes": available_routes,
            "active_carriers": active_carriers,
            "unknown_entities": unknown_entities,
            "sources": sorted(list(sources)),
            "extra_context": extra_context or {},
        }

    def format_context_prompt(self, context: Dict[str, Any]) -> str:
        """Format the structured context into a concise textual summary for prompts."""
        sections = []

        if context.get("unknown_entities"):
            sections.append(
                "UNREGISTERED ENTITIES (Not found in RouteX database):\n"
                + ", ".join(context["unknown_entities"])
            )

        if context.get("target_shipments"):
            lines = ["TARGET SHIPMENT DETAILS:"]
            for s in context["target_shipments"]:
                lines.append(
                    f"- {s['shipment_id']}: Origin={s['origin']} -> Dest={s['destination']}, "
                    f"Route={s['route_id']} (via {s['route_via']}), Carrier={s['carrier_id']} ({s['carrier_name']}, Rel={s['carrier_reliability']}), "
                    f"Cargo={s['cargo_type']} (${s['cargo_value']:,.0f}), Priority={s['priority']}, Status={s['status']}"
                )
            sections.append("\n".join(lines))

        if context.get("target_disruptions"):
            lines = ["TARGET DISRUPTION DETAILS:"]
            for d in context["target_disruptions"]:
                lines.append(
                    f"- {d['disruption_id']} ({d['location']}): Type={d['type']}, Severity={d['severity']}, "
                    f"Duration={d['duration_days']} days, Status={d['status']}. Details: {d['description']}"
                )
            sections.append("\n".join(lines))

        if context.get("active_disruptions"):
            lines = ["ACTIVE NETWORK DISRUPTIONS:"]
            for d in context["active_disruptions"]:
                lines.append(
                    f"- {d['disruption_id']} at {d['location']}: {d['severity']} severity, {d['duration_days']}d duration"
                )
            sections.append("\n".join(lines))

        if context.get("extra_context"):
            sections.append(f"SCENARIO CONTEXT:\n{context['extra_context']}")

        return "\n\n".join(sections)
