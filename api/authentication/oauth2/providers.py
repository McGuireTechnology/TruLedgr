"""
OAuth2 Providers

Enhanced OAuth2 provider implementations with additional social login options
and improved user data handling.
"""

import json
import httpx
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode, parse_qs, urlparse
import secrets

from api.settings import get_settings


class OAuth2ProviderError(Exception):
    """Exception raised for OAuth2 provider errors"""
    pass


class BaseOAuth2Provider:
    """Base class for OAuth2 providers"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scopes: List[str] = []
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Generate authorization URL for the provider"""
        raise NotImplementedError
    
    async def exchange_code_for_token(self, code: str, state: Optional[str] = None) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        raise NotImplementedError
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information using access token"""
        raise NotImplementedError
    
    def _generate_state(self) -> str:
        """Generate secure state parameter"""
        return secrets.token_urlsafe(32)


class GoogleOAuth2Provider(BaseOAuth2Provider):
    """Google OAuth2 provider with enhanced user data"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        super().__init__(client_id, client_secret, redirect_uri)
        self.scopes = ["openid", "email", "profile"]
        self.auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Generate Google authorization URL"""
        if not state:
            state = self._generate_state()
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.scopes),
            "response_type": "code",
            "state": state,
            "access_type": "offline",  # Get refresh token
            "prompt": "select_account"  # Allow account selection
        }
        
        return f"{self.auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str, state: Optional[str] = None) -> Dict[str, Any]:
        """Exchange Google authorization code for tokens"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri
                },
                headers={"Accept": "application/json"}
            )
            
            if response.status_code != 200:
                raise OAuth2ProviderError(f"Token exchange failed: {response.text}")
            
            return response.json()
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get Google user information"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.user_info_url,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                raise OAuth2ProviderError(f"User info request failed: {response.text}")
            
            user_data = response.json()
            
            # Normalize user data
            return {
                "provider_id": user_data.get("id"),
                "email": user_data.get("email"),
                "first_name": user_data.get("given_name", ""),
                "last_name": user_data.get("family_name", ""),
                "full_name": user_data.get("name", ""),
                "picture": user_data.get("picture"),
                "email_verified": user_data.get("verified_email", False),
                "locale": user_data.get("locale"),
                "provider": "google",
                "raw_data": user_data
            }


