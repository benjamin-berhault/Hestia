from fastapi import FastAPI, Request, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
import time
import uuid
import logging
import structlog
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import redis.asyncio as redis
from sqlalchemy.orm import Session
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

# Import configurations and services
from config import settings
from database import db_manager, get_db
from routes import auth, users, profiles, photos, matches, messages, charters, admin, payments, analytics
from services import NotificationService, AIService, AnalyticsService, SafetyService
from utils.rate_limiter import RateLimiter
from utils.security import SecurityHeaders
from utils.health_check import HealthChecker

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer() if settings.environment == "production" else structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Initialize Sentry for error tracking
if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        integrations=[
            FastApiIntegration(auto_enabling=True),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.1,
        environment=settings.environment,
        release=settings.app_version,
    )

# Prometheus metrics
REQUEST_COUNT = Counter('family_platform_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('family_platform_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
ACTIVE_USERS = Counter('family_platform_active_users_total', 'Active users')
MATCHES_CREATED = Counter('family_platform_matches_created_total', 'Matches created')
MESSAGES_SENT = Counter('family_platform_messages_sent_total', 'Messages sent')

# Global services instances
notification_service = NotificationService()
ai_service = AIService()
analytics_service = AnalyticsService()
safety_service = SafetyService()
health_checker = HealthChecker()
rate_limiter = RateLimiter()
security_headers = SecurityHeaders()

# Redis connection
redis_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Family Platform API", version=settings.app_version, environment=settings.environment)
    
    try:
        # Initialize database
        db_manager.create_tables()
        logger.info("Database tables created/verified")
        
        # Initialize Redis connection
        global redis_client
        redis_client = redis.from_url(settings.redis_url)
        await redis_client.ping()
        logger.info("Redis connection established")
        
        # Initialize services
        await notification_service.initialize()
        await analytics_service.initialize()
        logger.info("Services initialized")
        
        # Perform health checks
        health_status = await health_checker.comprehensive_health_check()
        if not health_status["healthy"]:
            logger.error("Health check failed", status=health_status)
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error("Application startup failed", error=str(e), exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Family Platform API")
    
    try:
        if redis_client:
            await redis_client.close()
        logger.info("Application shutdown completed")
    except Exception as e:
        logger.error("Error during shutdown", error=str(e))

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    openapi_url="/api/v1/openapi.json" if settings.debug else None,
    docs_url="/api/v1/docs" if settings.debug else None,
    redoc_url="/api/v1/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Custom middleware for request tracking and analytics
class RequestTrackingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Add request ID to context
        request.state.request_id = request_id
        
        # Process request
        with structlog.contextvars.bound_contextvars(request_id=request_id):
            try:
                response = await call_next(request)
                
                # Calculate metrics
                duration = time.time() - start_time
                
                # Update Prometheus metrics
                REQUEST_COUNT.labels(
                    method=request.method,
                    endpoint=request.url.path,
                    status=response.status_code
                ).inc()
                
                REQUEST_DURATION.labels(
                    method=request.method,
                    endpoint=request.url.path
                ).observe(duration)
                
                # Log request
                logger.info(
                    "Request completed",
                    method=request.method,
                    url=str(request.url),
                    status_code=response.status_code,
                    duration=duration,
                    user_agent=request.headers.get("user-agent"),
                    client_ip=request.client.host
                )
                
                # Add security headers
                response = security_headers.add_security_headers(response)
                response.headers["X-Request-ID"] = request_id
                
                return response
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    "Request failed",
                    method=request.method,
                    url=str(request.url),
                    duration=duration,
                    error=str(e),
                    exc_info=True
                )
                
                # Track error metrics
                REQUEST_COUNT.labels(
                    method=request.method,
                    endpoint=request.url.path,
                    status=500
                ).inc()
                
                raise

# Rate limiting middleware
class RateLimitingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if settings.rate_limit_enabled:
            client_ip = request.client.host
            endpoint = request.url.path
            
            # Check rate limit
            is_allowed = await rate_limiter.check_rate_limit(
                client_ip, 
                endpoint,
                settings.rate_limit_requests_per_minute
            )
            
            if not is_allowed:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "message": "Too many requests. Please try again later."
                    }
                )
        
        return await call_next(request)

