"""
Main Authentication Service

This module provides a coordinated authentication service that integrates all submodules:
- Passwords: Password management and reset
- TOTP: Two-factor authentication
- Sessions: Session management
- OAuth2: Social login integration
"""

from typing import Optional, Dict, Any, List
from sqlmodel.ext.asyncio.session import AsyncSession

from api.users.models import User
from .passwords import PasswordService, AccountLockedError
from .totp import TOTPService
from .sessions import SessionService
from .oauth2 import OAuth2Service
from .schemas import LoginRequest, LoginResponse
from .utils.jwt import create_access_token


class AuthenticationService:
    """
    Main authentication service coordinating all authentication submodules.
    
    This service provides a unified interface for all authentication operations
    while delegating specific functionality to specialized submodules.
    """
    
    def __init__(self):
        self.password_service = PasswordService()
        self.totp_service = TOTPService()
        self.session_service = SessionService()
        self.oauth2_service = OAuth2Service()
    
    async def authenticate_user(
        self,
        session: AsyncSession,
        login_request: LoginRequest,
        client_ip: str,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Authenticate user with comprehensive validation.
        
        Args:
            session: Database session
            login_request: Login request data
            client_ip: Client IP address
            user_agent: User agent string
            
        Returns:
            Dictionary with authentication results
        """
        # Step 1: Validate credentials with account lockout protection
        try:
            user = await self.password_service.authenticate_user(
                session, login_request.username, login_request.password, client_ip
            )
        except AccountLockedError as e:
            return {
                "error": "account_locked",
                "message": f"Account is locked. Try again in {e.seconds_remaining} seconds.",
                "seconds_remaining": e.seconds_remaining
            }
        
        if not user:
            return {
                "error": "invalid_credentials",
                "message": "Invalid username or password"
            }
        
        # Step 2: Check if TOTP is required
        if user.totp_enabled:
            if not login_request.totp_code:
                return {
                    "error": "totp_required",
                    "message": "TOTP code is required for this account",
                    "totp_required": True
                }
            
            # Verify TOTP code
            totp_valid = await self.totp_service.verify_totp_code(
                session, user.id, login_request.totp_code
            )
            
            if not totp_valid:
                return {
                    "error": "invalid_totp",
                    "message": "Invalid TOTP code"
                }
        
        # Step 3: Create session
        session_data = await self.session_service.create_session(
            session,
            user,
            client_ip,
            user_agent,
            login_method="password"
        )
        
        # Step 4: Create JWT access token
        token_data = {
            "sub": user.id,
            "username": user.username,
            "email": user.email
        }
        access_token = create_access_token(token_data)
        
        # Step 5: Prepare response
        return {
            "success": True,
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "access_token": access_token,  # JWT token
            "session_token": session_data["session_token"],  # Session token for session management
            "session_id": session_data["session_id"],
            "expires_at": session_data["expires_at"],
            "totp_enabled": user.totp_enabled
        }
    
    async def validate_session_token(
        self,
        session: AsyncSession,
        session_token: str,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Optional[User]:
        """
        Validate session token and return authenticated user.
        
        Args:
            session: Database session
            session_token: Session token to validate
            client_ip: Client IP address
            user_agent: User agent string
            
        Returns:
            User if session is valid, None otherwise
        """
        return await self.session_service.validate_session(
            session, session_token, client_ip, user_agent
        )
    
    async def logout_user(
        self,
        session: AsyncSession,
        session_token: str,
        all_sessions: bool = False
    ) -> Dict[str, Any]:
        """
        Logout user by revoking session(s).
        
        Args:
            session: Database session
            session_token: Current session token
            all_sessions: Whether to revoke all user sessions
            
        Returns:
            Dictionary with logout results
        """
        if all_sessions:
            # Get user from session token first
            user = await self.validate_session_token(session, session_token)
            if not user:
                return {
                    "error": "invalid_session",
                    "message": "Invalid session token"
                }
            
            # Revoke all sessions
            revoked_count = await self.session_service.revoke_all_user_sessions(
                session, user.id
            )
            
            return {
                "success": True,
                "message": f"Logged out from {revoked_count} sessions"
            }
        else:
            # Revoke current session only
            success = await self.session_service.revoke_session(
                session, session_token, "user_logout"
            )
            
            if success:
                return {
                    "success": True,
                    "message": "Logged out successfully"
                }
            else:
                return {
                    "error": "logout_failed",
                    "message": "Failed to logout"
                }
    
    async def setup_two_factor_auth(
        self,
        session: AsyncSession,
        user: User
    ) -> Dict[str, Any]:
        """
        Setup TOTP two-factor authentication for user.
        
        Args:
            session: Database session
            user: User setting up 2FA
            
        Returns:
            Dictionary with setup data
        """
        return await self.totp_service.setup_totp(session, user)
    
    async def verify_and_enable_totp(
        self,
        session: AsyncSession,
        user: User,
        totp_code: str
    ) -> Dict[str, Any]:
        """
        Verify TOTP setup and enable 2FA.
        
        Args:
            session: Database session
            user: User enabling 2FA
            totp_code: TOTP verification code
            
        Returns:
            Dictionary with verification results
        """
        return await self.totp_service.verify_and_enable_totp(session, user, totp_code)
    
    async def disable_two_factor_auth(
        self,
        session: AsyncSession,
        user: User,
        totp_code: str
    ) -> Dict[str, Any]:
        """
        Disable TOTP two-factor authentication.
        
        Args:
            session: Database session
            user: User disabling 2FA
            totp_code: TOTP verification code
            
        Returns:
            Dictionary with disable results
        """
        return await self.totp_service.disable_totp(session, user, totp_code)
    
    async def initiate_password_reset(
        self,
        session: AsyncSession,
        email: str,
        client_ip: str
    ) -> Dict[str, Any]:
        """
        Initiate password reset process.
        
        Args:
            session: Database session
            email: User email address
            client_ip: Client IP address
            
        Returns:
            Dictionary with reset initiation results
        """
        return await self.password_service.request_password_reset(
            session, email, client_ip, user_agent="unknown"
        )
    
    async def complete_password_reset(
        self,
        session: AsyncSession,
        token: str,
        new_password: str,
        client_ip: str
    ) -> Dict[str, Any]:
        """
        Complete password reset process.
        
        Args:
            session: Database session
            token: Reset token
            new_password: New password
            client_ip: Client IP address
            
        Returns:
            Dictionary with reset completion results
        """
        return await self.password_service.confirm_password_reset(
            session, token, new_password
        )
    
    async def change_password(
        self,
        session: AsyncSession,
        user: User,
        current_password: str,
        new_password: str
    ) -> Dict[str, Any]:
        """
        Change user password.
        
        Args:
            session: Database session
            user: User changing password
            current_password: Current password
            new_password: New password
            
        Returns:
            Dictionary with change results
        """
        success = await self.password_service.change_password(
            session, user, current_password, new_password
        )
        
        if success:
            return {
                "success": True,
                "message": "Password changed successfully"
            }
        else:
            return {
                "error": "password_change_failed",
                "message": "Failed to change password"
            }
    
    def get_oauth_authorization_url(
        self,
        provider: str,
        state: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get OAuth2 authorization URL.
        
        Args:
            provider: OAuth2 provider name
            state: Optional state parameter
            
        Returns:
            Dictionary with authorization URL
        """
        return self.oauth2_service.get_authorization_url(provider, state)
    
    async def handle_oauth_callback(
        self,
        session: AsyncSession,
        provider: str,
        code: str,
        state: str,
        client_ip: str,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle OAuth2 callback and authenticate user.
        
        Args:
            session: Database session
            provider: OAuth2 provider name
            code: Authorization code
            state: State parameter
            client_ip: Client IP address
            user_agent: User agent string
            
        Returns:
            Dictionary with authentication results
        """
        # Exchange code for token
        token_result = await self.oauth2_service.exchange_code_for_token(
            provider, code, state
        )
        
        if "error" in token_result:
            return token_result
        
        # Get user info from provider
        user_info = await self.oauth2_service.get_user_info(
            provider, token_result["access_token"]
        )
        
        if "error" in user_info:
            return user_info
        
        # TODO: Implement user lookup/creation logic
        # For now, return the user info
        return {
            "success": True,
            "provider": provider,
            "user_info": user_info,
            "token_info": token_result
        }
    
    async def get_user_sessions(
        self,
        session: AsyncSession,
        user: User,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get user's active sessions.
        
        Args:
            session: Database session
            user: User to get sessions for
            active_only: Whether to return only active sessions
            
        Returns:
            List of session information
        """
        return await self.session_service.get_user_sessions(
            session, user.id, active_only
        )
    
    async def get_user_oauth_accounts(
        self,
        session: AsyncSession,
        user: User
    ) -> List[Dict[str, Any]]:
        """
        Get user's linked OAuth accounts.
        
        Args:
            session: Database session
            user: User to get accounts for
            
        Returns:
            List of OAuth account information
        """
        return await self.oauth2_service.get_user_oauth_accounts(session, user)
