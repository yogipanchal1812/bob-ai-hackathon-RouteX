"""
RouteX AI Module — Test Configuration and Fixtures.
"""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure src/ and src/backend are in sys.path
_src_dir = Path(__file__).resolve().parent.parent.parent
_backend_dir = _src_dir / "backend"

if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from ai.main import app
from ai.copilot.service import CopilotService
from ai.recommendations.recommendation_service import RecommendationService


@pytest.fixture
def client():
    """FastAPI TestClient for standalone AI module."""
    return TestClient(app)


@pytest.fixture
def copilot_service():
    """Instantiated CopilotService fixture."""
    return CopilotService()


@pytest.fixture
def recommendation_service():
    """Instantiated RecommendationService fixture."""
    return RecommendationService()
