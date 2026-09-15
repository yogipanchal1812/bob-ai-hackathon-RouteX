"""
test_fleet.py — Tests for fleet utilization and vehicle matching.

Covers:
    - Utilization with full seed fleet
    - Utilization with zero vehicles (edge case)
    - Utilization with all-MAINTENANCE fleet (0% utilization)
    - Utilization with all-IN_TRANSIT fleet (100% utilization)
    - Utilization pct is always in [0, 100]
    - Vehicle matching — sufficient capacity
    - Vehicle matching — insufficient capacity (no match)
    - Vehicle matching — no available vehicles
    - Vehicle matching — empty vehicle list
    - Fleet API: GET /api/fleet
    - Fleet API: GET /api/fleet?status=AVAILABLE
    - Fleet API: GET /api/fleet/utilization
    - Fleet API: POST /api/optimize-fleet
    - Fleet API: POST /api/optimize-fleet with specific shipment_ids
"""

import pytest
from fastapi.testclient import TestClient

from optimization.fleet.allocation import match_vehicles_to_shipment
from optimization.fleet.utilization import calculate_utilization
from optimization.main import app
from optimization.schemas.fleet import Vehicle, VehicleStatus, VehicleType

client = TestClient(app)


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------

def make_vehicle(
    vehicle_id: str = "V999",
    status: VehicleStatus = VehicleStatus.AVAILABLE,
    capacity_tons: float = 20.0,
    location: str = "Mumbai",
    carrier_id: str = "C001",
) -> Vehicle:
    return Vehicle(
        vehicle_id=vehicle_id,
        type=VehicleType.TRUCK,
        location=location,
        capacity_tons=capacity_tons,
        status=status,
        available=status in (VehicleStatus.AVAILABLE, VehicleStatus.IDLE),
        carrier_id=carrier_id,
    )


def make_shipment(
    shipment_id: str = "SH999",
    origin: str = "Mumbai",
    weight_tons: float = 10.0,
    carrier_id: str = "C001",
) -> dict:
    return {
        "shipment_id": shipment_id,
        "origin": origin,
        "destination": "Delhi",
        "weight_tons": weight_tons,
        "carrier_id": carrier_id,
        "risk_score": 50,
        "disruption_id": "D999",
        "route_id": "R999",
    }


# ===========================================================================
# UNIT TESTS — Utilization
# ===========================================================================

class TestCalculateUtilization:
    def test_zero_vehicles_returns_zeros(self):
        """Empty fleet must not crash and must return 0 utilization."""
        report = calculate_utilization([])
        assert report.total_vehicles == 0
        assert report.available_vehicles == 0
        assert report.idle_vehicles == 0
        assert report.in_transit_vehicles == 0
        assert report.maintenance_vehicles == 0
        assert report.utilization_pct == 0.0

    def test_all_maintenance_is_zero_utilization(self):
        """All MAINTENANCE vehicles → 0% utilization, no division errors."""
        vehicles = [make_vehicle(f"V{i}", VehicleStatus.MAINTENANCE) for i in range(5)]
        report = calculate_utilization(vehicles)
        assert report.total_vehicles == 5
        assert report.maintenance_vehicles == 5
        assert report.in_transit_vehicles == 0
        assert report.utilization_pct == 0.0

    def test_all_in_transit_is_100_utilization(self):
        """All IN_TRANSIT → 100% utilization."""
        vehicles = [make_vehicle(f"V{i}", VehicleStatus.IN_TRANSIT) for i in range(4)]
        report = calculate_utilization(vehicles)
        assert report.total_vehicles == 4
        assert report.in_transit_vehicles == 4
        assert report.utilization_pct == 100.0

    def test_all_idle_is_zero_utilization(self):
        """IDLE vehicles are on-site but not active — 0% utilization."""
        vehicles = [make_vehicle(f"V{i}", VehicleStatus.IDLE) for i in range(3)]
        report = calculate_utilization(vehicles)
        assert report.utilization_pct == 0.0
        assert report.idle_vehicles == 3

    def test_mixed_fleet_utilization(self):
        """2 IN_TRANSIT out of 4 total = 50%."""
        vehicles = [
            make_vehicle("V1", VehicleStatus.IN_TRANSIT),
            make_vehicle("V2", VehicleStatus.IN_TRANSIT),
            make_vehicle("V3", VehicleStatus.AVAILABLE),
            make_vehicle("V4", VehicleStatus.IDLE),
        ]
        report = calculate_utilization(vehicles)
        assert report.total_vehicles == 4
        assert report.in_transit_vehicles == 2
        assert report.utilization_pct == 50.0

    def test_utilization_pct_always_in_range(self):
        """utilization_pct must always be in [0.0, 100.0]."""
        for n_transit in range(0, 6):
            total = 5
            vehicles = (
                [make_vehicle(f"V{i}", VehicleStatus.IN_TRANSIT) for i in range(n_transit)]
                + [make_vehicle(f"VA{i}", VehicleStatus.AVAILABLE) for i in range(total - n_transit)]
            )
            report = calculate_utilization(vehicles)
            assert 0.0 <= report.utilization_pct <= 100.0

    def test_counts_sum_to_total(self):
        """All status counts must add up to total_vehicles."""
        vehicles = [
            make_vehicle("V1", VehicleStatus.AVAILABLE),
            make_vehicle("V2", VehicleStatus.IN_TRANSIT),
            make_vehicle("V3", VehicleStatus.IDLE),
            make_vehicle("V4", VehicleStatus.MAINTENANCE),
            make_vehicle("V5", VehicleStatus.AVAILABLE),
        ]
        report = calculate_utilization(vehicles)
        total_by_status = (
            report.available_vehicles
            + report.in_transit_vehicles
            + report.idle_vehicles
            + report.maintenance_vehicles
        )
        assert total_by_status == report.total_vehicles


