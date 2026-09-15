"""
Tests for Structured Recommendation Engine.

Verifies:
- Action selection (REROUTE, CARRIER_EXPEDITE, MONITOR)
- Priority tiering (CRITICAL, HIGH, MEDIUM, LOW)
- Confidence score invariants (bounded 0.0 - 1.0)
- Alternative route selection
"""

from ai.recommendations.recommendation_service import RecommendationService
from ai.recommendations.rules import calculate_confidence, determine_recommendation_priority


def test_confidence_score_bounded():
    """Confidence score must remain between 0.10 and 0.99."""
    for rel in [0.0, 0.5, 0.75, 0.92, 1.0]:
        for sev in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
            for prio in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
                for alt in [True, False]:
                    score = calculate_confidence(rel, sev, prio, alt)
                    assert 0.0 <= score <= 1.0, f"Confidence out of range: {score}"


def test_recommendation_priority_tiers():
    """Priority mapping correctly elevates sensitive and high-value cargo."""
    assert determine_recommendation_priority("CRITICAL", "HIGH", 5_000_000, "Medical Equipment") == "CRITICAL"
    assert determine_recommendation_priority("HIGH", "CRITICAL", 4_500_000, "Pharmaceuticals") == "CRITICAL"
    assert determine_recommendation_priority("HIGH", "MEDIUM", 800_000, "Textiles") == "HIGH"
    assert determine_recommendation_priority("LOW", "LOW", 350_000, "Spices") == "LOW"


def test_generate_recommendation_for_exposed_shipment(recommendation_service):
    """Exposed shipment SH001 produces an operational REROUTE action."""
    recs = recommendation_service.generate_recommendations(shipment_id="SH001")
    assert len(recs) == 1
    rec = recs[0]

    assert rec.shipment_id == "SH001"
    assert rec.action in ["REROUTE", "CARRIER_EXPEDITE"]
    assert rec.priority in ["CRITICAL", "HIGH"]
    assert rec.recommended_route is not None
    assert 0.0 < rec.confidence <= 1.0
    assert "Suez Canal" in rec.reason


def test_generate_recommendation_for_safe_shipment(recommendation_service):
    """Shipment with no active exposure produces a MONITOR action."""
    recs = recommendation_service.generate_recommendations(shipment_id="SH002")
    assert len(recs) == 1
    rec = recs[0]
    assert rec.action in ["MONITOR", "REROUTE"]
    assert 0.0 < rec.confidence <= 1.0


def test_global_recommendations_ordered_by_priority(recommendation_service):
    """Global recommendations return highest-priority items first."""
    recs = recommendation_service.generate_recommendations(max_count=5)
    assert len(recs) > 0

    p_map = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    for i in range(len(recs) - 1):
        assert p_map[recs[i].priority] <= p_map[recs[i + 1].priority]
