"""
RouteX AI Module — Recommendation Schemas.

Structured schema for supply-chain operational recommendations.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class RecommendationAction(str, Enum):
    REROUTE = "REROUTE"
    CARRIER_EXPEDITE = "CARRIER_EXPEDITE"
    BUFFER_HOLD = "BUFFER_HOLD"
    MONITOR = "MONITOR"
    SPLIT_SHIPMENT = "SPLIT_SHIPMENT"


class RecommendationPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Recommendation(BaseModel):
    """A structured, actionable supply-chain recommendation."""

    action: str = Field(..., description="Action type (REROUTE, CARRIER_EXPEDITE, BUFFER_HOLD, etc.)")
    priority: str = Field(..., description="Priority: CRITICAL, HIGH, MEDIUM, LOW")
    shipment_id: Optional[str] = Field(None, description="Impacted shipment ID (string)")
    recommended_route: Optional[str] = Field(None, description="Suggested bypass route ID (string)")
    carrier_id: Optional[str] = Field(None, description="Recommended alternative carrier ID (string)")
    reason: str = Field(..., description="Explainable rationale grounded in RouteX context")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Calculated confidence score between 0.0 and 1.0")


class RecommendationRequest(BaseModel):
    """Request for targeted recommendation generation."""

    shipment_id: Optional[str] = None
    disruption_id: Optional[str] = None
    max_recommendations: int = Field(default=5, ge=1, le=20)


class RecommendationResponse(BaseModel):
    """Response containing structured recommendations."""

    success: bool = True
    count: int
    data: List[Recommendation]
