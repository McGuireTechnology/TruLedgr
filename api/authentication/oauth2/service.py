"""
OAuth2 Service

This module provides OAuth2 integration functionality for third-party authentication providers.
"""

import secrets
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode, parse_qs
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, and_

from api.users.models import User, OAuthAccount
from api.settings import get_settings

settings = get_settings()


class OAuth2Service:
    """
    Service for OAuth2 provider integration.
    
    Provides OAuth2 functionality including:
    - Provider configuration
    - Authorization URL generation
    - Token exchange
    - Account linking
    """
    
    def __init__(self):
        self.providers = self._setup_providers()
        self.state_expiry = 600  # 10 minutes
    
    def _setup_providers(self) -> Dict[str, Dict[str, Any]]:
        """
        Setup OAuth2 provider configurations.
        
        Returns:
            Dictionary of provider configurations
        """
        providers = {}
        
        # Google OAuth2
        google_client_id = getattr(settings, 'google_oauth_client_id', None)
        google_client_secret = getattr(settings, 'google_oauth_client_secret', None)
        
        if google_client_id and google_client_secret:
            providers['google'] = {
                'client_id': google_client_id,
                'client_secret': google_client_secret,
                'auth_url': 'https://accounts.google.com/o/oauth2/v2/auth',
                'token_url': 'https://oauth2.googleapis.com/token',
                'user_info_url': 'https://www.googleapis.com/oauth2/v2/userinfo',
                'scopes': ['openid', 'email', 'profile'],
                'redirect_uri': getattr(settings, 'google_oauth_redirect_uri', None)
            }
        
        # Microsoft OAuth2
        microsoft_client_id = getattr(settings, 'microsoft_oauth_client_id', None)
        microsoft_client_secret = getattr(settings, 'microsoft_oauth_client_secret', None)
        
        if microsoft_client_id and microsoft_client_secret:
            providers['microsoft'] = {
                'client_id': microsoft_client_id,
                'client_secret': microsoft_client_secret,
                'auth_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
                'token_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
                'user_info_url': 'https://graph.microsoft.com/v1.0/me',
                'scopes': ['openid', 'email', 'profile'],
                'redirect_uri': getattr(settings, 'microsoft_oauth_redirect_uri', None)
            }
        
        # Apple OAuth2
        apple_client_id = getattr(settings, 'apple_oauth_client_id', None)
        apple_client_secret = getattr(settings, 'apple_oauth_client_secret', None)
        
        if apple_client_id and apple_client_secret:
            providers['apple'] = {
                'client_id': apple_client_id,
                'client_secret': apple_client_secret,
                'auth_url': 'https://appleid.apple.com/auth/authorize',
                'token_url': 'https://appleid.apple.com/auth/token',
                'user_info_url': None,  # Apple provides user info in ID token
                'scopes': ['name', 'email'],
                'redirect_uri': getattr(settings, 'apple_oauth_redirect_uri', None)
            }
        
        return providers
    
    def get_authorization_url(
        self,
        provider: str,
        state: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate OAuth2 authorization URL.
        
        Args:
            provider: OAuth2 provider name
            state: Optional state parameter
            
        Returns:
            Dictionary with authorization URL and state
        """
        if provider not in self.providers:
            return {
                "error": "provider_not_supported",
                "message": f"OAuth2 provider '{provider}' is not supported"
            }
        
        provider_config = self.providers[provider]
        
        if not state:
            state = secrets.token_urlsafe(32)
        
        # Build authorization parameters
        auth_params = {
            'client_id': provider_config['client_id'],
            'response_type': 'code',
            'scope': ' '.join(provider_config['scopes']),
            'redirect_uri': provider_config['redirect_uri'],
            'state': state
        }
        
        # Provider-specific parameters
        if provider == 'microsoft':
            auth_params['response_mode'] = 'query'
        elif provider == 'apple':
            auth_params['response_mode'] = 'form_post'
        
        # Build authorization URL
        auth_url = f"{provider_config['auth_url']}?{urlencode(auth_params)}"
        
        return {
            "authorization_url": auth_url,
            "state": state,
            "provider": provider
        }
    
    async def exchange_code_for_token(
        self,
        provider: str,
        code: str,
        state: str
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.
        
        Args:
            provider: OAuth2 provider name
            code: Authorization code
            state: State parameter
            
        Returns:
            Dictionary with token information
        """
        if provider not in self.providers:
            return {
                "error": "provider_not_supported",
                "message": f"OAuth2 provider '{provider}' is not supported"
            }
        
        provider_config = self.providers[provider]
        
        # TODO: In a real implementation, you would make HTTP requests to exchange the code
        # For now, return a mock response
        return {
            "access_token": f"mock_access_token_{secrets.token_urlsafe(16)}",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": f"mock_refresh_token_{secrets.token_urlsafe(16)}",
            "scope": " ".join(provider_config['scopes'])
        }
    
    async def get_user_info(
        self,
        provider: str,
        access_token: str
    ) -> Dict[str, Any]:
        """
        Get user information from OAuth2 provider.
        
        Args:
            provider: OAuth2 provider name
            access_token: Access token
            
        Returns:
            Dictionary with user information
        """
        if provider not in self.providers:
            return {
                "error": "provider_not_supported",
                "message": f"OAuth2 provider '{provider}' is not supported"
            }
        
        # TODO: In a real implementation, you would make HTTP requests to get user info
        # For now, return a mock response
        mock_user_info = {
            "id": f"mock_user_id_{secrets.token_urlsafe(8)}",
            "email": f"user_{secrets.token_urlsafe(4)}@example.com",
            "name": f"Mock User {secrets.token_urlsafe(4)}",
            "picture": None,
            "verified_email": True
        }
        
        return mock_user_info
    
    async def link_oauth_account(
        self,
        session: AsyncSession,
        user: User,
        provider: str,
        provider_user_id: str,
        provider_email: str,
        provider_name: Optional[str] = None,
        provider_picture: Optional[str] = None,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        token_expires_at: Optional[datetime] = None,
        raw_user_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Link OAuth account to user.
        
        Args:
            session: Database session
            user: User to link account to
            provider: OAuth2 provider name
            provider_user_id: Provider user ID
            provider_email: Provider email
            provider_name: Provider display name
            provider_picture: Provider profile picture URL
            access_token: Access token
            refresh_token: Refresh token
            token_expires_at: Token expiration
            raw_user_data: Raw user data from provider
            
        Returns:
            Dictionary with linking results
        """
        # Check if OAuth account already exists
        stmt = select(OAuthAccount).where(
            and_(
                OAuthAccount.provider == provider,
                OAuthAccount.provider_user_id == provider_user_id
            )
        )
        
        result = await session.execute(stmt)
        existing_account = result.scalar_one_or_none()
        
        if existing_account:
            if existing_account.user_id == user.id:
                # Update existing account
                existing_account.provider_email = provider_email
                existing_account.provider_name = provider_name
                existing_account.provider_picture = provider_picture
                existing_account.access_token = access_token
                existing_account.refresh_token = refresh_token
                existing_account.token_expires_at = token_expires_at
                existing_account.raw_user_data = json.dumps(raw_user_data) if raw_user_data else None
                existing_account.updated_at = datetime.utcnow()
                
                await session.commit()
                
                return {
                    "success": True,
                    "message": "OAuth account updated successfully",
                    "account_id": existing_account.id
                }
            else:
                return {
                    "error": "account_already_linked",
                    "message": "This OAuth account is already linked to another user"
                }
        
        # Create new OAuth account
        oauth_account = OAuthAccount(
            id=secrets.token_urlsafe(16),
            user_id=user.id,
            provider=provider,
            provider_user_id=provider_user_id,
            provider_email=provider_email,
            provider_name=provider_name,
            provider_picture=provider_picture,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expires_at=token_expires_at,
            raw_user_data=json.dumps(raw_user_data) if raw_user_data else None
        )
        
        session.add(oauth_account)
        await session.commit()
        await session.refresh(oauth_account)
        
        return {
            "success": True,
            "message": "OAuth account linked successfully",
            "account_id": oauth_account.id
        }
    
    async def unlink_oauth_account(
        self,
        session: AsyncSession,
        user: User,
        provider: str
    ) -> Dict[str, Any]:
        """
        Unlink OAuth account from user.
        
        Args:
            session: Database session
            user: User to unlink account from
            provider: OAuth2 provider name
            
        Returns:
            Dictionary with unlinking results
        """
        # Find OAuth account
        stmt = select(OAuthAccount).where(
            and_(
                OAuthAccount.user_id == user.id,
                OAuthAccount.provider == provider
            )
        )
        
        result = await session.execute(stmt)
        oauth_account = result.scalar_one_or_none()
        
        if not oauth_account:
            return {
                "error": "account_not_found",
                "message": f"No {provider} account found for this user"
            }
        
        # Remove OAuth account
        await session.delete(oauth_account)
        await session.commit()
        
        return {
            "success": True,
            "message": f"{provider.title()} account unlinked successfully"
        }
    
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
        stmt = select(OAuthAccount).where(OAuthAccount.user_id == user.id)
        result = await session.execute(stmt)
        oauth_accounts = result.scalars().all()
        
        accounts_info = []
        for account in oauth_accounts:
            accounts_info.append({
                "id": account.id,
                "provider": account.provider,
                "provider_email": account.provider_email,
                "provider_name": account.provider_name,
                "provider_picture": account.provider_picture,
                "created_at": account.created_at,
                "updated_at": account.updated_at
            })
        
        return accounts_info
    
    def get_available_providers(self) -> List[str]:
        """
        Get list of available OAuth2 providers.
        
        Returns:
            List of provider names
        """
        return list(self.providers.keys())
