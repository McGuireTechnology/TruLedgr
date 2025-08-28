"""
FastAPI application factory and main router configuration.

This module creates the FastAPI application instance and includes
all module routers with proper prefixes and tags.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
from sqlalchemy import text

from api.settings import get_settings
from api.db import engine, create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events including:
    - Database table creation
    - Background task management
    - Resource cleanup
    """
    settings = get_settings()
    
    # Startup
    print("🚀 Starting FastAPI Security Sample v2.0...")
    
    # Create database tables
    await create_tables(engine)
    print("✅ Database tables created/verified")
    
    # Seed database if in development
    if settings.is_development:
        try:
            from api.db.seed import seed_database
            await seed_database()
            print("✅ Database seeded with default data")
        except Exception as e:
            print(f"⚠️ Database seeding failed: {e}")

    print("✅ Startup complete")
    
    # Yield control to the application
    yield
    
    # Shutdown
    print("🛑 Shutting down FastAPI Security Sample...")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured application instance
    """
    settings = get_settings()
    
    # Create FastAPI app with configuration
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan
    )

    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods_list,
        allow_headers=settings.cors_allow_headers_list,
    )
    
    # Include routers
    include_routers(app)
    
    # Add health check endpoints
    add_health_endpoints(app)
    
    return app





def include_routers(app: FastAPI):
    """Include all module routers with proper prefixes and tags."""
    
    # Root endpoint
    @app.get("/", tags=["Root"])
    def root():
        """Welcome endpoint with API information."""
        return {
            "message": "Welcome to FastAPI Security Sample v2.0!",
            "version": "2.0.0",
            "architecture": "modular",
            "docs": "/docs",
            "health": "/health"
        }
    
    # Include module routers
    try:
        from api.authentication.router import router as authentication_router
        app.include_router(authentication_router)
    except ImportError:
        print("⚠️ Auth router not available")
    
    try:
        from api.users.router import router as users_router
        app.include_router(users_router)
    except ImportError:
        print("⚠️ Users router not available")
    
    try:
        from api.groups.router import router as groups_router
        app.include_router(groups_router)
    except ImportError:
        print("⚠️ Groups router not available")
    
    try:
        from api.authorization.router import router as authorization_router
        app.include_router(authorization_router)
    except ImportError:
        print("⚠️ Authorization router not available")
    
    try:
        from api.items.router import router as items_router
        app.include_router(items_router)
    except ImportError:
        print("⚠️ Items router not available")
    
    try:
        from api.activities.router import router as activities_router
        app.include_router(activities_router)
    except ImportError:
        print("⚠️ Activities router not available")



def add_health_endpoints(app: FastAPI):
    """Add health check endpoints."""
    
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Basic health check endpoint."""
        try:
            # Test database connection
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            
            db_status = "healthy"
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"
        
        return JSONResponse(
            status_code=200 if db_status == "healthy" else 503,
            content={
                "status": "healthy" if db_status == "healthy" else "unhealthy",
                "app_name": "FastAPI Security Sample",
                "version": "2.0.0",
                "architecture": "modular",
                "database": db_status,
                "checks": {
                    "database_connection": db_status == "healthy",
                    "configuration_loaded": True,
                }
            }
        )
    
    @app.get("/ready", tags=["Health"])
    async def readiness_check():
        """Kubernetes readiness probe."""
        try:
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            
            return JSONResponse(
                status_code=200,
                content={
                    "status": "ready",
                    "checks": {
                        "database": True,
                        "configuration": True
                    }
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "not_ready",
                    "error": str(e)
                }
            )


# Create the application instance
app = create_app()

# For compatibility with uvicorn main:app
if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        workers=settings.workers if not settings.reload else 1
    )