# Add middleware (order matters!)
app.add_middleware(RateLimitingMiddleware)
app.add_middleware(RequestTrackingMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts if settings.environment == "production" else ["*"]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"]
)

# Include API routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(profiles.router, prefix="/api/v1/profiles", tags=["Profiles"])
app.include_router(photos.router, prefix="/api/v1/photos", tags=["Photos"])
app.include_router(matches.router, prefix="/api/v1/matches", tags=["Matching"])
app.include_router(messages.router, prefix="/api/v1/messages", tags=["Messaging"])
app.include_router(charters.router, prefix="/api/v1/charters", tags=["Charters"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Administration"])

# Health check endpoints
@app.get("/health", include_in_schema=False)
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/health/detailed", include_in_schema=False)
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with dependencies"""
    try:
        health_status = await health_checker.comprehensive_health_check(db)
        status_code = 200 if health_status["healthy"] else 503
        return JSONResponse(content=health_status, status_code=status_code)
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return JSONResponse(
            content={"healthy": False, "error": str(e)},
            status_code=503
        )

# Metrics endpoint for Prometheus
@app.get("/metrics", include_in_schema=False)
async def metrics():
    """Prometheus metrics endpoint"""
    if not settings.prometheus_enabled:
        raise HTTPException(status_code=404, detail="Metrics not enabled")
    
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": settings.app_description,
        "environment": settings.environment,
        "docs_url": "/api/v1/docs" if settings.debug else None,
        "status": "operational"
    }

# API Info endpoint
@app.get("/api/v1/info")
async def api_info():
    """API information and status"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "features": {
            "ai_matching": settings.ai_matching_enabled,
            "video_calls": True,
            "real_time_messaging": True,
            "digital_charters": settings.charter_templates_enabled,
            "premium_features": settings.premium_features_enabled,
            "background_checks": settings.background_check_integration,
            "content_moderation": settings.auto_moderation_enabled
        },
        "limits": {
            "free_daily_matches": settings.max_daily_matches,
            "premium_daily_matches": settings.premium_max_daily_matches,
            "max_photos": settings.max_photos_per_user,
            "max_message_length": settings.max_message_length
        }
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.error(
        "Unhandled exception",
        request_id=request_id,
        url=str(request.url),
        error=str(exc),
        exc_info=True
    )
    
    if settings.environment == "production":
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "request_id": request_id,
                "message": "An unexpected error occurred. Please try again later."
            }
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "request_id": request_id,
                "message": str(exc),
                "type": type(exc).__name__
            }
        )

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.app_name,
        version=settings.app_version,
        description=settings.app_description,
        routes=app.routes,
    )
    
    # Add custom security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    # Add global security requirement
    openapi_schema["security"] = [{"BearerAuth": []}]
    
    # Add custom info
    openapi_schema["info"]["contact"] = {
        "name": "Family Platform Support",
        "email": "support@familyplatform.com"
    }
    
    openapi_schema["info"]["license"] = {
        "name": "Proprietary",
        "url": "https://familyplatform.com/license"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Background task for analytics
async def background_analytics_task():
    """Background task for processing analytics"""
    try:
        await analytics_service.process_daily_metrics()
        logger.info("Daily analytics processed successfully")
    except Exception as e:
        logger.error("Analytics processing failed", error=str(e))

# Startup event for background tasks
@app.on_event("startup")
async def startup_background_tasks():
    """Start background tasks"""
    try:
        # Schedule daily analytics processing
        import asyncio
        asyncio.create_task(analytics_service.start_background_processing())
        logger.info("Background tasks started")
    except Exception as e:
        logger.error("Failed to start background tasks", error=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True
    )