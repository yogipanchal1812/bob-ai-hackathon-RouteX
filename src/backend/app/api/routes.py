"""RouteX Backend — Route API endpoints."""

from fastapi import APIRouter

from app.services.data_loader import get_data_store

router = APIRouter(prefix="/api", tags=["Routes"])


@router.get("/routes")
def list_routes():
    """Return all shipping routes."""
    store = get_data_store()
    routes = list(store.routes.values())
    return {
        "success": True,
        "count": len(routes),
        "data": [r.__dict__ for r in routes],
    }
