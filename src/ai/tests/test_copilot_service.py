"""
Tests for AI Copilot Service & 7 Core Query Categories.

Verifies:
1. Which shipments are most affected?
2. Why is SH001 high risk?
3. What should we do about the Mumbai / Suez disruption?
4. Which shipments should be prioritized?
5. What happens if disruption lasts 5 days (What-if)?
6. Which fleet assets can help?
7. Which alternative route should we consider?
- Anti-hallucination for unregistered entity IDs
- Fact / Inference / Recommendation delineation
"""


def test_copilot_q1_most_affected_shipments(copilot_service):
    """Category 1: Most affected shipments."""
    resp = copilot_service.answer_question("Which shipments are most affected right now?")
    assert resp.success is True
    assert "[FACT]" in resp.answer
    assert "[INFERENCE]" in resp.answer
    assert "[RECOMMENDATION]" in resp.answer
    assert len(resp.recommendations) > 0


def test_copilot_q2_why_shipment_high_risk(copilot_service):
    """Category 2: Why is SH001 high risk?"""
    resp = copilot_service.answer_question("Why is SH001 high risk?")
    assert resp.success is True
    assert "SH001" in resp.answer
    assert "shipment:SH001" in resp.sources
    assert len(resp.recommendations) >= 1
    assert resp.recommendations[0].shipment_id == "SH001"


def test_copilot_q3_disruption_action(copilot_service):
    """Category 3: What should we do about the Suez Canal disruption?"""
    resp = copilot_service.answer_question("What should we do about the Suez Canal disruption?")
    assert resp.success is True
    assert "Suez Canal" in resp.answer
    assert "disruption:D001" in resp.sources


def test_copilot_q4_prioritize_shipments(copilot_service):
    """Category 4: Which shipments should be prioritized?"""
    resp = copilot_service.answer_question("Which shipments should be prioritized first?")
    assert resp.success is True
    assert "SH003" in resp.answer or "Priority" in resp.answer
    assert len(resp.recommendations) > 0


def test_copilot_q5_what_if_extension(copilot_service):
    """Category 5: What happens if the disruption lasts 5 days?"""
    resp = copilot_service.answer_question("What happens if the disruption lasts 5 more days?")
    assert resp.success is True
    assert "+5" in resp.answer or "5 days" in resp.answer
    assert "[INFERENCE]" in resp.answer
    assert "delay" in resp.answer.lower()


def test_copilot_q6_fleet_assets(copilot_service):
    """Category 6: Which fleet assets can help?"""
    resp = copilot_service.answer_question("Which fleet assets or carriers can help?")
    assert resp.success is True
    assert "C001" in resp.answer or "GlobalShip" in resp.answer


def test_copilot_q7_alternative_routes(copilot_service):
    """Category 7: Which alternative route should we consider?"""
    resp = copilot_service.answer_question("Which alternative route should we consider for rerouting?")
    assert resp.success is True
    assert "R002" in resp.answer or "R004" in resp.answer or "route" in resp.answer.lower()


def test_anti_hallucination_unknown_shipment(copilot_service):
    """Anti-hallucination: Rejects unknown shipment ID and refuses to invent facts."""
    resp = copilot_service.answer_question("Why is SH999 delayed?")
    assert resp.success is True
    assert "not found in the active RouteX registry" in resp.answer
    assert "SH999" in resp.answer
    assert resp.sources == []
    assert len(resp.recommendations) == 0


def test_copilot_api_endpoint(client):
    """REST POST /api/copilot works with both 'question' and 'message' fields."""
    # Test with 'question' (official spec)
    r1 = client.post("/api/copilot", json={"question": "Why is SH001 high risk?"})
    assert r1.status_code == 200
    data1 = r1.json()
    assert data1["success"] is True
    assert "answer" in data1
    assert "data" in data1
    assert data1["data"]["response"] == data1["answer"]

    # Test with 'message' (frontend UI)
    r2 = client.post("/api/copilot", json={"message": "Which shipments are most affected?"})
    assert r2.status_code == 200
    data2 = r2.json()
    assert data2["success"] is True


def test_copilot_api_empty_query_rejected(client):
    """Empty queries are rejected with 422 Unprocessable Entity."""
    resp = client.post("/api/copilot", json={"question": "   "})
    assert resp.status_code == 422


def test_recommendation_api_endpoint(client):
    """REST POST /api/recommendation returns structured actions."""
    resp = client.post("/api/recommendation", json={"shipment_id": "SH001"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["count"] >= 1
    assert data["data"][0]["shipment_id"] == "SH001"
