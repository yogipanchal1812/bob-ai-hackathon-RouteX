"""Tests for the deterministic risk engine.

Covers:
    • risk-level boundary conditions (the spec's exact thresholds)
    • determinism (same input → same output)
    • score range invariant (0–100)
    • explainable factors structure
    • route exposure matching
"""

from app.models.common import RiskLevel, risk_level_from_score
from app.models.disruption import Disruption
from app.models.route import Route
from app.services.risk_service import calculate_risk, is_route_exposed


# ══════════════════════════════════════════════════════════════════════════════
# Risk-level boundary tests  (spec-mandated)
# ══════════════════════════════════════════════════════════════════════════════


def test_risk_level_0_is_low():
    assert risk_level_from_score(0) == RiskLevel.LOW


def test_risk_level_39_is_low():
    assert risk_level_from_score(39) == RiskLevel.LOW


def test_risk_level_40_is_medium():
    assert risk_level_from_score(40) == RiskLevel.MEDIUM


def test_risk_level_69_is_medium():
    assert risk_level_from_score(69) == RiskLevel.MEDIUM


def test_risk_level_70_is_high():
    assert risk_level_from_score(70) == RiskLevel.HIGH


def test_risk_level_89_is_high():
    assert risk_level_from_score(89) == RiskLevel.HIGH


def test_risk_level_90_is_critical():
    assert risk_level_from_score(90) == RiskLevel.CRITICAL


def test_risk_level_100_is_critical():
    assert risk_level_from_score(100) == RiskLevel.CRITICAL


# ══════════════════════════════════════════════════════════════════════════════
# Determinism
# ══════════════════════════════════════════════════════════════════════════════


def test_risk_calculation_deterministic():
    """Same input must always produce the identical output."""
    from app.services.data_loader import get_data_store

    store = get_data_store()
    shipment = store.shipments.get("SH001")
    disruption = store.disruptions.get("D001")
    if not shipment or not disruption:
        return

    result1 = calculate_risk(shipment, disruption)
    result2 = calculate_risk(shipment, disruption)
    assert result1["risk_score"] == result2["risk_score"]
    assert result1["risk_level"] == result2["risk_level"]
    assert result1["factors"] == result2["factors"]


# ══════════════════════════════════════════════════════════════════════════════
# Score range invariant
# ══════════════════════════════════════════════════════════════════════════════


def test_risk_score_within_bounds():
    """risk_score must be in [0, 100] for every shipment × disruption pair."""
    from app.services.data_loader import get_data_store

    store = get_data_store()
    for shipment in store.shipments.values():
        for disruption in store.disruptions.values():
            result = calculate_risk(shipment, disruption)
            assert 0 <= result["risk_score"] <= 100, (
                f"Out-of-range score {result['risk_score']} for "
                f"{shipment.shipment_id} × {disruption.disruption_id}"
            )
            assert result["risk_level"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")


# ══════════════════════════════════════════════════════════════════════════════
# Explainable factors
# ══════════════════════════════════════════════════════════════════════════════


def test_risk_factors_present_and_complete():
    """Risk result must include 6 named, weighted factors."""
    from app.services.data_loader import get_data_store

    store = get_data_store()
    shipment = list(store.shipments.values())[0]
    disruption = list(store.disruptions.values())[0]
    result = calculate_risk(shipment, disruption)

    assert "factors" in result
    assert len(result["factors"]) == 6
    for f in result["factors"]:
        assert "factor" in f
        assert "score" in f
        assert "weight" in f
        assert "impact" in f
        assert f["impact"] in ("LOW", "MEDIUM", "HIGH")


# ══════════════════════════════════════════════════════════════════════════════
# Route exposure
# ══════════════════════════════════════════════════════════════════════════════


def test_route_exposure_match():
    """A route whose via field contains the disruption location is exposed."""
    route = Route(
        "R001", "Shanghai", "Rotterdam",
        "Strait of Malacca; Suez Canal", 19500, 28, 42000, "ACTIVE",
    )
    disruption = Disruption(
        "D001", "Suez Canal", "PORT_CONGESTION",
        "CRITICAL", 14, "Test", "ACTIVE",
    )
    assert is_route_exposed(route, disruption) is True


def test_route_exposure_no_match():
    """A route that does not pass through the disruption is not exposed."""
    route = Route(
        "R005", "Tokyo", "Seattle",
        "North Pacific Ocean", 7700, 12, 22000, "ACTIVE",
    )
    disruption = Disruption(
        "D001", "Suez Canal", "PORT_CONGESTION",
        "CRITICAL", 14, "Test", "ACTIVE",
    )
    assert is_route_exposed(route, disruption) is False


def test_route_exposure_origin_match():
    """Disruption at a route's origin city counts as exposed."""
    route = Route(
        "R001", "Shanghai", "Rotterdam",
        "Strait of Malacca; Suez Canal", 19500, 28, 42000, "ACTIVE",
    )
    disruption = Disruption(
        "D006", "Shanghai", "PORT_CONGESTION",
        "MEDIUM", 5, "Test", "MONITORING",
    )
    assert is_route_exposed(route, disruption) is True


def test_route_exposure_case_insensitive():
    """Route exposure matching is case-insensitive."""
    route = Route(
        "R001", "Shanghai", "Rotterdam",
        "Strait of Malacca; Suez Canal", 19500, 28, 42000, "ACTIVE",
    )
    disruption = Disruption(
        "D001", "suez canal", "PORT_CONGESTION",
        "CRITICAL", 14, "Test", "ACTIVE",
    )
    assert is_route_exposed(route, disruption) is True
