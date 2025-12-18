"""
AutoList AI - FastAPI Application Entry Point

This is the main FastAPI application that serves as the backend for AutoList AI,
an intelligent product data mapping tool for e-commerce marketplaces.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .auth import router as auth_router
from .api.shopify import router as shopify_router
from .api.products import router as products_router
from .api.analytics import router as analytics_router
from .dependencies import connect_database, close_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler for startup and shutdown events.
    Manages database connections and background workers.
    """
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Initialize MongoDB connection
    try:
        await connect_database()
    except Exception as e:
        print(f"Warning: Could not connect to MongoDB: {e}")
        print("Application will continue but database features may not work.")

    yield

    # Shutdown
    print(f"Shutting down {settings.APP_NAME}")
    await close_database()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Intelligent product data mapping for e-commerce marketplaces",
    lifespan=lifespan,
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Register Routers
# ============================================================================

# Auth routes
app.include_router(auth_router)

# Shopify routes
app.include_router(shopify_router)

# Products routes
app.include_router(products_router)

# Analytics routes
app.include_router(analytics_router)


# ============================================================================
# Root Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - API info."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
    }


# ============================================================================
# Development / Debug Endpoints
# ============================================================================

if settings.DEBUG:
    @app.get("/debug/config")
    async def debug_config():
        """Debug endpoint to view non-sensitive config (dev only)."""
        return {
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "debug": settings.DEBUG,
            "shopify_api_version": settings.SHOPIFY_API_VERSION,
        }
