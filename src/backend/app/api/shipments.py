"""RouteX Backend — Shipment API endpoints."""

from typing import Optional

from fastapi import APIRouter, Query

from app.schemas.shipment import ShipmentListResponse, ShipmentResponse
from app.services import shipment_service

router = APIRouter(prefix="/api", tags=["Shipments"])


@router.get("/shipments", response_model=ShipmentListResponse)
def list_shipments(
    status: Optional[str] = Query(
        None, description="Filter by status (IN_TRANSIT, DELIVERED, DELAYED, CANCELLED)"
    ),
):
    """Return all shipments, optionally filtered by status."""
    shipments = shipment_service.get_all_shipments(status=status)
    return ShipmentListResponse(
        success=True,
        count=len(shipments),
        data=[ShipmentResponse(**s.__dict__) for s in shipments],
    )


@router.get("/shipments/{shipment_id}")
def get_shipment(shipment_id: str):
    """Return a single shipment by ID."""
    shipment = shipment_service.get_shipment_by_id(shipment_id)
    return {
        "success": True,
        "data": ShipmentResponse(**shipment.__dict__).model_dump(),
    }
