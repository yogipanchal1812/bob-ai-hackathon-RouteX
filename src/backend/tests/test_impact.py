"""Tests for impact analysis, global summary, health, and routes endpoints.

Covers:
    • valid disruption analysis (structure + counts)
    • missing disruption → 404
    • malformed / empty request body → 422
    • financial values are numeric
    • risk-count consistency
    • global impact summary
    • health endpoint
    • routes endpoint
"""


# ══════════════════════════════════════════════════════════════════════════════
# POST /api/analyze-disruption
# ══════════════════════════════════════════════════════════════════════════════


def test_analyze_disruption_valid(client):
    """Valid disruption ID returns stable response structure."""
    response = client.post("/api/analyze-disruption", json={"disruption_id": "D001"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    result = data["data"]
    assert result["disruption_id"] == "D001"
    assert isinstance(result["affected_shipments"], list)

    summary = result["summary"]
    for key in (
        "total_affected", "low_risk", "medium_risk",
        "high_risk", "critical_risk", "estimated_impact",
        "estimated_delay_days",
    ):
        assert key in summary, f"Missing summary field: {key}"


def test_analyze_disruption_risk_counts_add_up(client):
    """low + medium + high + critical must equal total_affected."""
    response = client.post("/api/analyze-disruption", json={"disruption_id": "D001"})
    data = response.json()
    summary = data["data"]["summary"]
    assert (
        summary["low_risk"]
        + summary["medium_risk"]
        + summary["high_risk"]
        + summary["critical_risk"]
        == summary["total_affected"]
    )


def test_analyze_disruption_not_found(client):
    """Nonexistent disruption_id returns 404."""
    response = client.post(
        "/api/analyze-disruption", json={"disruption_id": "NONEXISTENT"}
    )
    assert response.status_code == 404


def test_analyze_disruption_empty_body(client):
    """Empty JSON body returns 422 (validation error)."""
    response = client.post("/api/analyze-disruption", json={})
    assert response.status_code == 422


def test_analyze_disruption_malformed_json(client):
    """Non-JSON body returns 422."""
    response = client.post(
        "/api/analyze-disruption",
        content="not-json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422


def test_analyze_disruption_financial_values_numeric(client):
    """All financial / numeric fields must be numbers, not strings."""
    response = client.post("/api/analyze-disruption", json={"disruption_id": "D001"})
    data = response.json()
    summary = data["data"]["summary"]
    assert isinstance(summary["estimated_impact"], (int, float))
    assert isinstance(summary["estimated_delay_days"], (int, float))


def test_affected_shipments_required_fields(client):
    """Each affected shipment entry has all required fields with correct types."""
    response = client.post("/api/analyze-disruption", json={"disruption_id": "D001"})
    data = response.json()
    for s in data["data"]["affected_shipments"]:
        assert isinstance(s["shipment_id"], str)
        assert isinstance(s["risk_score"], int)
        assert s["risk_level"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
        assert isinstance(s["estimated_delay_days"], (int, float))
        assert isinstance(s["estimated_impact"], (int, float))
        assert isinstance(s["factors"], list)


def test_analyze_disruption_no_affected_shipments(client):
    """
    D004 targets North Pacific — only R005 (Tokyo→Seattle) is exposed.
    Regardless of count, verify the response structure is valid even
    with few or zero affected shipments.
    """
    response = client.post("/api/analyze-disruption", json={"disruption_id": "D008"})
    assert response.status_code == 200
    data = response.json()
    result = data["data"]
    assert isinstance(result["affected_shipments"], list)
    summary = result["summary"]
    assert summary["total_affected"] >= 0
    assert isinstance(summary["estimated_impact"], (int, float))


# ══════════════════════════════════════════════════════════════════════════════
# GET /api/impact-summary
# ══════════════════════════════════════════════════════════════════════════════


def test_impact_summary(client):
    """Global impact summary has the right structure."""
    response = client.get("/api/impact-summary")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    result = data["data"]
    assert "total_active_disruptions" in result
    assert "total_affected_shipments" in result
    assert "total_estimated_impact" in result
    assert "risk_distribution" in result
    assert "disruptions" in result
    assert isinstance(result["disruptions"], list)
    assert isinstance(result["total_estimated_impact"], (int, float))


# ══════════════════════════════════════════════════════════════════════════════
# GET /api/health
# ══════════════════════════════════════════════════════════════════════════════


def test_health_endpoint(client):
    """Health check returns healthy status and module name."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["module"] == "routex-backend"
    assert "data_loaded" in data
    assert data["data_loaded"]["shipments"] > 0


# ══════════════════════════════════════════════════════════════════════════════
# GET /api/routes
# ══════════════════════════════════════════════════════════════════════════════


def test_routes_endpoint(client):
    """Routes list returns 200 with data."""
    response = client.get("/api/routes")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
    assert data["count"] > 0


def test_route_fields_present(client):
    """Each route has all required fields."""
    response = client.get("/api/routes")
    data = response.json()
    for r in data["data"]:
        for field in ("route_id", "origin", "destination", "via",
                      "distance_km", "estimated_days", "estimated_cost", "status"):
            assert field in r, f"Missing route field: {field}"
        assert isinstance(r["route_id"], str)
        assert isinstance(r["distance_km"], (int, float))
        assert isinstance(r["estimated_cost"], (int, float))
