"""
RouteX Backend — Shared Enums & Constants.

Central definitions for risk levels, statuses, and the canonical
risk-score-to-level mapping used by every module.
"""

from enum import Enum


# ── Risk ──────────────────────────────────────────────────────────────────────

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


def risk_level_from_score(score: int) -> RiskLevel:
    """
    Map a numeric risk score (0–100) to a RiskLevel.

    Boundaries (inclusive):
        0–39   → LOW
        40–69  → MEDIUM
        70–89  → HIGH
        90–100 → CRITICAL
    """
    if score <= 39:
        return RiskLevel.LOW
    elif score <= 69:
        return RiskLevel.MEDIUM
    elif score <= 89:
        return RiskLevel.HIGH
    else:
        return RiskLevel.CRITICAL


# ── Shipment ──────────────────────────────────────────────────────────────────

class ShipmentStatus(str, Enum):
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    DELAYED = "DELAYED"
    CANCELLED = "CANCELLED"


class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ── Disruption ────────────────────────────────────────────────────────────────

class DisruptionType(str, Enum):
    WEATHER = "WEATHER"
    PORT_CONGESTION = "PORT_CONGESTION"
    GEOPOLITICAL = "GEOPOLITICAL"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    LABOR_STRIKE = "LABOR_STRIKE"


class DisruptionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    RESOLVED = "RESOLVED"
    MONITORING = "MONITORING"


# ── Route ─────────────────────────────────────────────────────────────────────

class RouteStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DISRUPTED = "DISRUPTED"
    SUSPENDED = "SUSPENDED"


# ── Carrier ───────────────────────────────────────────────────────────────────

class CarrierStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
