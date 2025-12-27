"""FastAPI application configuration and middleware setup."""

import logging
import os
import sys

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1 import databases, exports, queries

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")

# Create FastAPI app
app = FastAPI(
    title="Database Query Tool API",
    description="REST API for PostgreSQL database connection management, schema browsing, and query execution",
    version="1.0.0",
)

logger.info("FastAPI application initialized")

# Configure CORS middleware
cors_origins_env = os.getenv("CORS_ORIGINS", "")
if cors_origins_env:
    cors_origins = cors_origins_env.split(",")
else:
    # Default: allow localhost for development
    cors_origins = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative dev port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"CORS enabled for origins: {cors_origins}")

# Register API routers
app.include_router(databases.router, prefix="/api/v1")
app.include_router(queries.router, prefix="/api/v1")
app.include_router(exports.router, prefix="/api/v1")

logger.info("API routers registered")


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint returning API information."""
    return {
        "name": "Database Query Tool API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health() -> dict[str, str | bool]:
    """
    Health check endpoint.
    
    Checks:
    - API service status
    - SQLite database connectivity
    
    Returns:
        dict: Health status with component checks
    """
    from src.services.storage import get_connection
    
    health_status = {
        "status": "healthy",
        "service": "Database Query Tool API",
        "database": False,
    }
    
    # Check SQLite database connection
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            health_status["database"] = True
    except Exception:
        health_status["status"] = "degraded"
        health_status["database"] = False
    
    return health_status


@app.get("/api/v1/health")
async def api_health() -> dict[str, str | bool]:
    """API v1 health check endpoint (alias for /health)."""
    return await health()

