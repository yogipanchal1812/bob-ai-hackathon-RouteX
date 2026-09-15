"""
seed_data.py — Deterministic in-memory seed dataset for Module 4.

Provides:
  - 20 fleet vehicles across 5 Indian logistic hubs
  - 5 carrier profiles with reliability and cost index
  - 12 route corridors including designated alternative bypass routes
  - 3 disruption events
  - 10 representative shipments
"""

from typing import Any, Dict, List, Optional

from optimization.schemas.fleet import Vehicle, VehicleStatus, VehicleType
from optimization.schemas.routes import Route

# ---------------------------------------------------------------------------
# 1. CARRIERS (5)
# ---------------------------------------------------------------------------
_CARRIERS: List[Dict[str, Any]] = [
    {
        "carrier_id": "C001",
        "name": "GlobalShip Logistics",
        "reliability_score": 92,  # integer or float per carrier_selector
        "cost_index": 1.10,
    },
    {
        "carrier_id": "C002",
        "name": "OceanBridge Freight",
        "reliability_score": 85,
        "cost_index": 0.95,
    },
    {
        "carrier_id": "C003",
        "name": "TransSea Carriers",
        "reliability_score": 78,
        "cost_index": 0.90,
    },
    {
        "carrier_id": "C004",
        "name": "PacificLine Shipping",
        "reliability_score": 88,
        "cost_index": 1.05,
    },
    {
        "carrier_id": "C005",
        "name": "HarborLink Transport",
        "reliability_score": 72,
        "cost_index": 0.85,
    },
]

# ---------------------------------------------------------------------------
# 2. ROUTES (12)
# ---------------------------------------------------------------------------
_ROUTES: List[Route] = [
    # Corridor 1: Mumbai -> Delhi
    Route(
        route_id="R001",
        origin="Mumbai",
        destination="Delhi",
        distance_km=1420.0,
        duration_hours=24.0,
        cost_usd=3200.0,
        disruption_exposure=0.85,
        carrier_id="C001",
        tags=["highway", "primary"],
    ),
    Route(
        route_id="R001_ALT1",
        origin="Mumbai",
        destination="Delhi",
        distance_km=1500.0,
        duration_hours=26.0,
        cost_usd=2900.0,
        disruption_exposure=0.15,
        carrier_id="C002",
        tags=["alternative", "coastal"],
    ),
    Route(
        route_id="R001_ALT2",
        origin="Mumbai",
        destination="Delhi",
        distance_km=1580.0,
        duration_hours=28.0,
        cost_usd=3500.0,
        disruption_exposure=0.35,
        carrier_id="C003",
        tags=["alternative", "bypass"],
    ),
    # Corridor 2: Chennai -> Bangalore
    Route(
        route_id="R003",
        origin="Chennai",
        destination="Bangalore",
        distance_km=350.0,
        duration_hours=6.0,
        cost_usd=1200.0,
        disruption_exposure=0.90,
        carrier_id="C001",
        tags=["primary"],
    ),
    Route(
        route_id="R003_ALT1",
        origin="Chennai",
        destination="Bangalore",
        distance_km=380.0,
        duration_hours=7.0,
        cost_usd=1100.0,
        disruption_exposure=0.20,
        carrier_id="C002",
        tags=["alternative"],
    ),
    # Corridor 3: Kolkata -> Delhi
    Route(
        route_id="R006",
        origin="Kolkata",
        destination="Delhi",
        distance_km=1500.0,
        duration_hours=28.0,
        cost_usd=3600.0,
        disruption_exposure=0.70,
        carrier_id="C003",
        tags=["primary"],
    ),
    Route(
        route_id="R006_ALT1",
        origin="Kolkata",
        destination="Delhi",
        distance_km=1600.0,
        duration_hours=30.0,
        cost_usd=3400.0,
        disruption_exposure=0.25,
        carrier_id="C004",
        tags=["alternative"],
    ),
    # Other Corridors
    Route(
        route_id="R004",
        origin="Surat",
        destination="Ahmedabad",
        distance_km=260.0,
        duration_hours=4.5,
        cost_usd=800.0,
        disruption_exposure=0.10,
        carrier_id="C002",
        tags=["highway"],
    ),
    Route(
        route_id="R002",
        origin="Pune",
        destination="Mumbai",
        distance_km=150.0,
        duration_hours=3.0,
        cost_usd=500.0,
        disruption_exposure=0.05,
        carrier_id="C001",
        tags=["express"],
    ),
    Route(
        route_id="R005",
        origin="Delhi",
        destination="Jaipur",
        distance_km=280.0,
        duration_hours=5.0,
        cost_usd=750.0,
        disruption_exposure=0.12,
        carrier_id="C002",
        tags=["express"],
    ),
    Route(
        route_id="R007",
        origin="Hyderabad",
        destination="Bangalore",
        distance_km=570.0,
        duration_hours=9.0,
        cost_usd=1600.0,
        disruption_exposure=0.18,
        carrier_id="C003",
        tags=["corridor"],
    ),
    Route(
        route_id="R008",
        origin="Ahmedabad",
        destination="Mumbai",
        distance_km=530.0,
        duration_hours=8.5,
        cost_usd=1500.0,
        disruption_exposure=0.22,
        carrier_id="C004",
        tags=["coastal"],
    ),
]

