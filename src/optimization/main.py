"""
main.py — FastAPI application entrypoint for Module 4: Fleet & Simulation.

RouteX / ChainGuard AI — Member 4 (Optimization Module)

Exposes:
    GET  /api/fleet              — List all fleet vehicles
    GET  /api/fleet/utilization  — Fleet utilization report
    POST /api/optimize-fleet     — Vehicle matching for affected shipments
    POST /api/what-if            — What-if disruption scenario simulation
    GET  /health                 — Health check (for integration testing)
    GET  /                       — Module info

To run:
    cd src/optimization
    uvicorn main:app --reload --port 8001

To run tests:
    cd src/optimization
    pytest tests/ -v
"""

import logging
import logging.config
import os
import sys
from contextlib import asynccontextmanager

# Add the parent of 'optimization' (i.e., src/) to sys.path so that
# 'from optimization.xxx import yyy' works whether started from repo root,
# src/, or src/optimization/.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from optimization.api.fleet_router import router as fleet_router
from optimization.api.simulation_router import router as simulation_router
from optimization.config import settings

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=getattr(logging, settings.log_level, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("optimization.main")


# ---------------------------------------------------------------------------
# App lifecycle
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Log startup configuration on boot."""
    logger.info("=== RouteX Module 4 — Fleet & Simulation Engine ===")
    logger.info("Environment : %s", settings.app_env)
    logger.info("Port        : %d", settings.port)
    logger.info("Data mode   : %s", "SEED DATA (dev)" if settings.use_seed_data else "LIVE API")
    if not settings.use_seed_data:
        logger.info("Disruption API: %s", settings.disruption_api_url)
    logger.info("CORS origins: %s", settings.cors_origins)
    yield
    logger.info("=== Module 4 shutting down ===")


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="RouteX — Fleet & Simulation API",
    description=(
        "Module 4: Fleet Utilization, Rerouting Support, and What-If Simulation. "
        "Part of the RouteX / ChainGuard AI supply chain risk platform.\n\n"
        "**Member 4** | Bob AI Hackathon\n\n"
        "Endpoints:\n"
        "- `GET /api/fleet` — All fleet vehicles\n"
        "- `GET /api/fleet/utilization` — Utilization metrics\n"
        "- `POST /api/optimize-fleet` — Vehicle-to-shipment matching\n"
        "- `POST /api/what-if` — Disruption scenario simulation\n"
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS — allow Member 2's frontend (React/Vite) to call this API
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(fleet_router)
app.include_router(simulation_router)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["health"], summary="Health check")
def health_check() -> JSONResponse:
    """
    GET /health

    Used by integration tests and deployment checks.
    Returns HTTP 200 when the service is running.
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "module": "Module 4 — Fleet & Simulation",
            "version": "1.0.0",
            "data_mode": "seed" if settings.use_seed_data else "live",
        },
    )


# ---------------------------------------------------------------------------
# Root info
# ---------------------------------------------------------------------------
@app.get("/", tags=["info"], summary="Module info", include_in_schema=False)
def root() -> JSONResponse:
    return JSONResponse(
        content={
            "module": "RouteX Module 4 — Fleet Utilization & What-If Simulation",
            "member": "Member 4",
            "endpoints": [
                "GET  /api/fleet",
                "GET  /api/fleet/utilization",
                "POST /api/optimize-fleet",
                "POST /api/what-if",
                "GET  /health",
                "GET  /docs",
            ],
        }
    )
