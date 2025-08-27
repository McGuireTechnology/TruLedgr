"""
Authentication API endpoints.

This module provides the main authentication router that includes:
- Core authentication (login, logout, register)
- User information endpoints
- Health checks
- Submodule routers for passwords, TOTP, sessions, and OAuth2
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, OAuth2PasswordRequestForm, HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession

from api.db.session import get_async_session
from api.authentication.deps import get_current_user
from api.users.models import User
from .service import AuthenticationService
from .schemas import LoginRequest, LogoutRequest

# Import submodule routers
from .passwords import router as passwords_router
from .totp import router as totp_router
from .sessions import router as sessions_router
from .oauth2 import router as oauth2_router

# Initialize router and services
router = APIRouter()
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer(auto_error=False)
auth_service = AuthenticationService()




def _get_client_ip(request: Request) -> str:
    """Extract client IP from request."""
    # Check for forwarded headers
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Fallback to direct connection
    if request.client:
        return request.client.host
    
    return "unknown"


def _get_user_agent(request: Request) -> str:
    """Extract user agent from request."""
    return request.headers.get("User-Agent", "unknown")


# Core Authentication Endpoints

@auth_router.post("/register", response_model=dict)
async def register(
    user_data: dict,
    request: Request,
    session: AsyncSession = Depends(get_async_session)
):
    """
    User registration endpoint.
    
    Creates a new user account and returns success message.
    """
    try:
        from api.users.schemas import UserCreate
        from api.users.service import create_user_with_validation
        
        # Create user from registration data
        user_create = UserCreate(**user_data)
        new_user = await create_user_with_validation(session, user_create)
        
        return {
            "message": "Registration successful",
            "user_id": new_user.id,
            "username": new_user.username,
            "email": new_user.email
        }
        
    except Exception as e:
        if "already exists" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists"
            )
        elif "validation" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed"
            )


@auth_router.post("/test-auth", response_model=dict)
async def test_auth(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Test authentication without full login flow.
    """
    try:
        from api.users.service import get_user_by_username, get_user_by_email
        from api.authentication.utils.password import verify_password
        
        # Step 1: Try to find user by username
        user = await get_user_by_username(session, form_data.username)
        user_source = "username"
        
        if not user:
            # Step 2: Try to find user by email
            user = await get_user_by_email(session, form_data.username)
            user_source = "email"
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User not found by {user_source}"
            )
        
        # Step 3: Check user status
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is inactive"
            )
        
        if user.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is deleted"
            )
        
        # Step 4: Verify password
        if not user.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User has no password set"
            )
        
        # Debug the exact values
        password_valid = verify_password(form_data.password, user.hashed_password)
        
        return {
            "user_found": True,
            "user_source": user_source,
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "is_deleted": user.is_deleted,
            "has_password": bool(user.hashed_password),
            "password_valid": password_valid,
            "totp_enabled": user.totp_enabled
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication test failed: {str(e)}"
        )


@auth_router.post("/login", response_model=dict)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session)
):
    """
    User login endpoint.
    
    Accepts username/email and password, returns access token.
    """
    try:
        client_ip = _get_client_ip(request)
        user_agent = _get_user_agent(request)
        
        # Create login request
        login_request = LoginRequest(
            username=form_data.username,
            password=form_data.password,
            totp_code=getattr(form_data, 'totp_code', None),
            remember_me=False
        )
        
        # Authenticate user
        result = await auth_service.authenticate_user(
            session, login_request, client_ip, user_agent
        )
        
        if "error" in result:
            if result["error"] == "account_locked":
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail={
                        "message": result["message"],
                        "seconds_remaining": result.get("seconds_remaining")
                    }
                )
            elif result["error"] == "totp_required":
                raise HTTPException(
                    status_code=status.HTTP_428_PRECONDITION_REQUIRED,
                    detail={
                        "message": result["message"],
                        "totp_required": True
                    }
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=result["message"]
                )
        
        return {
            "access_token": result["access_token"],  # Now using JWT token
            "token_type": "bearer",
            "expires_in": 3600,  # 1 hour
            "user": {
                "id": result["user_id"],
                "username": result["username"],
                "email": result["email"]
            },
            "session_id": result["session_id"],
            "totp_enabled": result["totp_enabled"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@auth_router.post("/logout")
async def logout(
    logout_data: LogoutRequest = LogoutRequest(all_sessions=False),
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Logout user by revoking session(s).
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    result = await auth_service.logout_user(
        session, credentials.credentials, logout_data.all_sessions
    )
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return {"message": result["message"]}


@auth_router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information.
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "email_verified": current_user.email_verified,
        "totp_enabled": current_user.totp_enabled,
        "last_login": current_user.last_login,
        "created_at": current_user.created_at
    }


# Health Check Endpoint

@auth_router.get("/health")
async def auth_health_check():
    """
    Authentication service health check.
    """
    return {
        "status": "healthy",
        "service": "authentication",
        "timestamp": "2025-08-25T00:00:00Z"
    }


# Include submodule routers
router.include_router(auth_router)
router.include_router(oauth2_router)
router.include_router(passwords_router)
router.include_router(sessions_router)
router.include_router(totp_router)