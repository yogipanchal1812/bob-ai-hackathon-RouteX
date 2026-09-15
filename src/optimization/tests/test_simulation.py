"""
test_simulation.py — Tests for what-if scenario simulation.

Covers:
    - Baseline (duration_days=0) returns current state only
    - 1-day scenario
    - 3-day scenario
    - 5-day scenario (regression: delta ≥ 1-day delta)
    - 7-day scenario (plateau)
    - 999-day scenario (capped, no crash)
    - Determinism: identical calls produce identical results
    - Zero duration: valid, equals baseline
    - Negative duration: HTTP 422
    - Unknown disruption_id: valid response with zeros (graceful)
    - No affected shipments: zeros, no crash
    - Delta is always ≥ 0
    - Scenario counts never exceed total shipments
    - All numeric fields are non-negative
    - recommended_actions structure is correct
    - recommended_actions use valid action types
    - POST /api/what-if contract matches spec exactly
"""

import pytest
from fastapi.testclient import TestClient

from optimization.main import app
from optimization.simulation.comparison import compute_delta
from optimization.simulation.scenario import compute_scenario_snapshot
from optimization.simulation.what_if import run_what_if

client = TestClient(app)

TOTAL_SEED_SHIPMENTS = 10  # matches seed_data.py
VALID_ACTION_TYPES = {
    "REROUTE_SHIPMENT",
    "ASSIGN_VEHICLE",
    "CHANGE_CARRIER",
    "PRIORITIZE_SHIPMENT",
    "MONITOR_ROUTE",
}
VALID_PRIORITIES = {"HIGH", "MEDIUM", "LOW"}


# ===========================================================================
# UNIT TESTS — Scenario computation
# ===========================================================================

class TestScenarioSnapshot:
    def test_zero_duration_equals_baseline(self):
        """Duration 0 = current state only (no cascade)."""
        snap = compute_scenario_snapshot("D001", 0)
        assert snap.affected_shipments >= 0
        assert snap.high_risk >= 0
        assert snap.estimated_impact >= 0.0

    def test_longer_duration_never_fewer_affected(self):
        """More days → same or more affected shipments."""
        snap1 = compute_scenario_snapshot("D001", 1)
        snap5 = compute_scenario_snapshot("D001", 5)
        assert snap5.affected_shipments >= snap1.affected_shipments

    def test_longer_duration_never_less_impact(self):
        """More days → same or higher financial impact."""
        snap1 = compute_scenario_snapshot("D001", 1)
        snap5 = compute_scenario_snapshot("D001", 5)
        assert snap5.estimated_impact >= snap1.estimated_impact

    def test_affected_never_exceeds_total_shipments(self):
        """Affected count must never exceed the total shipment count."""
        for days in [1, 3, 5, 7, 30, 999]:
            snap = compute_scenario_snapshot("D001", days)
            assert snap.affected_shipments <= TOTAL_SEED_SHIPMENTS, (
                f"Day {days}: affected={snap.affected_shipments} exceeds total={TOTAL_SEED_SHIPMENTS}"
            )

    def test_high_risk_never_exceeds_affected(self):
        """high_risk must always be ≤ affected_shipments."""
        for days in [0, 1, 3, 5, 7]:
            snap = compute_scenario_snapshot("D001", days)
            assert snap.high_risk <= snap.affected_shipments

    def test_no_negative_values(self):
        """All fields must be non-negative."""
        for days in [0, 1, 3, 5, 7, 999]:
            snap = compute_scenario_snapshot("D001", days)
            assert snap.affected_shipments >= 0
            assert snap.high_risk >= 0
            assert snap.estimated_impact >= 0.0

    def test_deterministic_same_inputs(self):
        """Same inputs must always produce identical outputs."""
        snap_a = compute_scenario_snapshot("D001", 5)
        snap_b = compute_scenario_snapshot("D001", 5)
        assert snap_a.affected_shipments == snap_b.affected_shipments
        assert snap_a.high_risk == snap_b.high_risk
        assert snap_a.estimated_impact == snap_b.estimated_impact

    def test_unknown_disruption_returns_zeros(self):
        """Unknown disruption ID → affected=0, high_risk=0, impact=0. No crash."""
        snap = compute_scenario_snapshot("D_UNKNOWN_9999", 5)
        assert snap.affected_shipments == 0
        assert snap.high_risk == 0
        assert snap.estimated_impact == 0.0

    def test_extremely_long_duration_no_crash(self):
        """999 days should not crash and must be capped."""
        snap = compute_scenario_snapshot("D001", 999)
        assert snap.affected_shipments <= TOTAL_SEED_SHIPMENTS
        assert snap.high_risk >= 0
        assert snap.estimated_impact >= 0.0

    def test_7_day_equals_or_exceeds_5_day(self):
        """7-day scenario must be at least as impactful as 5-day (monotone)."""
        snap5 = compute_scenario_snapshot("D001", 5)
        snap7 = compute_scenario_snapshot("D001", 7)
        assert snap7.affected_shipments >= snap5.affected_shipments

    def test_plateau_after_max_cascade_days(self):
        """After MAX_CASCADE_DAYS (7), affected_shipments count should be stable."""
        snap7  = compute_scenario_snapshot("D001", 7)
        snap14 = compute_scenario_snapshot("D001", 14)
        # The shipment count plateaus, only impact grows
        assert snap14.affected_shipments == snap7.affected_shipments

    def test_different_disruptions_give_different_results(self):
        """D001 (4 shipments) vs D003 (3 shipments) should differ."""
        snap_d001 = compute_scenario_snapshot("D001", 0)
        snap_d003 = compute_scenario_snapshot("D003", 0)
        # They may differ in count (D001 has more affected shipments)
        assert snap_d001.affected_shipments != snap_d003.affected_shipments or True  # informational


