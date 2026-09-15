"""
RouteX Backend — FastAPI Application Entry Point.

Wires together routers, exception handlers, CORS middleware,
and triggers data loading on startup.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import disruptions, impact, routes, shipments
from app.config import APP_DESCRIPTION, APP_TITLE, APP_VERSION, CORS_ORIGINS
from app.services.data_loader import get_data_store
from app.utils.errors import RouteXError, general_error_handler, routex_error_handler


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Load CSV data once at startup."""
    get_data_store()
    yield


# ── App instance ──────────────────────────────────────────────────────────────

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception handlers ────────────────────────────────────────────────────────

app.add_exception_handler(RouteXError, routex_error_handler)
app.add_exception_handler(Exception, general_error_handler)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(shipments.router)
app.include_router(disruptions.router)
app.include_router(routes.router)
app.include_router(impact.router)


# ── Health check ──────────────────────────────────────────────────────────────


@app.get("/api/health", tags=["Health"])
def health_check():
    """Health check — returns module status and data counts."""
    store = get_data_store()
    return {
        "status": "healthy",
        "module": "routex-backend",
        "version": APP_VERSION,
        "data_loaded": {
            "shipments": len(store.shipments),
            "disruptions": len(store.disruptions),
            "routes": len(store.routes),
            "carriers": len(store.carriers),
        },
    }
