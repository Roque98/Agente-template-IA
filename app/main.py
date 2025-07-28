from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time

from app.api.router import api_router
from app.core.config import settings
from app.core.database import engine
from app.models import *  # Import all models to ensure they are registered
from app.services.config_service import config_service

# Create database tables
from app.core.database import Base
Base.metadata.create_all(bind=engine)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="A complete configurable agent system with LangChain integration",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Start configuration hot reload if enabled
@app.on_event("startup")
async def startup_event():
    if config_service.is_hot_reload_enabled():
        config_service.start_hot_reload()

@app.on_event("shutdown")
async def shutdown_event():
    config_service.stop_hot_reload()

# Health check endpoint
@app.get("/health")
@limiter.limit("30/minute")
async def health_check(request: Request):
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
@limiter.limit("10/minute")
async def root(request: Request):
    return {
        "message": "Agent System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )