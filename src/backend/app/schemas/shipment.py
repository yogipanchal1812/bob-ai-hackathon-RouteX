"""RouteX Backend — Shipment response schemas."""

from typing import List
from pydantic import BaseModel


class ShipmentResponse(BaseModel):
    """Single shipment detail."""

    shipment_id: str
    origin: str
    destination: str
    route_id: str
    carrier_id: str
    cargo_type: str
    cargo_value: float
    priority: str
    eta: str
    status: str


class ShipmentListResponse(BaseModel):
    """Response for the shipments list endpoint."""

    success: bool
    count: int
    data: List[ShipmentResponse]
