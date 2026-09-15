"""
RouteX Backend — Data Loader.

Loads CSV files from app/data/ into an in-memory DataStore singleton.
Handles missing files, malformed rows, and negative values gracefully.
"""

import csv
from pathlib import Path
from typing import Dict

from app.config import DATA_DIR
from app.models.shipment import Shipment
from app.models.disruption import Disruption
from app.models.route import Route
from app.models.carrier import Carrier
from app.utils.validators import validate_positive_number, validate_duration


class DataStore:
    """In-memory data store backed by CSV files."""

    def __init__(self) -> None:
        self.shipments: Dict[str, Shipment] = {}
        self.disruptions: Dict[str, Disruption] = {}
        self.routes: Dict[str, Route] = {}
        self.carriers: Dict[str, Carrier] = {}
        self._loaded: bool = False

    def load(self) -> None:
        """Load all CSV files. Safe to call multiple times (idempotent)."""
        self.shipments = self._load_shipments()
        self.disruptions = self._load_disruptions()
        self.routes = self._load_routes()
        self.carriers = self._load_carriers()
        self._loaded = True

    # ── Private loaders ───────────────────────────────────────────────────

    def _load_shipments(self) -> Dict[str, Shipment]:
        path = DATA_DIR / "shipments.csv"
        if not path.exists():
            return {}
        result: Dict[str, Shipment] = {}
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    cargo_value = float(row["cargo_value"])
                    validate_positive_number(cargo_value, "cargo_value")
                except (ValueError, KeyError):
                    cargo_value = 0.0
                shipment = Shipment(
                    shipment_id=str(row["shipment_id"]).strip(),
                    origin=row["origin"].strip(),
                    destination=row["destination"].strip(),
                    route_id=str(row["route_id"]).strip(),
                    carrier_id=str(row["carrier_id"]).strip(),
                    cargo_type=row["cargo_type"].strip(),
                    cargo_value=cargo_value,
                    priority=row["priority"].strip().upper(),
                    eta=row["eta"].strip(),
                    status=row["status"].strip().upper(),
                )
                result[shipment.shipment_id] = shipment
        return result

    def _load_disruptions(self) -> Dict[str, Disruption]:
        path = DATA_DIR / "disruptions.csv"
        if not path.exists():
            return {}
        result: Dict[str, Disruption] = {}
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    duration = int(row["duration_days"])
                    validate_duration(duration)
                except (ValueError, KeyError):
                    duration = 0
                disruption = Disruption(
                    disruption_id=str(row["disruption_id"]).strip(),
                    location=row["location"].strip(),
                    type=row["type"].strip().upper(),
                    severity=row["severity"].strip().upper(),
                    duration_days=duration,
                    description=row["description"].strip(),
                    status=row["status"].strip().upper(),
                )
                result[disruption.disruption_id] = disruption
        return result

    def _load_routes(self) -> Dict[str, Route]:
        path = DATA_DIR / "routes.csv"
        if not path.exists():
            return {}
        result: Dict[str, Route] = {}
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                route = Route(
                    route_id=str(row["route_id"]).strip(),
                    origin=row["origin"].strip(),
                    destination=row["destination"].strip(),
                    via=row["via"].strip(),
                    distance_km=float(row["distance_km"]),
                    estimated_days=int(row["estimated_days"]),
                    estimated_cost=float(row["estimated_cost"]),
                    status=row["status"].strip().upper(),
                )
                result[route.route_id] = route
        return result

    def _load_carriers(self) -> Dict[str, Carrier]:
        path = DATA_DIR / "carriers.csv"
        if not path.exists():
            return {}
        result: Dict[str, Carrier] = {}
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                carrier = Carrier(
                    carrier_id=str(row["carrier_id"]).strip(),
                    name=row["name"].strip(),
                    capacity=int(row["capacity"]),
                    reliability_score=float(row["reliability_score"]),
                    status=row["status"].strip().upper(),
                )
                result[carrier.carrier_id] = carrier
        return result


# ── Singleton ─────────────────────────────────────────────────────────────────

_data_store = DataStore()


def get_data_store() -> DataStore:
    """Return the singleton DataStore, loading data on first access."""
    if not _data_store._loaded:
        _data_store.load()
    return _data_store
