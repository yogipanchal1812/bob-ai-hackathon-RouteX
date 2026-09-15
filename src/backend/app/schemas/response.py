"""RouteX Backend — Shared API response wrappers."""

from typing import Any, Optional
from pydantic import BaseModel


class APIResponse(BaseModel):
    """Standard API success response wrapper."""

    success: bool
    data: Any
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response body."""

    error: str
    status_code: int
