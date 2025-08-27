"""
Refined Authentication Module

This module provides comprehensive authentication functionality organized into submodules:
- oauth2: OAuth2 social login with Google, Microsoft, Apple
- passwords: Password management, reset, and validation
- sessions: Session management and tracking
- totp: Time-based One-Time Password (2FA) implementation

The module is designed for:
- Security best practices
- Modular architecture
- Easy configuration
- Comprehensive logging
- Rate limiting protection
"""

# Import schemas
from .schemas import (
    LoginRequest,
    LoginResponse,
    TokenRequest,
    TokenResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordChangeRequest,
    TOTPSetupRequest,
    TOTPSetupResponse,
    TOTPVerifyRequest,
    TOTPDisableRequest,
    OAuth2AuthorizeRequest,
    OAuth2CallbackRequest,
    OAuth2LinkRequest,
    SessionInfo,
    ErrorResponse
)

# Import submodule services and dependencies
from .passwords import PasswordService, router as passwords_router
from .totp import TOTPService, router as totp_router
from .sessions import SessionService, router as sessions_router
from .oauth2 import OAuth2Service, router as oauth2_router
from .service import AuthenticationService
from .router import router
from .deps import (
    get_current_user_token,
    get_current_user,
    get_current_active_user,
    get_optional_current_user,
    security
)

__all__ = [
    # Schemas
    "LoginRequest",
    "LoginResponse", 
    "TokenRequest",
    "TokenResponse",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "PasswordChangeRequest",
    "TOTPSetupRequest",
    "TOTPSetupResponse",
    "TOTPVerifyRequest",
    "TOTPDisableRequest",
    "OAuth2AuthorizeRequest",
    "OAuth2CallbackRequest",
    "OAuth2LinkRequest",
    "SessionInfo",
    "ErrorResponse",
    
    # Services
    "PasswordService",
    "TOTPService",
    "SessionService",
    "OAuth2Service",
    "AuthenticationService",
    
    # Routers
    "router",
    "passwords_router",
    "totp_router", 
    "sessions_router",
    "oauth2_router",
    
    # Dependencies
    "get_current_user_token",
    "get_current_user",
    "get_current_active_user",
    "get_optional_current_user",
    "security"
]
