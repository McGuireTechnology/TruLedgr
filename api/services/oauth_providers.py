"""OAuth provider services for token exchange and user info retrieval."""

from abc import ABC, abstractmethod
from typing import Dict
import httpx

from ..config.settings import get_settings

settings = get_settings()


class OAuthProviderError(Exception):
    """Base exception for OAuth provider errors."""
    pass


class OAuthProviderService(ABC):
    """Abstract base class for OAuth provider services."""
    
    @abstractmethod
    async def exchange_code_for_token(
        self,
        code: str,
        redirect_uri: str
    ) -> Dict[str, str]:
        """Exchange authorization code for access token.
        
        Args:
            code: Authorization code from OAuth provider
            redirect_uri: Redirect URI used in the OAuth flow
            
        Returns:
            Dictionary with access_token, refresh_token, expires_in, etc.
            
        Raises:
            OAuthProviderError: If token exchange fails
        """
        pass
    
    @abstractmethod
    async def get_user_info(self, access_token: str) -> Dict[str, str]:
        """Get user information from OAuth provider.
        
        Args:
            access_token: Access token from OAuth provider
            
        Returns:
            Dictionary with user info (id, email, name, etc.)
            
        Raises:
            OAuthProviderError: If user info retrieval fails
        """
        pass


class GoogleOAuthProvider(OAuthProviderService):
    """Google OAuth 2.0 provider service."""
    
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    async def exchange_code_for_token(
        self,
        code: str,
        redirect_uri: str
    ) -> Dict[str, str]:
        """Exchange authorization code for Google access token."""
        if not settings.oauth_google_client_id:
            raise OAuthProviderError("Google OAuth is not configured")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.TOKEN_URL,
                    data={
                        "code": code,
                        "client_id": settings.oauth_google_client_id,
                        "client_secret": settings.oauth_google_client_secret,
                        "redirect_uri": redirect_uri,
                        "grant_type": "authorization_code",
                    },
                    headers={"Accept": "application/json"},
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise OAuthProviderError(
                    f"Google token exchange failed: {e.response.text}"
                ) from e
            except httpx.RequestError as e:
                raise OAuthProviderError(
                    f"Google token exchange request failed: {str(e)}"
                ) from e
    
    async def get_user_info(self, access_token: str) -> Dict[str, str]:
        """Get user information from Google."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.USER_INFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                response.raise_for_status()
                data = response.json()
                
                # Normalize to standard format
                return {
                    "id": data.get("id"),
                    "email": data.get("email"),
                    "name": data.get("name"),
                    "given_name": data.get("given_name"),
                    "family_name": data.get("family_name"),
                    "picture": data.get("picture"),
                    "verified_email": data.get("verified_email", False),
                }
            except httpx.HTTPStatusError as e:
                raise OAuthProviderError(
                    f"Google user info retrieval failed: {e.response.text}"
                ) from e
            except httpx.RequestError as e:
                raise OAuthProviderError(
                    f"Google user info request failed: {str(e)}"
                ) from e


class MicrosoftOAuthProvider(OAuthProviderService):
    """Microsoft OAuth 2.0 provider service."""
    
    TOKEN_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    USER_INFO_URL = "https://graph.microsoft.com/v1.0/me"
    
    async def exchange_code_for_token(
        self,
        code: str,
        redirect_uri: str
    ) -> Dict[str, str]:
        """Exchange authorization code for Microsoft access token."""
        if not settings.oauth_microsoft_client_id:
            raise OAuthProviderError("Microsoft OAuth is not configured")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.TOKEN_URL,
                    data={
                        "code": code,
                        "client_id": settings.oauth_microsoft_client_id,
                        "client_secret": (
                            settings.oauth_microsoft_client_secret
                        ),
                        "redirect_uri": redirect_uri,
                        "grant_type": "authorization_code",
                    },
                    headers={"Accept": "application/json"},
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise OAuthProviderError(
                    f"Microsoft token exchange failed: {e.response.text}"
                ) from e
            except httpx.RequestError as e:
                raise OAuthProviderError(
                    f"Microsoft token exchange request failed: {str(e)}"
                ) from e
    
    async def get_user_info(self, access_token: str) -> Dict[str, str]:
        """Get user information from Microsoft."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.USER_INFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                response.raise_for_status()
                data = response.json()
                
                # Normalize to standard format
                return {
                    "id": data.get("id"),
                    "email": data.get("mail") or data.get("userPrincipalName"),
                    "name": data.get("displayName"),
                    "given_name": data.get("givenName"),
                    "family_name": data.get("surname"),
                }
            except httpx.HTTPStatusError as e:
                raise OAuthProviderError(
                    f"Microsoft user info retrieval failed: {e.response.text}"
                ) from e
            except httpx.RequestError as e:
                raise OAuthProviderError(
                    f"Microsoft user info request failed: {str(e)}"
                ) from e


class AppleOAuthProvider(OAuthProviderService):
    """Apple OAuth 2.0 provider service."""
    
    TOKEN_URL = "https://appleid.apple.com/auth/token"
    
    async def exchange_code_for_token(
        self,
        code: str,
        redirect_uri: str
    ) -> Dict[str, str]:
        """Exchange authorization code for Apple access token."""
        if not settings.oauth_apple_client_id:
            raise OAuthProviderError("Apple OAuth is not configured")
        
        # Note: Apple OAuth requires a client secret JWT
        # For now, using basic implementation
        # Production would require JWT generation with Apple private key
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.TOKEN_URL,
                    data={
                        "code": code,
                        "client_id": settings.oauth_apple_client_id,
                        "client_secret": settings.oauth_apple_client_secret,
                        "redirect_uri": redirect_uri,
                        "grant_type": "authorization_code",
                    },
                    headers={"Accept": "application/json"},
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise OAuthProviderError(
                    f"Apple token exchange failed: {e.response.text}"
                ) from e
            except httpx.RequestError as e:
                raise OAuthProviderError(
                    f"Apple token exchange request failed: {str(e)}"
                ) from e
    
    async def get_user_info(self, access_token: str) -> Dict[str, str]:
        """Get user information from Apple.
        
        Note: Apple provides user info in the ID token (JWT) during
        token exchange, not via a separate endpoint. For now, we'll
        decode the id_token to get user info.
        """
        # Apple's approach is different - user info is in the id_token JWT
        # This is a simplified implementation
        # Production would decode and verify the JWT
        raise OAuthProviderError(
            "Apple user info retrieval not yet implemented. "
            "User info should be extracted from id_token JWT."
        )


def get_oauth_provider(provider: str) -> OAuthProviderService:
    """Get OAuth provider service by name.
    
    Args:
        provider: Provider name (google, microsoft, apple)
        
    Returns:
        OAuth provider service instance
        
    Raises:
        ValueError: If provider is not supported
    """
    providers = {
        "google": GoogleOAuthProvider,
        "microsoft": MicrosoftOAuthProvider,
        "apple": AppleOAuthProvider,
    }
    
    provider_class = providers.get(provider.lower())
    if not provider_class:
        raise ValueError(f"Unsupported OAuth provider: {provider}")
    
    return provider_class()
