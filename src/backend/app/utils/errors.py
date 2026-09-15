"""
RouteX Backend — Error Handling.

Custom exception classes and global FastAPI exception handlers.
Stack traces are never leaked to API clients.
"""

from fastapi import Request
from fastapi.responses import JSONResponse


# ── Custom Exceptions ─────────────────────────────────────────────────────────


class RouteXError(Exception):
    """Base exception for all RouteX backend errors."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ResourceNotFoundError(RouteXError):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            message=f"{resource} '{resource_id}' not found",
            status_code=404,
        )


class ValidationError(RouteXError):
    """Raised when input validation fails."""

    def __init__(self, message: str):
        super().__init__(message=message, status_code=422)


class DataLoadError(RouteXError):
    """Raised when CSV data cannot be loaded."""

    def __init__(self, message: str):
        super().__init__(message=message, status_code=500)


# ── FastAPI Exception Handlers ────────────────────────────────────────────────


async def routex_error_handler(request: Request, exc: RouteXError) -> JSONResponse:
    """Handle known RouteX exceptions with clean JSON responses."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "status_code": exc.status_code,
        },
    )


async def general_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler — never leaks stack traces to clients."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "An unexpected error occurred",
            "status_code": 500,
        },
    )