# ---------------------------------------------------------------------------
# 3. DISRUPTIONS (3)
# ---------------------------------------------------------------------------
_DISRUPTIONS: List[Dict[str, Any]] = [
    {
        "disruption_id": "D001",
        "name": "Monsoon Flooding",
        "location": "Western Corridor",
        "affected_routes": ["R001", "R006"],
        "severity": "HIGH",
        "duration_days": 7,
    },
    {
        "disruption_id": "D002",
        "name": "Highway Blockade",
        "location": "Southern Corridor",
        "affected_routes": ["R003"],
        "severity": "CRITICAL",
        "duration_days": 14,
    },
    {
        "disruption_id": "D003",
        "name": "Port Congestion",
        "location": "Eastern Corridor",
        "affected_routes": [],
        "severity": "MEDIUM",
        "duration_days": 3,
    },
]

# ---------------------------------------------------------------------------
# 4. SHIPMENTS (10)
# ---------------------------------------------------------------------------
_SHIPMENTS: List[Dict[str, Any]] = [
    {
        "shipment_id": "SH001",
        "origin": "Mumbai",
        "destination": "Delhi",
        "weight_tons": 18.0,
        "route_id": "R001",
        "carrier_id": "C001",
        "disruption_id": "D001",
        "risk_score": 85,
        "priority": "HIGH",
        "cargo_type": "Electronics",
        "cargo_value": 2500000.0,
    },
    {
        "shipment_id": "SH002",
        "origin": "Pune",
        "destination": "Mumbai",
        "weight_tons": 12.0,
        "route_id": "R002",
        "carrier_id": "C002",
        "disruption_id": None,
        "risk_score": 25,
        "priority": "MEDIUM",
        "cargo_type": "Textiles",
        "cargo_value": 800000.0,
    },
    {
        "shipment_id": "SH003",
        "origin": "Chennai",
        "destination": "Bangalore",
        "weight_tons": 8.0,
        "route_id": "R003",
        "carrier_id": "C001",
        "disruption_id": "D002",
        "risk_score": 92,
        "priority": "CRITICAL",
        "cargo_type": "Pharmaceuticals",
        "cargo_value": 4500000.0,
    },
    {
        "shipment_id": "SH004",
        "origin": "Surat",
        "destination": "Ahmedabad",
        "weight_tons": 22.0,
        "route_id": "R004",
        "carrier_id": "C002",
        "disruption_id": None,
        "risk_score": 30,
        "priority": "MEDIUM",
        "cargo_type": "Machinery",
        "cargo_value": 1200000.0,
    },
    {
        "shipment_id": "SH005",
        "origin": "Delhi",
        "destination": "Jaipur",
        "weight_tons": 15.0,
        "route_id": "R005",
        "carrier_id": "C004",
        "disruption_id": None,
        "risk_score": 35,
        "priority": "HIGH",
        "cargo_type": "Automotive Parts",
        "cargo_value": 3200000.0,
    },
    {
        "shipment_id": "SH006",
        "origin": "Kolkata",
        "destination": "Delhi",
        "weight_tons": 25.0,
        "route_id": "R006",
        "carrier_id": "C003",
        "disruption_id": "D001",
        "risk_score": 75,
        "priority": "LOW",
        "cargo_type": "Furniture",
        "cargo_value": 600000.0,
    },
    {
        "shipment_id": "SH007",
        "origin": "Hyderabad",
        "destination": "Bangalore",
        "weight_tons": 14.0,
        "route_id": "R007",
        "carrier_id": "C005",
        "disruption_id": None,
        "risk_score": 40,
        "priority": "MEDIUM",
        "cargo_type": "Consumer Goods",
        "cargo_value": 950000.0,
    },
    {
        "shipment_id": "SH008",
        "origin": "Ahmedabad",
        "destination": "Mumbai",
        "weight_tons": 10.0,
        "route_id": "R008",
        "carrier_id": "C003",
        "disruption_id": None,
        "risk_score": 20,
        "priority": "LOW",
        "cargo_type": "Spices",
        "cargo_value": 350000.0,
    },
    {
        "shipment_id": "SH009",
        "origin": "Mumbai",
        "destination": "Delhi",
        "weight_tons": 16.0,
        "route_id": "R001",
        "carrier_id": "C004",
        "disruption_id": "D001",
        "risk_score": 88,
        "priority": "CRITICAL",
        "cargo_type": "Medical Equipment",
        "cargo_value": 5000000.0,
    },
    {
        "shipment_id": "SH010",
        "origin": "Chennai",
        "destination": "Bangalore",
        "weight_tons": 11.0,
        "route_id": "R003",
        "carrier_id": "C001",
        "disruption_id": "D002",
        "risk_score": 72,
        "priority": "HIGH",
        "cargo_type": "Chemicals",
        "cargo_value": 2100000.0,
    },
]

