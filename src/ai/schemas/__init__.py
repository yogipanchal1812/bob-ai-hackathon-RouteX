"""
RouteX AI Module — Schemas Package.
"""

from ai.schemas.chat import CopilotRequest, CopilotResponse
from ai.schemas.recommendation import (
    Recommendation,
    RecommendationRequest,
    RecommendationResponse,
)

__all__ = [
    "CopilotRequest",
    "CopilotResponse",
    "Recommendation",
    "RecommendationRequest",
    "RecommendationResponse",
]
