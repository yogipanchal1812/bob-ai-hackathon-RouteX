"""RouteX Backend — Shipment data model."""

from dataclasses import dataclass


@dataclass
class Shipment:
    """Represents a cargo shipment in transit."""

    shipment_id: str
    origin: str
    destination: str
    route_id: str
    carrier_id: str
    cargo_type: str
    cargo_value: float
    priority: str       # LOW | MEDIUM | HIGH | CRITICAL
    eta: str            # ISO 8601 date
    status: str         # IN_TRANSIT | DELIVERED | DELAYED | CANCELLED
