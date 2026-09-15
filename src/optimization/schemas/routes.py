"""
routes.py — Pydantic v2 schemas for route data.

Routes are used for alternative-route ranking.
Do NOT invent roads — only routes present in seed_data are returned.
"""

from pydantic import BaseModel, Field


class Route(BaseModel):
    """A supply chain route between two hubs."""

    route_id: str = Field(..., description="Unique route identifier (string)")
    origin: str
    destination: str
    distance_km: float = Field(..., gt=0)
    duration_hours: float = Field(..., gt=0)
    cost_usd: float = Field(..., ge=0, description="Estimated transport cost in USD (numeric)")
    disruption_exposure: float = Field(
        ..., ge=0.0, le=1.0, description="0.0 = no exposure, 1.0 = fully disrupted"
    )
    carrier_id: str = Field(..., description="Default carrier for this route")
    tags: list[str] = Field(default_factory=list, description="e.g. ['highway', 'coastal']")


class AlternativeRouteResult(BaseModel):
    """
    A ranked alternative route recommendation.

    rank         → 1 = best alternative
    reason       → list of factors that made this the preferred route
    savings_usd  → estimated savings vs. disrupted primary route (may be 0)
    """

    rank: int = Field(..., ge=1)
    route: Route
    reason: list[str] = Field(default_factory=list)
    savings_usd: float = Field(..., ge=0.0)
    time_delta_hours: float = Field(
        ..., description="Positive = slower than primary, Negative = faster"
    )