class MicrosoftOAuth2Provider(BaseOAuth2Provider):
    """Microsoft OAuth2 provider (Azure AD)"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, tenant: str = "common"):
        super().__init__(client_id, client_secret, redirect_uri)
        self.tenant = tenant
        self.scopes = ["openid", "profile", "email", "User.Read"]
        self.auth_url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize"
        self.token_url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
        self.user_info_url = "https://graph.microsoft.com/v1.0/me"
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Generate Microsoft authorization URL"""
        if not state:
            state = self._generate_state()
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.scopes),
            "response_type": "code",
            "state": state,
            "response_mode": "query"
        }
        
        return f"{self.auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str, state: Optional[str] = None) -> Dict[str, Any]:
        """Exchange Microsoft authorization code for tokens"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri
                },
                headers={"Accept": "application/json"}
            )
            
            if response.status_code != 200:
                raise OAuth2ProviderError(f"Token exchange failed: {response.text}")
            
            return response.json()
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get Microsoft user information"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.user_info_url,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                raise OAuth2ProviderError(f"User info request failed: {response.text}")
            
            user_data = response.json()
            
            # Normalize user data
            return {
                "provider_id": user_data.get("id"),
                "email": user_data.get("mail") or user_data.get("userPrincipalName"),
                "first_name": user_data.get("givenName", ""),
                "last_name": user_data.get("surname", ""),
                "full_name": user_data.get("displayName", ""),
                "picture": None,  # Would need separate Graph API call
                "email_verified": True,  # Microsoft emails are typically verified
                "locale": user_data.get("preferredLanguage"),
                "provider": "microsoft",
                "raw_data": user_data
            }


class AppleOAuth2Provider(BaseOAuth2Provider):
    """Apple Sign In OAuth2 provider"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        super().__init__(client_id, client_secret, redirect_uri)
        self.scopes = ["name", "email"]
        self.auth_url = "https://appleid.apple.com/auth/authorize"
        self.token_url = "https://appleid.apple.com/auth/token"
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Generate Apple authorization URL"""
        if not state:
            state = self._generate_state()
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.scopes),
            "response_type": "code",
            "state": state,
            "response_mode": "form_post"  # Apple recommends form_post
        }
        
        return f"{self.auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str, state: Optional[str] = None) -> Dict[str, Any]:
        """Exchange Apple authorization code for tokens"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri
                },
                headers={"Accept": "application/json"}
            )
            
            if response.status_code != 200:
                raise OAuth2ProviderError(f"Token exchange failed: {response.text}")
            
            return response.json()
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get Apple user information.
        Note: Apple provides user info only on first authorization.
        """
        # Apple doesn't provide a user info endpoint
        # User data is provided in the ID token during first authorization
        # For subsequent logins, you need to store user data from first login
        
        # This is a simplified implementation
        # In practice, you'd decode the ID token to get user info
        return {
            "provider_id": None,  # Would come from ID token
            "email": None,  # Would come from ID token
            "first_name": "",
            "last_name": "",
            "full_name": "",
            "picture": None,
            "email_verified": True,  # Apple emails are verified
            "locale": None,
            "provider": "apple",
            "raw_data": {}
        }


class GitHubOAuth2Provider(BaseOAuth2Provider):
    """GitHub OAuth2 provider"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        super().__init__(client_id, client_secret, redirect_uri)
        self.scopes = ["user:email"]
        self.auth_url = "https://github.com/login/oauth/authorize"
        self.token_url = "https://github.com/login/oauth/access_token"
        self.user_info_url = "https://api.github.com/user"
        self.user_emails_url = "https://api.github.com/user/emails"
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Generate GitHub authorization URL"""
        if not state:
            state = self._generate_state()
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.scopes),
            "state": state,
            "allow_signup": "true"
        }
        
        return f"{self.auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str, state: Optional[str] = None) -> Dict[str, Any]:
        """Exchange GitHub authorization code for tokens"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code
                },
                headers={"Accept": "application/json"}
            )
            
            if response.status_code != 200:
                raise OAuth2ProviderError(f"Token exchange failed: {response.text}")
            
            return response.json()
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get GitHub user information"""
        async with httpx.AsyncClient() as client:
            # Get user profile
            user_response = await client.get(
                self.user_info_url,
                headers={"Authorization": f"token {access_token}"}
            )
            
            if user_response.status_code != 200:
                raise OAuth2ProviderError(f"User info request failed: {user_response.text}")
            
            user_data = user_response.json()
            
            # Get user emails
            email_response = await client.get(
                self.user_emails_url,
                headers={"Authorization": f"token {access_token}"}
            )
            
            primary_email = user_data.get("email")
            email_verified = False
            
            if email_response.status_code == 200:
                emails = email_response.json()
                for email_info in emails:
                    if email_info.get("primary", False):
                        primary_email = email_info["email"]
                        email_verified = email_info.get("verified", False)
                        break
            
            # Parse name
            full_name = user_data.get("name", "")
            name_parts = full_name.split(" ", 1) if full_name else ["", ""]
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ""
            
            return {
                "provider_id": str(user_data.get("id")),
                "email": primary_email,
                "first_name": first_name,
                "last_name": last_name,
                "full_name": full_name,
                "picture": user_data.get("avatar_url"),
                "email_verified": email_verified,
                "locale": None,
                "provider": "github",
                "raw_data": user_data
            }


class OAuth2ProviderFactory:
    """Factory for creating OAuth2 providers"""
    
    _providers = {
        "google": GoogleOAuth2Provider,
        "microsoft": MicrosoftOAuth2Provider,
        "apple": AppleOAuth2Provider,
        "github": GitHubOAuth2Provider
    }
    
    @classmethod
    def create_provider(
        cls,
        provider_name: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        **kwargs
    ) -> BaseOAuth2Provider:
        """Create an OAuth2 provider instance"""
        
        if provider_name not in cls._providers:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        provider_class = cls._providers[provider_name]
        
        if provider_name == "microsoft":
            tenant = kwargs.get("tenant", "common")
            return provider_class(client_id, client_secret, redirect_uri, tenant)
        else:
            return provider_class(client_id, client_secret, redirect_uri)
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of available OAuth2 providers"""
        return list(cls._providers.keys())


def get_oauth2_provider(provider_name: str) -> BaseOAuth2Provider:
    """Get configured OAuth2 provider instance"""
    settings = get_settings()
    
    # Get provider configuration from settings
    provider_config = getattr(settings, f"{provider_name}_oauth2", None)
    if not provider_config:
        raise ValueError(f"OAuth2 provider '{provider_name}' not configured")
    
    return OAuth2ProviderFactory.create_provider(
        provider_name,
        provider_config.client_id,
        provider_config.client_secret,
        provider_config.redirect_uri,
        **provider_config.extra_params if hasattr(provider_config, 'extra_params') else {}
    )
