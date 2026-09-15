"""Tests for disruption API endpoints."""


def test_list_disruptions(client):
    """GET /api/disruptions returns 200 with a JSON array."""
    response = client.get("/api/disruptions")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
    assert data["count"] == len(data["data"])
    assert data["count"] > 0


def test_list_disruptions_filter_active(client):
    """GET /api/disruptions?status=ACTIVE returns only active disruptions."""
    response = client.get("/api/disruptions?status=ACTIVE")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    for d in data["data"]:
        assert d["status"] == "ACTIVE"


def test_list_disruptions_filter_resolved(client):
    """Filter by RESOLVED status."""
    response = client.get("/api/disruptions?status=RESOLVED")
    assert response.status_code == 200
    data = response.json()
    for d in data["data"]:
        assert d["status"] == "RESOLVED"


def test_get_disruption_exists(client):
    """GET /api/disruptions/D001 returns the correct disruption."""
    response = client.get("/api/disruptions/D001")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["disruption_id"] == "D001"
    required = [
        "disruption_id", "location", "type", "severity",
        "duration_days", "description", "status",
    ]
    for field in required:
        assert field in data["data"], f"Missing field: {field}"


def test_get_disruption_not_found(client):
    """GET /api/disruptions/NONEXISTENT returns 404."""
    response = client.get("/api/disruptions/NONEXISTENT")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data


def test_disruption_ids_are_strings(client):
    """disruption_id must be a string."""
    response = client.get("/api/disruptions")
    data = response.json()
    for d in data["data"]:
        assert isinstance(d["disruption_id"], str)


def test_disruption_duration_is_integer(client):
    """duration_days must be an integer."""
    response = client.get("/api/disruptions/D001")
    data = response.json()
    assert isinstance(data["data"]["duration_days"], int)
