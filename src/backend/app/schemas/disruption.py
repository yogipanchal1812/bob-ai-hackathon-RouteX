"""RouteX Backend — Disruption response schemas."""

from typing import List
from pydantic import BaseModel


class DisruptionResponse(BaseModel):
    """Single disruption detail."""

    disruption_id: str
    location: str
    type: str
    severity: str
    duration_days: int
    description: str
    status: str


class DisruptionListResponse(BaseModel):
    """Response for the disruptions list endpoint."""

    success: bool
    count: int
    data: List[DisruptionResponse]
