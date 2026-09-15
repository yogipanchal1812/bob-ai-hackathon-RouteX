"""
RouteX Backend — Application Configuration.

Loads settings from environment variables with sensible defaults.
"""

import os
from pathlib import Path

# ── Directory paths ───────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# ── Application metadata ─────────────────────────────────────────────────────

APP_TITLE = "RouteX Backend API"
APP_DESCRIPTION = (
    "ChainGuard AI — Supply Chain Disruption Intelligence & Risk Engine"
)
APP_VERSION = "1.0.0"

# ── Server settings ──────────────────────────────────────────────────────────

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("APP_PORT", "8000"))

# ── CORS ──────────────────────────────────────────────────────────────────────

CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS", "http://localhost:3000,http://localhost:5173"
).split(",")
