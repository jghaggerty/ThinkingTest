from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.routers import evaluations, heuristics, baselines, recommendations

# Initialize database tables on startup
init_db()

# Create FastAPI app
app = FastAPI(
    title="AI Bias & Heuristics Diagnostic Tool API",
    description="RESTful API for detecting and analyzing heuristic biases in AI systems",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(evaluations.router)
app.include_router(heuristics.router)
app.include_router(baselines.router)
app.include_router(recommendations.router)


@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "name": "AI Bias & Heuristics Diagnostic Tool API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "operational",
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": "2025-11-25T00:00:00Z"}


# Global exception handler for consistent error responses
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle uncaught exceptions with consistent error format."""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": str(exc) if settings.database_url != "sqlite:///./bias_tool.db" else None,
            }
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
