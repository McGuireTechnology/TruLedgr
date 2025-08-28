"""
Plaid Accounts Router

FastAPI endpoints for Account information and balance operations.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import logging

from api.authentication.deps import get_current_user
from api.users.models import User
from ..service import PlaidService, get_plaid_service
from ..items.models import PlaidEnvironment
from .models import (
    PlaidAccountResponse,
    AccountSyncRequest,
    AccountBalanceHistoryResponse,
    AccountStatusHistoryResponse,
    AccountInversionSettingsRequest
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/accounts", tags=["Plaid Accounts"])

# Request models for account operations
class AccountRefreshRequest(BaseModel):
    """Request model for refreshing account data"""
    force_refresh: bool = False
    include_balances: bool = True

# Helper functions for ID handling
def _convert_ulid_to_legacy_id(account_ulid: str) -> int:
    """Temporary helper to convert ULID to legacy integer ID for service calls"""
    import hashlib
    hash_obj = hashlib.md5(account_ulid.encode())
    return int(hash_obj.hexdigest()[:8], 16) % (2**31)

# ==========================================
# Main Account Management Routes
# ==========================================

@router.get("/summary")
async def get_accounts_summary(
    current_user: User = Depends(get_current_user),
    plaid_service: PlaidService = Depends(get_plaid_service)
):
    """
    Get a summary of all accounts for the current user.
    
    Returns aggregated information like total balances by type,
    account counts, and status overview.
    """
    try:
        accounts = await plaid_service.get_user_accounts_db(current_user.id)
        
        # Calculate summary statistics
        summary = {
            "total_accounts": len(accounts),
            "accounts_by_type": {},
            "total_balances": {
                "available": 0.0,
                "current": 0.0
            },
            "active_accounts": 0,
            "institutions": set()
        }
        
        for account in accounts:
            # Count by type
            account_type = account.type
            if account_type not in summary["accounts_by_type"]:
                summary["accounts_by_type"][account_type] = 0
            summary["accounts_by_type"][account_type] += 1
            
            # Sum balances (only for active accounts)
            if account.is_active and not account.is_closed:
                summary["active_accounts"] += 1
                if account.available_balance:
                    summary["total_balances"]["available"] += account.available_balance
                if account.current_balance:
                    summary["total_balances"]["current"] += account.current_balance
            
            # Track institutions
            if hasattr(account, 'institution_name'):
                summary["institutions"].add(account.institution_name)
        
        # Convert set to list for JSON serialization
        summary["institutions"] = list(summary["institutions"])
        summary["total_institutions"] = len(summary["institutions"])
        
        return summary
    except Exception as e:
        logger.error(f"Error generating account summary for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate account summary"
        )

@router.get("/", response_model=List[PlaidAccountResponse])
async def get_accounts(
    environment: Optional[str] = Query(default=None, description="Filter by environment (sandbox/production)"),
    item_id: Optional[str] = Query(default=None, description="Filter by specific item ID"),
    account_type: Optional[str] = Query(default=None, description="Filter by account type (depository, credit, etc.)"),
    current_user: User = Depends(get_current_user),
    plaid_service: PlaidService = Depends(get_plaid_service)
):
    """
    Get all accounts for the current user from database.
    
    Supports filtering by environment, item, and account type.
    Returns comprehensive account information including balances and metadata.
    """
    try:
        accounts = await plaid_service.get_user_accounts_db(current_user.id)
        
        # Apply filters if specified
        if environment:
            # This would need to be implemented in the service to filter by environment
            pass
            
        if item_id:
            accounts = [acc for acc in accounts if getattr(acc, 'item_id', None) == item_id]
            
        if account_type:
            accounts = [acc for acc in accounts if acc.type == account_type]
        
        return accounts
    except Exception as e:
        logger.error(f"Error fetching accounts for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch accounts"
        )

@router.get("/{account_id}", response_model=PlaidAccountResponse)
async def get_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
    plaid_service: PlaidService = Depends(get_plaid_service)
):
    """Get a specific account by ID."""
    try:
        # Get all user accounts and filter by ID
        accounts = await plaid_service.get_user_accounts_db(current_user.id)
        account = next((acc for acc in accounts if acc.id == account_id), None)
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        return account
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching account {account_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch account"
        )

@router.post("/{account_id}/refresh")
async def refresh_account(
    account_id: str,
    request: AccountRefreshRequest,
    current_user: User = Depends(get_current_user),
    plaid_service: PlaidService = Depends(get_plaid_service)
):
    """
    Refresh account data from Plaid API.
    
    This can help get the latest balance information and account status.
    """
    try:
        # This will need to be implemented in the service
        return {
            "message": "Account refresh functionality coming soon",
            "account_id": account_id,
            "force_refresh": request.force_refresh,
            "include_balances": request.include_balances
        }
    except Exception as e:
        logger.error(f"Error refreshing account {account_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh account"
        )

# ==========================================
# Account History and Analytics Routes
# ==========================================

@router.get("/{account_id}/balance-history")
async def get_account_balance_history(
    account_id: str,
    days: int = Query(default=30, ge=1, le=365, description="Number of days of history (1-365)"),
    current_user: User = Depends(get_current_user),
    plaid_service: PlaidService = Depends(get_plaid_service)
):
    """
    Get balance history for a specific account.
    
    Returns historical balance data for the specified time period.
    """
    try:
        # Verify user owns the account
        accounts = await plaid_service.get_user_accounts_db(current_user.id)
        account = next((acc for acc in accounts if acc.id == account_id), None)
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        # This will need to be implemented in the service
        return {
            "message": "Balance history functionality coming soon",
            "account_id": account_id,
            "days_requested": days
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching balance history for account {account_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch balance history"
        )

@router.get("/{account_id}/status-history")
async def get_account_status_history(
    account_id: str,
    limit: int = Query(default=50, ge=1, le=200, description="Number of status changes to return"),
    current_user: User = Depends(get_current_user),
    plaid_service: PlaidService = Depends(get_plaid_service)
):
    """
    Get status change history for a specific account.
    
    Returns history of account status changes, verification updates, etc.
    """
    try:
        # Verify user owns the account
        accounts = await plaid_service.get_user_accounts_db(current_user.id)
        account = next((acc for acc in accounts if acc.id == account_id), None)
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        # This will need to be implemented in the service
        return {
            "message": "Status history functionality coming soon",
            "account_id": account_id,
            "limit": limit
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching status history for account {account_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch status history"
        )

# ==========================================
# Account Sync and Management Routes
# ==========================================

@router.post("/sync")
async def sync_all_accounts(
    current_user: User = Depends(get_current_user),
    plaid_service: PlaidService = Depends(get_plaid_service)
):
    """
    Sync all accounts for the current user.
    
    This will refresh account information and balances for all items.
    """
    try:
        # This will need to be implemented to sync all user accounts
        return {
            "message": "Account sync functionality coming soon",
            "user_id": current_user.id
        }
    except Exception as e:
        logger.error(f"Error syncing accounts for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync accounts"
        )


@router.put("/{account_id}/settings")
async def update_account_inversion_settings(
    account_id: str,
    settings: AccountInversionSettingsRequest,
    current_user: User = Depends(get_current_user),
    plaid_service: PlaidService = Depends(get_plaid_service)
):
    """
    Update account inversion display settings.
    
    This allows users to configure how balances and transaction amounts
    are displayed for this account. Inversion only affects the view layer,
    not the underlying data stored from Plaid.
    
    Args:
        account_id: The account ID to update settings for
        settings: The inversion settings to apply
        
    Returns:
        Updated account information with new settings
    """
    try:
        updated_account = await plaid_service.accounts_service.update_account_inversion_settings(
            account_id=account_id,
            user_id=str(current_user.id),
            invert_balance=settings.invert_balance,
            invert_transactions=settings.invert_transactions
        )
        
        return updated_account
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating account settings for {account_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update account settings"
        )
