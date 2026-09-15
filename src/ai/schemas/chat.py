"""
RouteX AI Module — Chat & Copilot Schemas.

Defines the request and response shapes for POST /api/copilot.
Provides backwards compatibility with both frontend payload shapes
and strict API contract specifications.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator

from ai.schemas.recommendation import Recommendation


class CopilotRequest(BaseModel):
    """
    Request body for POST /api/copilot.
    Accepts either 'question' (official spec) or 'message' (frontend UI).
    """

    question: Optional[str] = Field(None, description="Natural language query from operator")
    message: Optional[str] = Field(None, description="Alias for question used by UI")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional extra context (e.g. what-if scenario)")

    @model_validator(mode="after")
    def validate_and_normalize(self):
        query = (self.question or self.message or "").strip()
        if not query:
            raise ValueError("Query string cannot be empty. Provide 'question' or 'message'.")
        self.question = query
        self.message = query
        return self


class CopilotData(BaseModel):
    """Structured copilot output payload."""

    answer: str = Field(..., description="Explainable answer grounded in factual RouteX data")
    response: str = Field(..., description="Mirror of answer for frontend UI compatibility")
    sources: List[str] = Field(default_factory=list, description="List of source entity IDs referenced")
    recommendations: List[Recommendation] = Field(default_factory=list, description="Structured operational actions")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Estimated response confidence")
    engine: str = Field(default="routex_decision_engine", description="Active processing engine (ibm_bob or routex_decision_engine)")


class CopilotResponse(BaseModel):
    """
    Top-level response envelope.
    Includes both nested 'data' and direct top-level fields for maximum consumer compatibility.
    """

    success: bool = True
    data: CopilotData
    answer: str
    sources: List[str]
    recommendations: List[Recommendation]
