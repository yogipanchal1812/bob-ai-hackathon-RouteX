"""
RouteX Backend — Input Validation Helpers.

Used by the data loader and service layer to enforce data integrity
before values enter the system.
"""

# ── Valid value sets ──────────────────────────────────────────────────────────

VALID_SEVERITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
VALID_DISRUPTION_TYPES = {
    "WEATHER",
    "PORT_CONGESTION",
    "GEOPOLITICAL",
    "INFRASTRUCTURE",
    "LABOR_STRIKE",
}
VALID_SHIPMENT_STATUSES = {"IN_TRANSIT", "DELIVERED", "DELAYED", "CANCELLED"}
VALID_DISRUPTION_STATUSES = {"ACTIVE", "RESOLVED", "MONITORING"}
VALID_ROUTE_STATUSES = {"ACTIVE", "DISRUPTED", "SUSPENDED"}
VALID_PRIORITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}


# ── Validation functions ─────────────────────────────────────────────────────


def validate_severity(severity: str) -> bool:
    """Return True if severity is a recognized value."""
    return severity.upper() in VALID_SEVERITIES


def validate_disruption_type(dtype: str) -> bool:
    """Return True if disruption type is a recognized value."""
    return dtype.upper() in VALID_DISRUPTION_TYPES


def validate_positive_number(value: float, field_name: str) -> float:
    """Ensure a numeric value is non-negative. Returns the value or raises."""
    if value < 0:
        raise ValueError(f"{field_name} cannot be negative: {value}")
    return value


def validate_duration(days: int) -> int:
    """Ensure duration is non-negative. Returns the value or raises."""
    if days < 0:
        raise ValueError(f"Duration cannot be negative: {days}")
    return days


def validate_status(status: str, valid_values: set, entity: str) -> str:
    """Validate status against a set of allowed values. Returns uppercased."""
    upper = status.upper()
    if upper not in valid_values:
        raise ValueError(
            f"Invalid {entity} status: '{status}'. "
            f"Must be one of: {', '.join(sorted(valid_values))}"
        )
    return upper
