"""
RouteX Backend — Shipment Service.

Lookup operations for shipments. Raises ResourceNotFoundError for unknown IDs.
"""

from typing import List, Optional

from app.models.shipment import Shipment
from app.services.data_loader import get_data_store
from app.utils.errors import ResourceNotFoundError


def get_all_shipments(status: Optional[str] = None) -> List[Shipment]:
    """Return all shipments, optionally filtered by status."""
    store = get_data_store()
    shipments = list(store.shipments.values())
    if status:
        status_upper = status.strip().upper()
        shipments = [s for s in shipments if s.status == status_upper]
    return shipments


def get_shipment_by_id(shipment_id: str) -> Shipment:
    """Return a single shipment or raise 404."""
    store = get_data_store()
    shipment = store.shipments.get(shipment_id)
    if not shipment:
        raise ResourceNotFoundError("Shipment", shipment_id)
    return shipment
