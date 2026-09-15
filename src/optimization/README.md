# Module 4 — Fleet Utilization, Rerouting Support & What-If Simulation

**RouteX / ChainGuard AI** | Bob AI Hackathon | Member 4

---

## What This Module Does

This module is the **fleet optimization and scenario simulation engine** for the RouteX supply chain risk platform. It answers:

1. Which fleet assets are currently idle or available?
2. Which vehicles can serve shipments affected by disruptions?
3. How can fleet utilization improve?
4. What happens to the supply chain if a disruption lasts longer?
5. Which operational actions become necessary?

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/fleet` | List all fleet vehicles (filterable by `?status=` and `?carrier_id=`) |
| `GET` | `/api/fleet/utilization` | Fleet utilization report with counts and % |
| `POST` | `/api/optimize-fleet` | Vehicle-to-shipment matching for affected shipments |
| `POST` | `/api/what-if` | What-if scenario simulation (disruption duration impact) |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Interactive Swagger UI |

---

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Install & Run

```bash
# 1. Navigate to this module
cd src/optimization

# 2. (Optional) Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the server
uvicorn main:app --reload --port 8001
```

The API will be available at: `http://localhost:8001`
Interactive docs: `http://localhost:8001/docs`

### Environment Variables

Copy `../../.env.example` to `.env` in the repo root. Module-specific variables:

| Variable | Default | Description |
|---|---|---|
| `OPT_PORT` | `8001` | Port for this service |
| `OPT_LOG_LEVEL` | `INFO` | Logging level |
| `APP_ENV` | `development` | `development` or `production` |
| `DISRUPTION_API_URL` | *(none)* | Member 1's API URL. When absent, uses seed data |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:5173` | Frontend origins for CORS |

---

## Running Tests

```bash
cd src/optimization
pytest tests/ -v
```

Expected output: **all tests pass** with no errors, warnings, or skips.

---

## Module Structure

```
src/optimization/
├── main.py               ← FastAPI app entrypoint
├── config.py             ← Environment-based config
├── conftest.py           ← pytest path setup
├── requirements.txt      ← Python dependencies
│
├── schemas/
│   ├── fleet.py          ← Vehicle, utilization, match schemas (Pydantic v2)
│   ├── simulation.py     ← WhatIf request/response schemas
│   └── routes.py         ← Route and alternative route schemas
│
├── data/
│   └── seed_data.py      ← 20 vehicles, 10 shipments, 3 disruptions, 12 routes (deterministic)
│
├── fleet/
│   ├── utilization.py    ← Pure utilization calculation
│   ├── allocation.py     ← Vehicle-to-shipment matching (0–100 score)
│   └── fleet_service.py  ← Service layer (data → logic → API)
│
├── routing/
│   ├── route_selector.py ← Alternative route ranking
│   └── carrier_selector.py ← Carrier recommendation
│
├── simulation/
│   ├── scenario.py       ← Deterministic impact snapshot computation
│   ├── comparison.py     ← Baseline vs scenario delta
│   └── what_if.py        ← What-if orchestrator + action generator
│
├── api/
│   ├── fleet_router.py   ← GET /api/fleet, GET /api/fleet/utilization, POST /api/optimize-fleet
│   └── simulation_router.py ← POST /api/what-if
│
└── tests/
    ├── test_fleet.py     ← Fleet utilization + matching + API tests
    ├── test_simulation.py ← What-if scenario + delta + API tests
    └── test_routes.py    ← Route ranking + carrier selection tests
```

---

## Fleet Utilization Formula

```
utilization_pct = (in_transit_count / total_count) × 100

Where:
  in_transit_count = vehicles with status == IN_TRANSIT
  total_count      = all vehicles in the fleet
  
Edge cases:
  total_count == 0  →  utilization_pct = 0.0  (no division by zero)
```

**IDLE** vehicles are tracked separately — they are on-site but idle, representing an optimization opportunity.

---

## Vehicle Matching Score

```
Score components (max 100):
  +40  Vehicle status is AVAILABLE or IDLE
  +30  Vehicle capacity ≥ shipment weight
  +20  Vehicle location is in same region as shipment origin
  +10  Vehicle carrier matches shipment carrier
```

---

## What-If Simulation Model

```
Cascade model (deterministic, no random values):
  cascade_factor = min(duration_days, 7) / 7
  extra_affected = floor(remaining_shipments × cascade_factor × 0.4)
  extra_high_risk = floor(extra_affected × 0.6)
  total_impact   = base_impact + (extra_affected × $15,000/day × duration_days)

Values are capped at the total shipment count — no fabrication.
```

---

## Integration with Other Modules

| Module | Integration |
|---|---|
| **Member 1** (Disruption Engine) | Set `DISRUPTION_API_URL` to consume live disruption/shipment data. Seed data used otherwise. |
| **Member 2** (Frontend) | CORS configured for React/Vite dev ports. Consumes all 4 API endpoints. |
| **Member 3** (AI Copilot) | Exposes `/api/what-if` and `/api/optimize-fleet` for IBM Bob recommendation context. |

---

## Shared API Contract Compliance

- ✅ IDs are strings (`vehicle_id`, `shipment_id`, `route_id`, `carrier_id`, `disruption_id`)
- ✅ Dates use ISO 8601
- ✅ Monetary values are numeric (currency formatting belongs to frontend)
- ✅ Risk levels: `LOW` | `MEDIUM` | `HIGH` | `CRITICAL`
- ✅ Risk scores: 0–39 LOW, 40–69 MEDIUM, 70–89 HIGH, 90–100 CRITICAL
- ✅ All APIs return JSON
- ✅ Consistent JSON structure per endpoint
- ✅ Input validation (Pydantic v2)
- ✅ Graceful empty data handling
- ✅ No secrets in code
- ✅ No hardcoded credentials
- ✅ No fabricated routes or vehicles
- ✅ Deterministic results (no random values)