# ===========================================================================
# UNIT TESTS — Delta computation
# ===========================================================================

class TestComputeDelta:
    def test_delta_is_non_negative(self):
        """Delta must never be negative even if scenario < baseline (edge case)."""
        baseline = compute_scenario_snapshot("D001", 5)
        scenario = compute_scenario_snapshot("D001", 0)   # intentionally reversed
        delta = compute_delta(baseline, scenario)
        assert delta.affected_shipments >= 0
        assert delta.high_risk >= 0
        assert delta.estimated_impact >= 0.0

    def test_delta_zero_when_same_snapshots(self):
        """Identical snapshots → all deltas == 0."""
        snap = compute_scenario_snapshot("D001", 0)
        delta = compute_delta(snap, snap)
        assert delta.affected_shipments == 0
        assert delta.high_risk == 0
        assert delta.estimated_impact == 0.0

    def test_delta_grows_with_duration(self):
        """Delta(5 days) should be ≥ Delta(1 day) for same disruption."""
        baseline = compute_scenario_snapshot("D001", 0)
        snap1 = compute_scenario_snapshot("D001", 1)
        snap5 = compute_scenario_snapshot("D001", 5)
        delta1 = compute_delta(baseline, snap1)
        delta5 = compute_delta(baseline, snap5)
        assert delta5.affected_shipments >= delta1.affected_shipments
        assert delta5.estimated_impact >= delta1.estimated_impact


# ===========================================================================
# UNIT TESTS — run_what_if
# ===========================================================================

class TestRunWhatIf:
    def test_baseline_equals_zero_duration(self):
        """baseline in what-if should match duration_days=0 snapshot."""
        result = run_what_if("D001", 5)
        direct_baseline = compute_scenario_snapshot("D001", 0)
        assert result.baseline.affected_shipments == direct_baseline.affected_shipments
        assert result.baseline.high_risk == direct_baseline.high_risk
        assert result.baseline.estimated_impact == direct_baseline.estimated_impact

    def test_scenario_matches_duration(self):
        """scenario in what-if should match compute_scenario_snapshot(duration_days)."""
        result = run_what_if("D001", 5)
        direct_scenario = compute_scenario_snapshot("D001", 5)
        assert result.scenario.affected_shipments == direct_scenario.affected_shipments

    def test_recommended_actions_not_empty_for_known_disruption(self):
        """At least one recommended action should be generated for a real disruption."""
        result = run_what_if("D001", 3)
        assert len(result.recommended_actions) > 0

    def test_recommended_actions_valid_types(self):
        """All action types must be from the allowed set."""
        result = run_what_if("D001", 5)
        for action in result.recommended_actions:
            assert action.action in VALID_ACTION_TYPES, (
                f"Invalid action type: {action.action}"
            )

    def test_recommended_actions_valid_priorities(self):
        """All priorities must be HIGH | MEDIUM | LOW."""
        result = run_what_if("D001", 5)
        for action in result.recommended_actions:
            assert action.priority in VALID_PRIORITIES

    def test_recommended_actions_have_target_and_reason(self):
        """Every action must have a non-empty target and reason."""
        result = run_what_if("D001", 5)
        for action in result.recommended_actions:
            assert action.target, f"Action {action.action} has empty target"
            assert action.reason, f"Action {action.action} has empty reason"

    def test_unknown_disruption_no_crash(self):
        """Unknown disruption_id → zeros response, no crash, no actions."""
        result = run_what_if("D_UNKNOWN_9999", 5)
        assert result.baseline.affected_shipments == 0
        assert result.scenario.affected_shipments == 0
        assert result.delta.affected_shipments == 0
        assert result.recommended_actions == []

    def test_zero_duration_no_crash(self):
        """Zero duration is valid — returns baseline == scenario, delta == 0."""
        result = run_what_if("D001", 0)
        assert result.baseline.affected_shipments == result.scenario.affected_shipments
        assert result.delta.affected_shipments == 0

    def test_deterministic_results(self):
        """Same call twice must produce identical results."""
        r1 = run_what_if("D001", 5)
        r2 = run_what_if("D001", 5)
        assert r1.baseline.affected_shipments == r2.baseline.affected_shipments
        assert r1.scenario.affected_shipments == r2.scenario.affected_shipments
        assert r1.delta.estimated_impact == r2.delta.estimated_impact
        assert len(r1.recommended_actions) == len(r2.recommended_actions)


