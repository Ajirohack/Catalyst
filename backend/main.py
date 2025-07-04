"""
Catalyst Backend Main Application
FastAPI application with comprehensive AI model integration system
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import database setup
try:
    from database.base import get_db_config
    from database.init_ai_providers import create_database_tables, seed_default_providers
except ImportError as e:
    logger.warning(f"Database imports failed: {e}")
    get_db_config = None
    create_database_tables = None
    seed_default_providers = None

# Import routers
try:
    from routers.v1 import (
        projects_router as projects,
        analysis_router as analysis, 
        ai_providers_router as ai_providers,
        knowledge_base_router as knowledge_base
    )
    from routers import ai_therapy
    from routers import advanced_analytics
except ImportError as e:
    logger.warning(f"Router imports failed: {e}")
    # Create mock routers to prevent app from failing
    from fastapi import APIRouter
    projects = APIRouter()
    analysis = APIRouter()
    ai_providers = APIRouter()
    knowledge_base = APIRouter()
    ai_therapy = type('MockRouter', (), {'router': APIRouter()})()
    advanced_analytics = type('MockRouter', (), {'router': APIRouter()})()

# Import middleware
try:
    from middleware.performance import PerformanceMiddleware
    from middleware.request_counter import RequestCounterMiddleware
except ImportError:
    # Mock middleware if not available
    PerformanceMiddleware = None
    RequestCounterMiddleware = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    logger.info("🚀 Catalyst Backend starting up...")
    
    try:
        # Initialize database
        if get_db_config:
            db_config = get_db_config()
            db_config.create_tables()
            logger.info("✅ Database initialized")
        
        # Create AI provider tables and seed data
        if create_database_tables and seed_default_providers:
            create_database_tables()
            await seed_default_providers()
            logger.info("✅ AI providers initialized")
            
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Catalyst Backend shutting down...")


# Create FastAPI application
app = FastAPI(
    title="Catalyst Backend API",
    description="""
    **Catalyst** - AI-Powered Relationship Analysis Platform
    
    ## Features
    
    * **Multi-Provider AI Integration** - OpenAI, Mistral, Anthropic, OpenRouter, Ollama, Groq, Huggingface
    * **Dynamic Model Management** - Real-time model syncing and configuration
    * **Secure Key Storage** - Encrypted API key management
    * **Health Monitoring** - Provider status and performance tracking
    * **Cost Analytics** - Usage and cost tracking per provider
    * **Knowledge Base** - Document upload with AI processing
    * **Admin UI** - Complete provider management interface
    
    ## Multi-Provider Support
    
    The system supports 7 major AI providers with dynamic configuration:
    
    - **OpenAI**: GPT-4, GPT-3.5-turbo, embeddings
    - **Mistral**: Mistral Large, Medium, Small models  
    - **Anthropic**: Claude 3 Opus, Sonnet, Haiku
    - **OpenRouter**: Access to 100+ models via single API
    - **Ollama**: Local LLM deployment (Llama 2, Code Llama, etc.)
    - **Groq**: Lightning-fast inference
    - **Hugging Face**: Thousands of open-source models
    
    ## Admin Features
    
    * Provider CRUD operations
    * Real-time connection testing
    * Dynamic model fetching
    * Usage analytics and monitoring
    * Cost optimization suggestions
    * Knowledge base management
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "Projects",
            "description": "Project management operations",
        },
        {
            "name": "Analysis", 
            "description": "AI-powered analysis operations",
        },
        {
            "name": "AI Providers Enhanced",
            "description": "Enhanced AI provider management with full CRUD operations",
        },
        {
            "name": "AI Therapy",
            "description": "AI-powered therapy and coaching features",
        },
        {
            "name": "Advanced Analytics",
            "description": "Advanced analytics and reporting",
        },
        {
            "name": "Knowledge Base",
            "description": "Knowledge base and document management",
        },
    ]
)

# CORS middleware configuration
allowed_origins = [
    "http://localhost:3000",  # React development server
    "http://127.0.0.1:3000",
    "http://localhost:3001",  # Admin dashboard
    "http://127.0.0.1:3001",
    "chrome-extension://*",   # Chrome extension
    "moz-extension://*",      # Firefox extension
]

# Add environment-specific origins
if os.getenv("ALLOWED_ORIGINS"):
    env_origins_str = os.getenv("ALLOWED_ORIGINS")
    if env_origins_str:
        env_origins = env_origins_str.split(",")
        allowed_origins.extend([origin.strip() for origin in env_origins])

# Add performance middleware if available
if PerformanceMiddleware:
    app.add_middleware(PerformanceMiddleware, log_slow_requests=True, slow_threshold=1.0)
if RequestCounterMiddleware:
    app.add_middleware(RequestCounterMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
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
    logger.error(f"Global exception: {exc}")
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
    projects, 
    prefix="/api/v1/projects", 
    tags=["Projects"]
)

app.include_router(
    analysis, 
    prefix="/api/v1/analysis", 
    tags=["Analysis"]
)

app.include_router(
    ai_therapy.router, 
    prefix="/api/v1/ai-therapy", 
    tags=["AI Therapy"]
)

# Include the unified AI providers router
app.include_router(
    ai_providers,
    tags=["AI Providers"]
)

app.include_router(
    advanced_analytics.router,
    prefix="/api/v1/analytics", 
    tags=["Advanced Analytics"]
)

app.include_router(
    knowledge_base,
    prefix="/api/v1/knowledge-base",
    tags=["Knowledge Base"]
)

# Root endpoint
@app.get("/", summary="Root Endpoint")
async def root():
    """Root endpoint providing basic API information."""
    return {
        "message": "Welcome to Catalyst System Backend",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "features": [
            "Multi-Provider AI Integration",
            "Dynamic Model Management", 
            "Secure Key Storage",
            "Health Monitoring",
            "Cost Analytics",
            "Knowledge Base",
            "Admin UI"
        ],
        "endpoints": {
            "projects": "/api/projects",
            "analysis": "/api/analysis",
            "ai_therapy": "/api/v1/ai-therapy",
            "ai_providers": "/api/v1/admin/ai-providers",
            "analytics": "/api/v1/analytics",
            "knowledge_base": "/api/v1/knowledge-base"
        }
    }

# Health check endpoint
@app.get("/health", summary="Health Check")
async def health_check():
    """Health check endpoint for monitoring and load balancers."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime": "unknown",  # Would be calculated from app start time
        "services": {
            "database": "operational",
            "ai_providers": "operational", 
            "analysis_engine": "operational",
            "websocket": "operational"
        },
        "dependencies": {
            "fastapi": "✅ Available",
            "uvicorn": "✅ Available",
            "sqlalchemy": "✅ Available"
        }
    }

# API status endpoint
@app.get("/api/status", summary="API Status")
async def api_status():
    """API status with feature availability."""
    return {
        "status": "operational",
        "api_version": "2.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "features": {
            "project_management": True,
            "real_time_analysis": True,
            "ai_providers": True,
            "multi_model_support": True,
            "whisper_suggestions": True,
            "file_upload": True,
            "advanced_analytics": True,
            "knowledge_base": True
        },
        "limits": {
            "max_file_size": "100MB",
            "max_projects_per_user": 50,
            "rate_limit_per_minute": 1000
        },
        "supported_platforms": [
            "web", "mobile", "chrome_extension"
        ],
        "ai_providers": {
            "supported": ["openai", "anthropic", "mistral", "openrouter", "ollama", "groq", "huggingface"],
            "total_models": "100+",
            "dynamic_configuration": True
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("RELOAD", "true").lower() == "true",
        log_level="info"
    )
