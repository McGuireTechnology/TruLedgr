"""
Plaid Users Service

This service handles Plaid User management for specialized products.

IMPORTANT NOTE: 
Plaid Users are NOT required for basic banking products like:
- Transactions ✅
- Liabilities ✅  
- Accounts ✅
- Investments ✅
- Auth ✅

Plaid Users are ONLY required for:
- Plaid Check Consumer Reports (credit/lending)
- Income verification
- Multi-Item Link flows
- Identity Verification (KYC/AML)
- Monitor services

Since TruLedgr currently only uses Transactions and Liabilities,
this service remains a placeholder until those specialized features are needed.
"""

import logging
from typing import Optional, Dict, Any
from .models import (
    UserCreateRequest,
    UserCreateResponse,
    UserGetRequest, 
    UserGetResponse,
    UserUpdateRequest,
    UserUpdateResponse
)

logger = logging.getLogger(__name__)

class PlaidUsersService:
    """
    Service for managing Plaid Users (specialized products only)
    
    This service is currently not used since TruLedgr only uses
    Transactions and Liabilities, which work with Items/Access Tokens.
    """
    
    def __init__(self, plaid_service):
        self.plaid_service = plaid_service
        logger.info("PlaidUsersService initialized (placeholder - not used for Transactions/Liabilities)")
    
    async def create_user(self, request: UserCreateRequest) -> UserCreateResponse:
        """
        Create a Plaid User for specialized products
        
        NOTE: Only call this when you need:
        - Plaid Check Consumer Reports
        - Income verification  
        - Multi-Item Link
        - Identity Verification
        - Monitor services
        """
        # TODO: Implement when specialized features are needed
        raise NotImplementedError("Plaid Users not needed for current Transactions/Liabilities usage")
    
    async def get_user(self, request: UserGetRequest) -> UserGetResponse:
        """Get Plaid User information"""
        # TODO: Implement when specialized features are needed
        raise NotImplementedError("Plaid Users not needed for current Transactions/Liabilities usage")
    
    async def update_user(self, request: UserUpdateRequest) -> UserUpdateResponse:
        """Update Plaid User information"""  
        # TODO: Implement when specialized features are needed
        raise NotImplementedError("Plaid Users not needed for current Transactions/Liabilities usage")


# Global service instance (placeholder)
_plaid_users_service: Optional[PlaidUsersService] = None

def get_plaid_users_service() -> PlaidUsersService:
    """Get or create Plaid Users service instance"""
    global _plaid_users_service
    if _plaid_users_service is None:
        from ..service import get_plaid_service
        _plaid_users_service = PlaidUsersService(get_plaid_service())
    return _plaid_users_service
