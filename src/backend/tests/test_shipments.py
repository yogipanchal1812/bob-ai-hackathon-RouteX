"""Tests for shipment API endpoints."""


def test_list_shipments(client):
    """GET /api/shipments returns 200 with a JSON array."""
    response = client.get("/api/shipments")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
    assert data["count"] == len(data["data"])
    assert data["count"] > 0


def test_list_shipments_filter_by_status(client):
    """GET /api/shipments?status=IN_TRANSIT only returns matching shipments."""
    response = client.get("/api/shipments?status=IN_TRANSIT")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    for shipment in data["data"]:
        assert shipment["status"] == "IN_TRANSIT"


def test_list_shipments_filter_no_results(client):
    """Filtering by a status with no matches returns empty list (not an error)."""
    response = client.get("/api/shipments?status=CANCELLED")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["count"] == 0
    assert data["data"] == []


def test_get_shipment_exists(client):
    """GET /api/shipments/SH001 returns the correct shipment."""
    response = client.get("/api/shipments/SH001")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["shipment_id"] == "SH001"
    # All required fields present
    required = [
        "shipment_id", "origin", "destination", "route_id",
        "carrier_id", "cargo_type", "cargo_value", "priority",
        "eta", "status",
    ]
    for field in required:
        assert field in data["data"], f"Missing field: {field}"


def test_get_shipment_not_found(client):
    """GET /api/shipments/NONEXISTENT returns 404."""
    response = client.get("/api/shipments/NONEXISTENT")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data


def test_shipment_ids_are_strings(client):
    """All ID fields must be strings, never integers."""
    response = client.get("/api/shipments")
    data = response.json()
    for s in data["data"]:
        assert isinstance(s["shipment_id"], str)
        assert isinstance(s["route_id"], str)
        assert isinstance(s["carrier_id"], str)


def test_shipment_cargo_value_is_numeric(client):
    """cargo_value must be a number (no formatted currency string)."""
    response = client.get("/api/shipments/SH001")
    data = response.json()
    assert isinstance(data["data"]["cargo_value"], (int, float))
