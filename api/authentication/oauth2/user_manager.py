"""
OAuth2 User Management Service

Provides comprehensive OAuth2 user account management including
account linking, provider management, and user data synchronization.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlmodel import SQLModel, Field, select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.authentication.oauth2.providers import get_oauth2_provider, OAuth2ProviderError


class OAuth2Account(SQLModel, table=True):
    """Database model for OAuth2 linked accounts"""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    provider: str = Field(index=True)  # google, microsoft, apple, github
    provider_user_id: str = Field(index=True)  # ID from OAuth2 provider
    email: str = Field(index=True)
    
    # User data from provider
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    picture_url: Optional[str] = None
    
    # Account status
    is_active: bool = Field(default=True)
    is_email_verified: bool = Field(default=False)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None
    
    # OAuth2 tokens (encrypted in production)
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    
    # Additional provider-specific data
    provider_data: Optional[str] = None  # JSON string


class OAuth2UserManager:
    """
    Comprehensive OAuth2 user management service.
    
    Features:
    - Account linking and unlinking
    - Provider data synchronization
    - Token management
    - User profile updates
    - Multi-provider support
    """
    
    async def link_oauth2_account(
        self,
        session: AsyncSession,
        user_id: str,
        provider: str,
        provider_user_data: Dict[str, Any],
        tokens: Dict[str, Any]
    ) -> OAuth2Account:
        """Link an OAuth2 account to an existing user"""
        
        # Check if account is already linked
        existing_account = await self.get_oauth2_account(
            session, user_id, provider
        )
        
        if existing_account:
            # Update existing account
            return await self.update_oauth2_account(
                session, existing_account, provider_user_data, tokens
            )
        
        # Create new OAuth2 account link
        oauth2_account = OAuth2Account(
            user_id=user_id,
            provider=provider,
            provider_user_id=provider_user_data.get("provider_id", ""),
            email=provider_user_data.get("email", ""),
            first_name=provider_user_data.get("first_name"),
            last_name=provider_user_data.get("last_name"),
            full_name=provider_user_data.get("full_name"),
            picture_url=provider_user_data.get("picture"),
            is_email_verified=provider_user_data.get("email_verified", False),
            access_token=tokens.get("access_token"),
            refresh_token=tokens.get("refresh_token"),
            provider_data=str(provider_user_data.get("raw_data", {}))
        )
        
        # Set token expiration
        if tokens.get("expires_in"):
            from datetime import timedelta
            oauth2_account.token_expires_at = datetime.utcnow() + timedelta(
                seconds=int(tokens["expires_in"])
            )
        
        session.add(oauth2_account)
        await session.commit()
        await session.refresh(oauth2_account)
        
        return oauth2_account
    
    async def get_oauth2_account(
        self,
        session: AsyncSession,
        user_id: str,
        provider: str
    ) -> Optional[OAuth2Account]:
        """Get OAuth2 account for user and provider"""
        
        query = select(OAuth2Account).where(
            OAuth2Account.user_id == user_id,
            OAuth2Account.provider == provider,
            OAuth2Account.is_active == True
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_oauth2_accounts(
        self,
        session: AsyncSession,
        user_id: str
    ) -> List[OAuth2Account]:
        """Get all OAuth2 accounts for a user"""
        
        query = select(OAuth2Account).where(
            OAuth2Account.user_id == user_id,
            OAuth2Account.is_active == True
        )
        result = await session.execute(query)
        return list(result.scalars().all())
    
    async def find_user_by_oauth2_account(
        self,
        session: AsyncSession,
        provider: str,
        provider_user_id: str
    ) -> Optional[OAuth2Account]:
        """Find user by OAuth2 provider and provider user ID"""
        
        query = select(OAuth2Account).where(
            OAuth2Account.provider == provider,
            OAuth2Account.provider_user_id == provider_user_id,
            OAuth2Account.is_active == True
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    async def update_oauth2_account(
        self,
        session: AsyncSession,
        oauth2_account: OAuth2Account,
        provider_user_data: Dict[str, Any],
        tokens: Dict[str, Any]
    ) -> OAuth2Account:
        """Update OAuth2 account with new data and tokens"""
        
        # Update user data
        oauth2_account.email = provider_user_data.get("email", oauth2_account.email)
        oauth2_account.first_name = provider_user_data.get("first_name", oauth2_account.first_name)
        oauth2_account.last_name = provider_user_data.get("last_name", oauth2_account.last_name)
        oauth2_account.full_name = provider_user_data.get("full_name", oauth2_account.full_name)
        oauth2_account.picture_url = provider_user_data.get("picture", oauth2_account.picture_url)
        oauth2_account.is_email_verified = provider_user_data.get("email_verified", oauth2_account.is_email_verified)
        oauth2_account.provider_data = str(provider_user_data.get("raw_data", {}))
        oauth2_account.updated_at = datetime.utcnow()
        oauth2_account.last_login_at = datetime.utcnow()
        
        # Update tokens
        oauth2_account.access_token = tokens.get("access_token", oauth2_account.access_token)
        oauth2_account.refresh_token = tokens.get("refresh_token", oauth2_account.refresh_token)
        
        # Update token expiration
        if tokens.get("expires_in"):
            from datetime import timedelta
            oauth2_account.token_expires_at = datetime.utcnow() + timedelta(
                seconds=int(tokens["expires_in"])
            )
        
        await session.commit()
        return oauth2_account
    
    async def unlink_oauth2_account(
        self,
        session: AsyncSession,
        user_id: str,
        provider: str
    ) -> bool:
        """Unlink OAuth2 account from user"""
        
        oauth2_account = await self.get_oauth2_account(session, user_id, provider)
        
        if not oauth2_account:
            return False
        
        # Soft delete - mark as inactive
        oauth2_account.is_active = False
        oauth2_account.updated_at = datetime.utcnow()
        
        await session.commit()
        return True
    
    async def refresh_oauth2_token(
        self,
        session: AsyncSession,
        oauth2_account: OAuth2Account
    ) -> Optional[Dict[str, Any]]:
        """Refresh OAuth2 access token using refresh token"""
        
        if not oauth2_account.refresh_token:
            return None
        
        try:
            provider = get_oauth2_provider(oauth2_account.provider)
            
            # This would require implementing refresh token logic in providers
            # For now, return None indicating refresh is not available
            return None
            
        except Exception:
            return None
    
    async def sync_user_profile(
        self,
        session: AsyncSession,
        user_id: str,
        provider: str,
        force_update: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Sync user profile data from OAuth2 provider"""
        
        oauth2_account = await self.get_oauth2_account(session, user_id, provider)
        
        if not oauth2_account or not oauth2_account.access_token:
            return None
        
        # Check if token is expired (simplified check)
        if oauth2_account.token_expires_at and datetime.utcnow() > oauth2_account.token_expires_at:
            # Try to refresh token
            new_tokens = await self.refresh_oauth2_token(session, oauth2_account)
            if not new_tokens:
                return None
        
        try:
            provider_instance = get_oauth2_provider(provider)
            user_data = await provider_instance.get_user_info(oauth2_account.access_token)
            
            # Update OAuth2 account with fresh data
            await self.update_oauth2_account(
                session, oauth2_account, user_data, {}
            )
            
            return user_data
            
        except OAuth2ProviderError:
            return None
    
    async def get_user_oauth2_summary(
        self,
        session: AsyncSession,
        user_id: str
    ) -> Dict[str, Any]:
        """Get summary of user's OAuth2 accounts"""
        
        accounts = await self.get_user_oauth2_accounts(session, user_id)
        
        providers_linked = []
        total_accounts = len(accounts)
        verified_emails = 0
        
        for account in accounts:
            providers_linked.append({
                "provider": account.provider,
                "email": account.email,
                "is_verified": account.is_email_verified,
                "last_login": account.last_login_at,
                "created_at": account.created_at
            })
            
            if account.is_email_verified:
                verified_emails += 1
        
        return {
            "total_accounts": total_accounts,
            "verified_emails": verified_emails,
            "providers_linked": providers_linked,
            "available_providers": ["google", "microsoft", "apple", "github"]
        }
    
    async def cleanup_inactive_accounts(
        self,
        session: AsyncSession,
        days_inactive: int = 365
    ) -> int:
        """Clean up old inactive OAuth2 accounts"""
        
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days_inactive)
        
        query = select(OAuth2Account).where(
            OAuth2Account.is_active == False,
            OAuth2Account.updated_at < cutoff_date
        )
        result = await session.execute(query)
        inactive_accounts = result.scalars().all()
        
        count = len(inactive_accounts)
        
        for account in inactive_accounts:
            await session.delete(account)
        
        await session.commit()
        return count
    
    async def get_provider_statistics(
        self,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Get OAuth2 provider usage statistics"""
        
        query = select(OAuth2Account).where(OAuth2Account.is_active == True)
        result = await session.execute(query)
        accounts = result.scalars().all()
        
        provider_counts = {}
        total_accounts = len(accounts)
        verified_accounts = 0
        
        for account in accounts:
            provider = account.provider
            if provider not in provider_counts:
                provider_counts[provider] = 0
            provider_counts[provider] += 1
            
            if account.is_email_verified:
                verified_accounts += 1
        
        return {
            "total_accounts": total_accounts,
            "verified_accounts": verified_accounts,
            "provider_distribution": provider_counts,
            "verification_rate": verified_accounts / total_accounts if total_accounts > 0 else 0
        }


# Global OAuth2 user manager instance
oauth2_user_manager = OAuth2UserManager()