# ---------------------------------------------------------------------------
# 5. VEHICLES (20)
# ---------------------------------------------------------------------------
_VEHICLES: List[Vehicle] = [
    # 8 AVAILABLE
    Vehicle(vehicle_id="V001", type=VehicleType.TRUCK, location="Mumbai", capacity_tons=25.0, status=VehicleStatus.AVAILABLE, available=True, carrier_id="C001"),
    Vehicle(vehicle_id="V002", type=VehicleType.CONTAINER, location="Mumbai", capacity_tons=30.0, status=VehicleStatus.AVAILABLE, available=True, carrier_id="C001"),
    Vehicle(vehicle_id="V003", type=VehicleType.REFRIGERATED, location="Chennai", capacity_tons=15.0, status=VehicleStatus.AVAILABLE, available=True, carrier_id="C001"),
    Vehicle(vehicle_id="V004", type=VehicleType.TRUCK, location="Delhi", capacity_tons=20.0, status=VehicleStatus.AVAILABLE, available=True, carrier_id="C002"),
    Vehicle(vehicle_id="V005", type=VehicleType.VAN, location="Pune", capacity_tons=5.0, status=VehicleStatus.AVAILABLE, available=True, carrier_id="C002"),
    Vehicle(vehicle_id="V006", type=VehicleType.FLATBED, location="Kolkata", capacity_tons=28.0, status=VehicleStatus.AVAILABLE, available=True, carrier_id="C003"),
    Vehicle(vehicle_id="V007", type=VehicleType.TRUCK, location="Ahmedabad", capacity_tons=22.0, status=VehicleStatus.AVAILABLE, available=True, carrier_id="C004"),
    Vehicle(vehicle_id="V008", type=VehicleType.CONTAINER, location="Bangalore", capacity_tons=26.0, status=VehicleStatus.AVAILABLE, available=True, carrier_id="C005"),

    # 6 IN_TRANSIT
    Vehicle(vehicle_id="V009", type=VehicleType.TRUCK, location="Mumbai", capacity_tons=24.0, status=VehicleStatus.IN_TRANSIT, available=False, carrier_id="C001"),
    Vehicle(vehicle_id="V010", type=VehicleType.CONTAINER, location="Delhi", capacity_tons=30.0, status=VehicleStatus.IN_TRANSIT, available=False, carrier_id="C002"),
    Vehicle(vehicle_id="V011", type=VehicleType.REFRIGERATED, location="Chennai", capacity_tons=18.0, status=VehicleStatus.IN_TRANSIT, available=False, carrier_id="C003"),
    Vehicle(vehicle_id="V012", type=VehicleType.TRUCK, location="Kolkata", capacity_tons=20.0, status=VehicleStatus.IN_TRANSIT, available=False, carrier_id="C004"),
    Vehicle(vehicle_id="V013", type=VehicleType.VAN, location="Surat", capacity_tons=6.0, status=VehicleStatus.IN_TRANSIT, available=False, carrier_id="C005"),
    Vehicle(vehicle_id="V014", type=VehicleType.CONTAINER, location="Hyderabad", capacity_tons=28.0, status=VehicleStatus.IN_TRANSIT, available=False, carrier_id="C001"),

    # 3 IDLE
    Vehicle(vehicle_id="V015", type=VehicleType.TRUCK, location="Mumbai", capacity_tons=20.0, status=VehicleStatus.IDLE, available=True, carrier_id="C001"),
    Vehicle(vehicle_id="V016", type=VehicleType.FLATBED, location="Pune", capacity_tons=25.0, status=VehicleStatus.IDLE, available=True, carrier_id="C002"),
    Vehicle(vehicle_id="V017", type=VehicleType.CONTAINER, location="Chennai", capacity_tons=30.0, status=VehicleStatus.IDLE, available=True, carrier_id="C003"),

    # 3 MAINTENANCE
    Vehicle(vehicle_id="V018", type=VehicleType.TRUCK, location="Delhi", capacity_tons=22.0, status=VehicleStatus.MAINTENANCE, available=False, carrier_id="C004"),
    Vehicle(vehicle_id="V019", type=VehicleType.VAN, location="Kolkata", capacity_tons=8.0, status=VehicleStatus.MAINTENANCE, available=False, carrier_id="C005"),
    Vehicle(vehicle_id="V020", type=VehicleType.REFRIGERATED, location="Mumbai", capacity_tons=16.0, status=VehicleStatus.MAINTENANCE, available=False, carrier_id="C001"),
]