# ===========================================================================
# UNIT TESTS — Vehicle Matching / Allocation
# ===========================================================================

class TestVehicleMatching:
    def test_perfect_match_scores_100(self):
        """Vehicle available, capacity sufficient, same location, same carrier → 100."""
        vehicles = [make_vehicle("V1", VehicleStatus.AVAILABLE, 20.0, "Mumbai", "C001")]
        shipment = make_shipment("SH1", "Mumbai", 10.0, "C001")
        results = match_vehicles_to_shipment(shipment, vehicles)
        assert len(results) == 1
        assert results[0].match_score == 100
        assert results[0].vehicle_id == "V1"

    def test_insufficient_capacity_lowers_score(self):
        """Vehicle capacity < shipment weight → 30pts deducted from capacity."""
        vehicles = [make_vehicle("V1", VehicleStatus.AVAILABLE, 5.0, "Mumbai", "C001")]
        shipment = make_shipment("SH1", "Mumbai", 10.0, "C001")
        results = match_vehicles_to_shipment(shipment, vehicles)
        # Still returns the vehicle (it is available), but score is lower (no capacity points)
        assert len(results) == 1
        assert results[0].match_score < 100
        # Score = 40 (available) + 0 (capacity fail) + 20 (same region) + 10 (carrier) = 70
        assert results[0].match_score == 70

    def test_no_available_vehicles_returns_empty(self):
        """IN_TRANSIT and MAINTENANCE vehicles should NOT be returned."""
        vehicles = [
            make_vehicle("V1", VehicleStatus.IN_TRANSIT),
            make_vehicle("V2", VehicleStatus.MAINTENANCE),
        ]
        shipment = make_shipment("SH1", "Mumbai", 5.0, "C001")
        results = match_vehicles_to_shipment(shipment, vehicles)
        assert results == []

    def test_empty_vehicle_list_returns_empty(self):
        """Empty fleet → no matches, no crash."""
        results = match_vehicles_to_shipment(make_shipment(), [])
        assert results == []

    def test_idle_vehicle_is_dispatchable(self):
        """IDLE vehicles should be included in matching (they can be dispatched)."""
        vehicles = [make_vehicle("V1", VehicleStatus.IDLE, 20.0, "Mumbai", "C001")]
        shipment = make_shipment("SH1", "Mumbai", 10.0, "C001")
        results = match_vehicles_to_shipment(shipment, vehicles)
        assert len(results) == 1
        assert results[0].vehicle_id == "V1"

    def test_results_sorted_best_first(self):
        """Results must be sorted by match_score descending."""
        vehicles = [
            make_vehicle("V1", VehicleStatus.AVAILABLE, 5.0, "Delhi", "C002"),   # lower score
            make_vehicle("V2", VehicleStatus.AVAILABLE, 20.0, "Mumbai", "C001"), # higher score
        ]
        shipment = make_shipment("SH1", "Mumbai", 10.0, "C001")
        results = match_vehicles_to_shipment(shipment, vehicles)
        assert len(results) == 2
        assert results[0].match_score >= results[1].match_score

    def test_match_score_never_exceeds_100(self):
        """Match score must always be ≤ 100."""
        vehicles = [make_vehicle("V1", VehicleStatus.AVAILABLE, 999.0, "Mumbai", "C001")]
        shipment = make_shipment("SH1", "Mumbai", 1.0, "C001")
        results = match_vehicles_to_shipment(shipment, vehicles)
        assert all(r.match_score <= 100 for r in results)

    def test_reason_list_not_empty(self):
        """Every match result must include at least one reason."""
        vehicles = [make_vehicle("V1", VehicleStatus.AVAILABLE, 20.0, "Mumbai", "C001")]
        shipment = make_shipment("SH1", "Mumbai", 10.0, "C001")
        results = match_vehicles_to_shipment(shipment, vehicles)
        assert len(results[0].reason) > 0


