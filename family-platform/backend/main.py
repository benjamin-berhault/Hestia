from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from sqlalchemy.orm import Session
import logging
import uvicorn
from contextlib import asynccontextmanager

# Import configurations and database
from config import settings
from database import create_tables, get_db

# Import routes
from routes import (
    auth_router,
    users_router,
    profiles_router,
    photos_router,
    matches_router,
    messages_router,
    charters_router,
    admin_router
)

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Family Platform API...")
    try:
        create_tables()
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Family Platform API...")

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    Family-Centered Relationship Platform API
    
    A secure platform for adults seeking committed relationships to start families.
    This platform focuses on meaningful connections based on shared values and family goals.
    
    ## Features
    
    * **User Authentication** - Secure JWT-based authentication with email verification
    * **Profile Management** - Comprehensive profiles with family goals and values
    * **Photo Management** - Secure photo upload and management with MinIO
    * **Smart Matching** - Compatibility-based matching algorithm
    * **Secure Messaging** - End-to-end encrypted conversations
    * **Charter System** - Digital relationship agreement builder
    * **Admin Tools** - Content moderation and user management
    
    ## Security
    
    * JWT tokens with refresh capability
    * Input validation and sanitization
    * CORS protection
    * Rate limiting
    * Content moderation
    """,
    docs_url="/api/docs" if settings.debug else None,
    redoc_url="/api/redoc" if settings.debug else None,
    openapi_url="/api/openapi.json" if settings.debug else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "request_id": str(id(request))
        }
    )

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint to verify API and database connectivity"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "service": settings.app_name,
            "version": settings.app_version,
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "service": settings.app_name,
                "version": settings.app_version,
                "database": "disconnected",
                "error": str(e)
            }
        )

# API Info endpoint
@app.get("/api/info", tags=["API Info"])
async def api_info():
    """Get API information and available endpoints"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Family-Centered Relationship Platform API",
        "features": [
            "User Authentication & Authorization",
            "Profile Management with Family Goals",
            "Photo Upload & Management", 
            "Compatibility-Based Matching",
            "Secure Messaging System",
            "Digital Charter Builder",
            "Admin Moderation Tools"
        ],
        "documentation": "/api/docs" if settings.debug else "Contact admin for documentation",
        "support": "support@familyplatform.com"
    }

# Include all route modules
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(profiles_router, prefix="/api/profiles", tags=["Profiles"])
app.include_router(photos_router, prefix="/api/photos", tags=["Photos"])
app.include_router(matches_router, prefix="/api/matches", tags=["Matches"])
app.include_router(messages_router, prefix="/api/messages", tags=["Messages"])
app.include_router(charters_router, prefix="/api/charters", tags=["Charters"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.app_name,
        version=settings.app_version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )