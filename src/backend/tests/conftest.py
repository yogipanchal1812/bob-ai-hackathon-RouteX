"""Shared test fixtures for the RouteX backend test suite."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Provide a FastAPI TestClient instance."""
    return TestClient(app)
