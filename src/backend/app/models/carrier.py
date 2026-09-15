"""RouteX Backend — Carrier data model."""

from dataclasses import dataclass


@dataclass
class Carrier:
    """Represents a logistics carrier / shipping line."""

    carrier_id: str
    name: str
    capacity: int           # TEU or equivalent units
    reliability_score: float  # 0.0–1.0
    status: str             # ACTIVE | SUSPENDED
