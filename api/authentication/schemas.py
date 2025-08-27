"""
Authentication request/response schemas and data models.

This module defines Pydantic models for authentication operations including:
- Login requests and responses
- Token management
- Password reset flows
- TOTP/2FA operations
- OAuth2 authentication
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime


# Base Authentication Schemas
class LoginRequest(BaseModel):
    """Login request with username/email and password."""
    username: str = Field(..., description="Username or email address")
    password: str = Field(..., min_length=1, description="User password")
    totp_code: Optional[str] = Field(None, description="TOTP code for 2FA")
    remember_me: bool = Field(False, description="Extended session duration")
    
    @validator('username')
    def validate_username(cls, v):
        if not v or not v.strip():
            raise ValueError('Username cannot be empty')
        return v.strip().lower()


class LoginResponse(BaseModel):
    """Login response with user information and token."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]
    session_id: Optional[str] = None
    totp_required: bool = False


class TokenResponse(BaseModel):
    """Simple token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None


class TokenRequest(BaseModel):
    """Token request for various authentication flows."""
    grant_type: str = Field(..., description="OAuth2 grant type")
    username: Optional[str] = Field(None, description="Username for password grant")
    password: Optional[str] = Field(None, description="Password for password grant")
    refresh_token: Optional[str] = Field(None, description="Refresh token for refresh grant")
    code: Optional[str] = Field(None, description="Authorization code for authorization_code grant")


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


class LogoutRequest(BaseModel):
    """Logout request."""
    all_sessions: bool = Field(False, description="Logout from all sessions")


# Password Management Schemas
class PasswordResetRequest(BaseModel):
    """Password reset request with email."""
    email: EmailStr = Field(..., description="Email address for password reset")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation with token and new password."""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class PasswordChangeRequest(BaseModel):
    """Password change request with current and new passwords."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


# TOTP/2FA Schemas
class TOTPSetupRequest(BaseModel):
    """TOTP setup initiation request."""
    user_id: Optional[str] = Field(None, description="User ID (for admin use)")


class TOTPSetupResponse(BaseModel):
    """TOTP setup response with secret and QR code URI."""
    secret: str = Field(..., description="TOTP secret key")
    qr_uri: str = Field(..., description="QR code provisioning URI")
    backup_codes: List[str] = Field(default_factory=list, description="Backup recovery codes")


class TOTPVerifyRequest(BaseModel):
    """TOTP code verification request."""
    code: str = Field(..., min_length=6, max_length=6, description="6-digit TOTP code")
    
    @validator('code')
    def validate_totp_code(cls, v):
        if not v.isdigit():
            raise ValueError('TOTP code must contain only digits')
        if len(v) != 6:
            raise ValueError('TOTP code must be exactly 6 digits')
        return v


class TOTPDisableRequest(BaseModel):
    """TOTP disable request."""
    totp_code: str = Field(..., min_length=6, max_length=6, description="6-digit TOTP code for verification")
    
    @validator('totp_code')
    def validate_totp_code(cls, v):
        if not v.isdigit():
            raise ValueError('TOTP code must contain only digits')
        if len(v) != 6:
            raise ValueError('TOTP code must be exactly 6 digits')
        return v


class TOTPStatusResponse(BaseModel):
    """TOTP status response."""
    enabled: bool
    setup_required: bool = False
    backup_codes_remaining: int = 0


class BackupCodeVerifyRequest(BaseModel):
    """Backup code verification request."""
    backup_code: str = Field(..., description="Backup recovery code")


# OAuth2 Schemas
class OAuth2AuthorizeRequest(BaseModel):
    """OAuth2 authorization request."""
    provider: str = Field(..., description="OAuth2 provider name")
    redirect_uri: Optional[str] = Field(None, description="Post-authorization redirect URI")
    state: Optional[str] = Field(None, description="State parameter for CSRF protection")


class OAuth2CallbackRequest(BaseModel):
    """OAuth2 callback request."""
    code: str = Field(..., description="Authorization code from provider")
    state: str = Field(..., description="State parameter for CSRF protection")
    provider: str = Field(..., description="OAuth2 provider name")


class OAuth2LinkRequest(BaseModel):
    """OAuth2 account linking request."""
    provider: str = Field(..., description="OAuth2 provider name")
    access_token: str = Field(..., description="OAuth2 access token")


class OAuthUserInfo(BaseModel):
    """OAuth2 user information from provider."""
    provider_id: str
    email: str
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    picture: Optional[str] = None
    provider: str


class OAuthAccountResponse(BaseModel):
    """OAuth2 linked account response."""
    id: str
    provider: str
    provider_email: str
    provider_name: Optional[str] = None
    created_at: datetime
    last_used_at: Optional[datetime] = None


# Session Management Schemas
class SessionInfo(BaseModel):
    """Session information response."""
    id: str
    user_id: str
    created_at: datetime
    last_accessed_at: datetime
    expires_at: Optional[datetime] = None
    client_ip: str
    user_agent: str
    is_current: bool = False
    location: Optional[str] = None


class SessionListResponse(BaseModel):
    """List of user sessions."""
    sessions: List[SessionInfo]
    total: int
    current_session_id: Optional[str] = None


class RevokeSessionRequest(BaseModel):
    """Revoke session request."""
    session_id: str


# Error Response Schemas
class AuthErrorResponse(BaseModel):
    """Authentication error response."""
    error: str
    error_description: Optional[str] = None
    error_code: Optional[str] = None


class ValidationErrorResponse(BaseModel):
    """Validation error response."""
    detail: List[Dict[str, Any]]


# Rate Limiting Schemas
class RateLimitResponse(BaseModel):
    """Rate limit error response."""
    error: str = "rate_limit_exceeded"
    retry_after: int
    limit: int
    remaining: int = 0


# Security Event Schemas
class SecurityEventRequest(BaseModel):
    """Security event logging request."""
    event_type: str
    details: Dict[str, Any] = Field(default_factory=dict)
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None


# Account Status Schemas
class AccountStatusResponse(BaseModel):
    """Account security status response."""
    two_factor_enabled: bool
    oauth_accounts: List[str] = Field(default_factory=list)
    last_password_change: Optional[datetime] = None
    failed_login_attempts: int = 0
    account_locked: bool = False
    lockout_expires_at: Optional[datetime] = None
    password_expires_at: Optional[datetime] = None


# Admin Schemas
class UserAuthStatsResponse(BaseModel):
    """User authentication statistics."""
    total_logins: int
    failed_attempts: int
    last_login: Optional[datetime] = None
    last_failed_attempt: Optional[datetime] = None
    oauth_providers: List[str] = Field(default_factory=list)
    two_factor_enabled: bool
    active_sessions: int


class SystemAuthStatsResponse(BaseModel):
    """System-wide authentication statistics."""
    total_users: int
    active_sessions: int
    oauth_users: int
    two_factor_users: int
    failed_attempts_24h: int
    successful_logins_24h: int


# Generic Error Response
class ErrorResponse(BaseModel):
    """Generic error response."""
    error: str = Field(..., description="Error code or type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
