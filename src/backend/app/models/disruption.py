"""RouteX Backend — Disruption data model."""

from dataclasses import dataclass


@dataclass
class Disruption:
    """Represents a supply-chain disruption event."""

    disruption_id: str
    location: str
    type: str           # WEATHER | PORT_CONGESTION | GEOPOLITICAL | INFRASTRUCTURE | LABOR_STRIKE
    severity: str       # LOW | MEDIUM | HIGH | CRITICAL
    duration_days: int
    description: str
    status: str         # ACTIVE | RESOLVED | MONITORING
