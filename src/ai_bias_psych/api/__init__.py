"""
FastAPI routes and endpoints for AI Bias Psychologist.

This module provides REST API endpoints for:
- Probe execution
- Dashboard data
- Report generation
"""

from .probes import router as probes_router
from .dashboard import router as dashboard_router
from .reports import router as reports_router

__all__ = [
    "probes_router",
    "dashboard_router", 
    "reports_router",
]
