"""
OAuth2 Authentication Module

This module provides OAuth2 integration functionality including:
- OAuth2 provider integration (Google, Microsoft, Apple, GitHub)
- Authorization code flow
- Token management
- Account linking and user management
- Provider-specific implementations
"""

from .service import OAuth2Service
from .router import router
from .providers import (
    BaseOAuth2Provider,
    GoogleOAuth2Provider,
    MicrosoftOAuth2Provider,
    AppleOAuth2Provider,
    GitHubOAuth2Provider,
    OAuth2ProviderFactory,
    OAuth2ProviderError,
    get_oauth2_provider
)
from .user_manager import OAuth2UserManager, OAuth2Account, oauth2_user_manager

__all__ = [
    "OAuth2Service",
    "router",
    # Providers
    "BaseOAuth2Provider",
    "GoogleOAuth2Provider", 
    "MicrosoftOAuth2Provider",
    "AppleOAuth2Provider",
    "GitHubOAuth2Provider",
    "OAuth2ProviderFactory",
    "OAuth2ProviderError",
    "get_oauth2_provider",
    # User Management
    "OAuth2UserManager",
    "OAuth2Account",
    "oauth2_user_manager"
]