# ===========================================================================
# INTEGRATION TESTS — Fleet API endpoints
# ===========================================================================

class TestFleetAPI:
    def test_get_fleet_returns_200(self):
        response = client.get("/api/fleet")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_fleet_vehicle_has_required_fields(self):
        response = client.get("/api/fleet")
        vehicle = response.json()[0]
        required_fields = {"vehicle_id", "type", "location", "capacity_tons", "status", "available", "carrier_id"}
        assert required_fields.issubset(vehicle.keys())

    def test_get_fleet_vehicle_ids_are_strings(self):
        """Rule 15: IDs must be strings."""
        response = client.get("/api/fleet")
        for vehicle in response.json():
            assert isinstance(vehicle["vehicle_id"], str)
            assert isinstance(vehicle["carrier_id"], str)

    def test_get_fleet_filter_by_status(self):
        response = client.get("/api/fleet?status=AVAILABLE")
        assert response.status_code == 200
        for vehicle in response.json():
            assert vehicle["status"] == "AVAILABLE"

    def test_get_fleet_filter_by_carrier(self):
        response = client.get("/api/fleet?carrier_id=C001")
        assert response.status_code == 200
        for vehicle in response.json():
            assert vehicle["carrier_id"] == "C001"

    def test_get_fleet_utilization_returns_200(self):
        response = client.get("/api/fleet/utilization")
        assert response.status_code == 200
        data = response.json()
        required_fields = {
            "total_vehicles", "available_vehicles", "idle_vehicles",
            "in_transit_vehicles", "maintenance_vehicles", "utilization_pct"
        }
        assert required_fields.issubset(data.keys())

    def test_get_fleet_utilization_pct_in_range(self):
        response = client.get("/api/fleet/utilization")
        data = response.json()
        assert 0.0 <= data["utilization_pct"] <= 100.0

    def test_get_fleet_utilization_counts_sum_to_total(self):
        response = client.get("/api/fleet/utilization")
        d = response.json()
        total_counted = (
            d["available_vehicles"] + d["idle_vehicles"]
            + d["in_transit_vehicles"] + d["maintenance_vehicles"]
        )
        assert total_counted == d["total_vehicles"]

    def test_optimize_fleet_no_body_returns_200(self):
        """Empty body (all fields optional) should work."""
        response = client.post("/api/optimize-fleet", json={})
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data
        assert "total_matches" in data
        assert "unmatched_shipment_ids" in data

    def test_optimize_fleet_with_disruption_id(self):
        response = client.post("/api/optimize-fleet", json={"disruption_id": "D001"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["matches"], list)
        assert data["total_matches"] == len(data["matches"])

    def test_optimize_fleet_specific_shipment_ids(self):
        response = client.post("/api/optimize-fleet", json={"shipment_ids": ["SH001", "SH002"]})
        assert response.status_code == 200

    def test_optimize_fleet_unknown_shipment_ids(self):
        """Unknown shipment IDs should return empty matches, not crash."""
        response = client.post("/api/optimize-fleet", json={"shipment_ids": ["SH999"]})
        assert response.status_code == 200
        data = response.json()
        assert data["total_matches"] == 0

    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
