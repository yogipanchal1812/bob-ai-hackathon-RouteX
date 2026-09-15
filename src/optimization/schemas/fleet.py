"""
fleet.py — Pydantic v2 schemas for fleet data.

Shared API contract field names (Rule 12):
  vehicle_id, carrier_id  → strings
  status                  → one of VehicleStatus enum values
  Dates                   → ISO 8601 (YYYY-MM-DD or YYYY-MM-DDTHH:mm:ssZ)
  Monetary values         → numeric (formatting belongs to frontend)
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class VehicleStatus(str, Enum):
    """Allowed vehicle statuses per shared engineering rules."""

    AVAILABLE = "AVAILABLE"
    IN_TRANSIT = "IN_TRANSIT"
    IDLE = "IDLE"
    MAINTENANCE = "MAINTENANCE"


class VehicleType(str, Enum):
    TRUCK = "TRUCK"
    VAN = "VAN"
    CONTAINER = "CONTAINER"
    FLATBED = "FLATBED"
    REFRIGERATED = "REFRIGERATED"


class Vehicle(BaseModel):
    """A single fleet asset."""

    vehicle_id: str = Field(..., description="Unique vehicle identifier (string)")
    type: VehicleType
    location: str = Field(..., description="Current location / hub name")
    capacity_tons: float = Field(..., gt=0, description="Maximum payload in metric tons")
    status: VehicleStatus
    available: bool = Field(..., description="Whether the vehicle can be assigned now")
    carrier_id: str = Field(..., description="Owning carrier identifier (string)")

    model_config = {"use_enum_values": True}


class FleetUtilizationReport(BaseModel):
    """
    Fleet utilization summary.

    Utilization formula:
        utilization_pct = (in_transit / total) * 100   [if total > 0 else 0.0]

    'idle' vehicles are flagged separately — they are on-site but unused,
    representing an optimisation opportunity.
    """

    total_vehicles: int = Field(..., ge=0)
    available_vehicles: int = Field(..., ge=0)
    idle_vehicles: int = Field(..., ge=0)
    in_transit_vehicles: int = Field(..., ge=0)
    maintenance_vehicles: int = Field(..., ge=0)
    utilization_pct: float = Field(
        ..., ge=0.0, le=100.0, description="% of fleet actively in transit"
    )


class FleetMatchResult(BaseModel):
    """
    Vehicle-to-shipment match recommendation.

    match_score: 0–100 (higher = better fit).
    reason: human-readable list explaining the score components.
    """

    vehicle_id: str
    shipment_id: str
    match_score: int = Field(..., ge=0, le=100)
    reason: list[str] = Field(default_factory=list)


class OptimizeFleetRequest(BaseModel):
    """Request body for POST /api/optimize-fleet."""

    shipment_ids: Optional[list[str]] = Field(
        default=None,
        description="Specific shipment IDs to optimize. If omitted, all affected shipments are used.",
    )
    disruption_id: Optional[str] = Field(
        default=None,
        description="Disruption context (for future Member 1 integration).",
    )

    @field_validator("shipment_ids")
    @classmethod
    def shipment_ids_not_empty_list(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        """An explicitly passed empty list is treated as None (use all)."""
        if v is not None and len(v) == 0:
            return None
        return v


class OptimizeFleetResponse(BaseModel):
    """Response for POST /api/optimize-fleet."""

    matches: list[FleetMatchResult] = Field(default_factory=list)
    total_matches: int = Field(..., ge=0)
    unmatched_shipment_ids: list[str] = Field(default_factory=list)
