"""
simulation.py — Pydantic v2 schemas for what-if scenario simulation.

Shared API contract (from spec):
    disruption_id → string
    duration_days → int ≥ 0
    estimated_impact → numeric (monetary, currency formatting on frontend)
    Risk levels: LOW | MEDIUM | HIGH | CRITICAL
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class ActionType(str):
    REROUTE_SHIPMENT = "REROUTE_SHIPMENT"
    ASSIGN_VEHICLE = "ASSIGN_VEHICLE"
    CHANGE_CARRIER = "CHANGE_CARRIER"
    PRIORITIZE_SHIPMENT = "PRIORITIZE_SHIPMENT"
    MONITOR_ROUTE = "MONITOR_ROUTE"


class ActionPriority(str):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RecommendedAction(BaseModel):
    """
    A structured operational recommendation.

    action   → one of the ActionType constants
    priority → HIGH | MEDIUM | LOW
    target   → the entity (shipment_id, route_id, vehicle_id, etc.)
    reason   → human-readable explanation
    """

    action: str = Field(..., description="Action type e.g. REROUTE_SHIPMENT")
    priority: str = Field(..., description="HIGH | MEDIUM | LOW")
    target: str = Field(..., description="Entity ID this action targets")
    reason: str = Field(..., description="Explanation of why this action is recommended")


class WhatIfRequest(BaseModel):
    """
    Request body for POST /api/what-if.

    duration_days must be ≥ 0.
    Negative values are rejected with HTTP 422.
    """

    disruption_id: str = Field(..., description="ID of the disruption to simulate")
    duration_days: int = Field(..., ge=0, description="Simulated disruption duration in days (≥ 0)")

    @field_validator("duration_days")
    @classmethod
    def duration_must_be_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("duration_days must be 0 or greater")
        return v


class ScenarioSnapshot(BaseModel):
    """
    A point-in-time view of the supply chain under a given disruption scenario.

    affected_shipments → count of shipments impacted
    high_risk          → count with risk level HIGH or CRITICAL
    estimated_impact   → total estimated financial impact (numeric USD)
    """

    affected_shipments: int = Field(..., ge=0)
    high_risk: int = Field(..., ge=0)
    estimated_impact: float = Field(..., ge=0.0, description="Estimated USD impact (numeric)")


class WhatIfDelta(BaseModel):
    """
    Difference between scenario and baseline.
    All delta values are ≥ 0 (impact can only worsen or stay same in a disruption).
    """

    affected_shipments: int = Field(..., ge=0)
    high_risk: int = Field(..., ge=0)
    estimated_impact: float = Field(..., ge=0.0)


class WhatIfResponse(BaseModel):
    """
    Full what-if API response.

    Stable contract — do NOT change field names without coordinating with Members 2 & 3.
    """

    baseline: ScenarioSnapshot
    scenario: ScenarioSnapshot
    delta: WhatIfDelta
    recommended_actions: list[RecommendedAction] = Field(default_factory=list)
