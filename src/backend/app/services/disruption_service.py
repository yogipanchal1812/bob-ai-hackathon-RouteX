"""
RouteX Backend — Disruption Service.

Lookup operations for disruptions. Raises ResourceNotFoundError for unknown IDs.
"""

from typing import List, Optional

from app.models.disruption import Disruption
from app.services.data_loader import get_data_store
from app.utils.errors import ResourceNotFoundError


def get_all_disruptions(status: Optional[str] = None) -> List[Disruption]:
    """Return all disruptions, optionally filtered by status."""
    store = get_data_store()
    disruptions = list(store.disruptions.values())
    if status:
        status_upper = status.strip().upper()
        disruptions = [d for d in disruptions if d.status == status_upper]
    return disruptions


def get_disruption_by_id(disruption_id: str) -> Disruption:
    """Return a single disruption or raise 404."""
    store = get_data_store()
    disruption = store.disruptions.get(disruption_id)
    if not disruption:
        raise ResourceNotFoundError("Disruption", disruption_id)
    return disruption
