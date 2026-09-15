"""RouteX Backend — Impact & Risk analysis schemas."""

from typing import List
from pydantic import BaseModel, Field


# ── Risk factors ──────────────────────────────────────────────────────────────


class RiskFactor(BaseModel):
    """A single explainable factor contributing to the risk score."""

    factor: str
    score: float
    weight: float
    impact: str  # LOW | MEDIUM | HIGH


# ── Disruption analysis ──────────────────────────────────────────────────────


class AffectedShipment(BaseModel):
    """A shipment impacted by a specific disruption."""

    shipment_id: str
    origin: str
    destination: str
    cargo_type: str
    cargo_value: float
    priority: str
    risk_score: int
    risk_level: str
    estimated_delay_days: float
    estimated_impact: float
    factors: List[RiskFactor]


class ImpactSummary(BaseModel):
    """Aggregated impact counts for a disruption analysis."""

    total_affected: int
    low_risk: int
    medium_risk: int
    high_risk: int
    critical_risk: int
    estimated_impact: float
    estimated_delay_days: float


class DisruptionAnalysisRequest(BaseModel):
    """Request body for POST /api/analyze-disruption."""

    disruption_id: str = Field(
        ..., min_length=1, description="ID of the disruption to analyze"
    )


class DisruptionAnalysisResponse(BaseModel):
    """Full response from the disruption analysis endpoint."""

    disruption_id: str
    disruption_type: str
    disruption_severity: str
    disruption_location: str
    affected_shipments: List[AffectedShipment]
    summary: ImpactSummary


# ── Global impact summary ────────────────────────────────────────────────────


class DisruptionSummaryItem(BaseModel):
    """One disruption's headline numbers in the global summary."""

    disruption_id: str
    location: str
    type: str
    severity: str
    total_affected: int
    estimated_impact: float
    estimated_delay_days: float


class RiskDistribution(BaseModel):
    """Counts of affected shipments by risk level."""

    low_risk: int
    medium_risk: int
    high_risk: int
    critical_risk: int


class GlobalImpactSummary(BaseModel):
    """Response from GET /api/impact-summary."""

    total_active_disruptions: int
    total_affected_shipments: int
    total_estimated_impact: float
    risk_distribution: RiskDistribution
    disruptions: List[DisruptionSummaryItem]