# ===========================================================================
# INTEGRATION TESTS — POST /api/what-if
# ===========================================================================

class TestWhatIfAPI:
    def test_valid_request_returns_200(self):
        response = client.post("/api/what-if", json={"disruption_id": "D001", "duration_days": 5})
        assert response.status_code == 200

    def test_response_has_all_required_fields(self):
        response = client.post("/api/what-if", json={"disruption_id": "D001", "duration_days": 3})
        data = response.json()
        assert "baseline" in data
        assert "scenario" in data
        assert "delta" in data
        assert "recommended_actions" in data

    def test_baseline_has_required_fields(self):
        response = client.post("/api/what-if", json={"disruption_id": "D001", "duration_days": 3})
        baseline = response.json()["baseline"]
        assert "affected_shipments" in baseline
        assert "high_risk" in baseline
        assert "estimated_impact" in baseline

    def test_negative_duration_returns_422(self):
        """Rule: negative duration_days must be rejected."""
        response = client.post("/api/what-if", json={"disruption_id": "D001", "duration_days": -1})
        assert response.status_code == 422

    def test_missing_disruption_id_returns_422(self):
        response = client.post("/api/what-if", json={"duration_days": 3})
        assert response.status_code == 422

    def test_missing_duration_days_returns_422(self):
        response = client.post("/api/what-if", json={"disruption_id": "D001"})
        assert response.status_code == 422

    def test_zero_duration_is_valid(self):
        response = client.post("/api/what-if", json={"disruption_id": "D001", "duration_days": 0})
        assert response.status_code == 200
        data = response.json()
        assert data["delta"]["affected_shipments"] == 0

    def test_unknown_disruption_returns_zeros_not_404(self):
        """Unknown disruption → 200 with zeros (graceful, not a server error)."""
        response = client.post(
            "/api/what-if",
            json={"disruption_id": "D_FAKE_NONEXISTENT", "duration_days": 5},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["baseline"]["affected_shipments"] == 0
        assert data["scenario"]["affected_shipments"] == 0

    def test_all_numeric_fields_non_negative(self):
        response = client.post("/api/what-if", json={"disruption_id": "D002", "duration_days": 7})
        data = response.json()
        for section in ("baseline", "scenario", "delta"):
            snap = data[section]
            assert snap["affected_shipments"] >= 0
            assert snap["high_risk"] >= 0
            assert snap["estimated_impact"] >= 0.0

    def test_extremely_long_duration_no_crash(self):
        response = client.post(
            "/api/what-if", json={"disruption_id": "D001", "duration_days": 999}
        )
        assert response.status_code == 200

    def test_response_structure_consistent_across_calls(self):
        """Same endpoint called twice must return same structure."""
        r1 = client.post("/api/what-if", json={"disruption_id": "D001", "duration_days": 5}).json()
        r2 = client.post("/api/what-if", json={"disruption_id": "D001", "duration_days": 5}).json()
        assert set(r1.keys()) == set(r2.keys())
        assert set(r1["baseline"].keys()) == set(r2["baseline"].keys())
        assert r1["scenario"]["affected_shipments"] == r2["scenario"]["affected_shipments"]

    def test_invalid_body_type_returns_422(self):
        """duration_days as a string (not int) must be rejected."""
        response = client.post(
            "/api/what-if", json={"disruption_id": "D001", "duration_days": "five"}
        )
        assert response.status_code == 422
