"""
FastAPI application entry point for AI Bias Psychologist.

This module creates and configures the FastAPI application with all routes,
middleware, and static file serving for the real-time dashboard.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from .api import probes_router, dashboard_router, reports_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="AI Bias Psychologist",
        description="A diagnostic tool for detecting cognitive biases in LLMs",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routers
    app.include_router(probes_router, prefix="/api/v1/probes", tags=["probes"])
    app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["dashboard"])
    app.include_router(reports_router, prefix="/api/v1/reports", tags=["reports"])
    
    # Mount static files
    app.mount("/static", StaticFiles(directory="src/ai_bias_psych/web/static"), name="static")
    
    # Configure templates
    templates = Jinja2Templates(directory="src/ai_bias_psych/web/templates")
    
    @app.get("/")
    async def root():
        """Root endpoint - redirect to dashboard."""
        return {"message": "AI Bias Psychologist API", "dashboard": "/dashboard"}
    
    @app.get("/dashboard")
    async def dashboard():
        """Dashboard endpoint - serve the main dashboard."""
        return templates.TemplateResponse("dashboard.html", {"request": {}})
    
    return app


# For development server
if __name__ == "__main__":
    import uvicorn
    
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
