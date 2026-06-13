# placeholder_route_health.py
# api/routes/health.py
#
# GET /health  — Health check endpoint
#
# Used by:
#   - Load balancers (Railway, Render, Docker)
#   - Monitoring tools to verify the API is alive
#   - Frontend to check connectivity before sending chat messages
#
# Response:
#   { "status": "ok", "version": "1.0.0" }
#
# TODO: optionally ping Supabase to verify DB connectivity.

from fastapi import APIRouter

router = APIRouter()

APP_VERSION = "0.1.0"


@router.get("/")
def health_check():
    """Return service health status."""
    return {"status": "ok", "version": APP_VERSION}
