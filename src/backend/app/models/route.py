"""RouteX Backend — Route data model."""

from dataclasses import dataclass


@dataclass
class Route:
    """Represents a shipping route between two locations."""

    route_id: str
    origin: str
    destination: str
    via: str              # Semicolon-separated waypoints / channels
    distance_km: float
    estimated_days: int
    estimated_cost: float   # Pure numeric — formatting is frontend's job
    status: str           # ACTIVE | DISRUPTED | SUSPENDED