# ---------------------------------------------------------------------------
# Accessor functions
# ---------------------------------------------------------------------------

def get_vehicles() -> List[Vehicle]:
    """Return all 20 fleet vehicles."""
    return list(_VEHICLES)


def get_vehicle_by_id(vehicle_id: str) -> Optional[Vehicle]:
    """Lookup vehicle by ID."""
    for v in _VEHICLES:
        if v.vehicle_id == vehicle_id:
            return v
    return None


def get_carriers() -> List[Dict[str, Any]]:
    """Return all 5 carrier profiles."""
    return list(_CARRIERS)


def get_routes() -> List[Route]:
    """Return all 12 routes."""
    return list(_ROUTES)


def get_route_by_id(route_id: str) -> Optional[Route]:
    """Lookup route by ID."""
    for r in _ROUTES:
        if r.route_id == route_id:
            return r
    return None


def get_shipments() -> List[Dict[str, Any]]:
    """Return all 10 seed shipments."""
    return list(_SHIPMENTS)


def get_shipment_by_id(shipment_id: str) -> Optional[Dict[str, Any]]:
    """Lookup shipment by ID."""
    for s in _SHIPMENTS:
        if s["shipment_id"] == shipment_id:
            return s
    return None


def get_shipments_by_disruption(disruption_id: str) -> List[Dict[str, Any]]:
    """Return all shipments affected by a specific disruption."""
    return [s for s in _SHIPMENTS if s.get("disruption_id") == disruption_id]


def get_disruptions() -> List[Dict[str, Any]]:
    """Return all 3 seed disruptions."""
    return list(_DISRUPTIONS)


def get_disruption_by_id(disruption_id: str) -> Optional[Dict[str, Any]]:
    """Lookup disruption by ID."""
    for d in _DISRUPTIONS:
        if d["disruption_id"] == disruption_id:
            return d
    return None
