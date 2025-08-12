from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import logging
import time
from datetime import datetime
from dotenv import load_dotenv
from templates import get_api_landing_page

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Log startup information
logger.info(f"Starting TruLedgr API...")
logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
logger.info(f"Port: {os.getenv('PORT', '8000')}")

# Initialize FastAPI app
app = FastAPI(
    title="TruLedgr API",
    description="Backend API for TruLedgr application",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dash.truledgr.app",
        "https://truledgr.app", 
        "http://localhost:3000",  # For local development
        "http://localhost:5173",  # Vite default port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Track startup time for uptime calculation
startup_time = time.time()

@app.on_event("startup")
async def startup_event():
    logger.info("TruLedgr API startup complete - ready to accept requests")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("TruLedgr API shutting down")

# Pydantic models
class HealthCheck(BaseModel):
    status: str
    message: str
    version: str

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None

class User(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    is_active: bool = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

# Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Beautiful landing page for the TruLedgr API"""
    return get_api_landing_page()

@app.get("/api", response_model=HealthCheck) 
async def api_root():
    """JSON API root endpoint"""
    return {
        "status": "healthy",
        "message": "TruLedgr API is running",
        "version": "1.0.0"
    }

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint for monitoring"""
    uptime_seconds = int(time.time() - startup_time)
    uptime_hours = uptime_seconds // 3600
    uptime_minutes = (uptime_seconds % 3600) // 60
    
    return {
        "status": "healthy",
        "message": f"All systems operational (uptime: {uptime_hours}h {uptime_minutes}m)",
        "version": "1.0.0"
    }

@app.get("/api/v1/status")
async def get_system_status():
    """Detailed system status information"""
    uptime_seconds = int(time.time() - startup_time)
    return {
        "status": "operational",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime_seconds": uptime_seconds,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "features": {
            "authentication": "available",
            "mobile_api": "available", 
            "health_monitoring": "active"
        }
    }

# API Routes
@app.post("/api/v1/auth/register", response_model=User)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    # TODO: Implement user registration logic
    return {
        "id": 1,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "is_active": True
    }

@app.post("/api/v1/auth/login", response_model=TokenResponse)
async def login_user(user_data: UserCreate):
    """Authenticate user and return access token"""
    # TODO: Implement authentication logic
    return {
        "access_token": "sample_token_replace_with_real_jwt",
        "token_type": "bearer"
    }

@app.get("/api/v1/users/me", response_model=User)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    # TODO: Implement JWT token validation and user retrieval
    return {
        "id": 1,
        "email": "user@example.com",
        "full_name": "Sample User",
        "is_active": True
    }

# Mobile-specific endpoints
@app.get("/api/v1/mobile/config")
async def get_mobile_config():
    """Configuration endpoint for mobile apps"""
    return {
        "api_version": "1.0.0",
        "min_app_version": "1.0.0",
        "force_update": False,
        "maintenance_mode": False,
        "features": {
            "biometric_auth": True,
            "push_notifications": True,
            "offline_mode": True
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    environment = os.getenv("ENVIRONMENT", "development")
    
    logger.info(f"Starting server on 0.0.0.0:{port}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=environment == "development",
        log_level="info",
        access_log=True
    )
