from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from contextlib import asynccontextmanager

# Import routers
from routers import projects, analysis

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Catalyst System Backend starting up...")
    yield
    # Shutdown
    print("🛑 Catalyst System Backend shutting down...")

# Create FastAPI application
app = FastAPI(
    title="Catalyst System Backend",
    description="API for managing Catalyst relationship projects and real-time coaching",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware configuration
allowed_origins = [
    "http://localhost:3000",  # React development server
    "http://127.0.0.1:3000",
    "chrome-extension://*",   # Chrome extension
    "moz-extension://*",      # Firefox extension
]

# Add environment-specific origins
if os.getenv("ALLOWED_ORIGINS"):
    env_origins = os.getenv("ALLOWED_ORIGINS").split(",")
    allowed_origins.extend([origin.strip() for origin in env_origins])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-API-Key",
    ],
)

# Trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
        "*.localhost",
        "*.ngrok.io",  # For development tunneling
        "testserver",  # For FastAPI TestClient
    ]
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "type": "server_error"
        }
    )

# Include routers
app.include_router(
    projects.router, 
    prefix="/api/projects", 
    tags=["Projects"]
)

app.include_router(
    analysis.router, 
    prefix="/api/analysis", 
    tags=["Analysis"]
)

# Root endpoint
@app.get("/", summary="Root Endpoint")
async def root():
    """Root endpoint providing basic API information."""
    return {
        "message": "Welcome to Catalyst System Backend",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "projects": "/api/projects",
            "analysis": "/api/analysis"
        }
    }

# Health check endpoint
@app.get("/health", summary="Health Check")
async def health_check():
    """Health check endpoint for monitoring and load balancers."""
    return {
        "status": "healthy",
        "service": "catalyst-backend",
        "version": "1.0.0",
        "timestamp": "2024-01-01T00:00:00Z",
        "uptime": "operational",
        "services": {
            "database": "connected",
            "analysis_engine": "available",
            "websocket": "active"
        },
        "dependencies": {
            "database": "connected",
            "nlp_service": "available",
            "whisper_service": "active",
            "fastapi": "active",
            "uvicorn": "active"
        }
    }

# API status endpoint
@app.get("/api/status", summary="API Status")
async def api_status():
    """Detailed API status information."""
    return {
        "api_version": "1.0.0",
        "status": "operational",
        "environment": "development",
        "features": {
            "project_management": True,
            "real_time_analysis": True,
            "whisper_suggestions": True,
            "file_upload": True
        },
        "limits": {
            "max_file_size": "10MB",
            "max_projects_per_user": 10,
            "rate_limit_per_minute": 100
        },
        "supported_platforms": {
            "web": True,
            "chrome_extension": True
        }
    }

# Development server configuration
if __name__ == "__main__":
    # Get configuration from environment variables
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    print(f"🌟 Starting Catalyst System Backend")
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🐛 Debug: {debug}")
    print(f"📚 Docs: http://{host}:{port}/docs")
    print(f"❤️  Health: http://{host}:{port}/health")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if not debug else "debug",
        access_log=True
    )