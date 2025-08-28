"""
Plaid Items Router

FastAPI endpoints for Item management and status operations.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import logging

from api.authentication.deps import get_current_user
from api.users.models import User
from ..service import PlaidService, get_plaid_service
from .models import PlaidEnvironment, PlaidItemResponse, PlaidItemCreateRequest
from ..accounts.models import PlaidAccountResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/items", tags=["Plaid Items"])

# Helper functions for ID handling
async def _get_item_by_ulid(plaid_service: PlaidService, user_id: int, item_ulid: str) -> Optional[PlaidItemResponse]:
    """Helper to find item by ULID from user's items"""
    items = await plaid_service.get_user_items_db(user_id)
    return next((item for item in items if item.id == item_ulid), None)

def _convert_ulid_to_legacy_id(item_ulid: str) -> int:
    """Temporary helper to convert ULID to legacy integer ID for service calls"""
    # This is a temporary workaround - the service layer should be updated to use ULIDs
    # For now, we'll use a hash-based approach to get a consistent integer
    import hashlib
    hash_obj = hashlib.md5(item_ulid.encode())
    return int(hash_obj.hexdigest()[:8], 16) % (2**31)  # Keep within int range

# Request models for item operations
class ItemUpdateWebhookRequest(BaseModel):
    """Request model for updating item webhook URL"""
    webhook_url: Optional[str] = None

class ItemRefreshRequest(BaseModel):
    """Request model for refreshing item data"""
    force_refresh: bool = False

# ==========================================
# Main Item Management Routes
# ==========================================

@router.post("/", response_model=PlaidItemResponse)
async def create_item(
    request: PlaidItemCreateRequest,
    current_user: User = Depends(get_current_user),
    plaid_service: PlaidService = Depends(get_plaid_service)
) -> PlaidItemResponse:
    """
    Create a new Plaid item from a public token.
    
    This endpoint exchanges a public token received from Plaid Link
    for an access token and creates a new item in the database.
    """
    try:
        result = await plaid_service.create_item_db(
            user_id=current_user.id,
            public_token=request.public_token
        )
        return result
    except Exception as e:
        logger.error(f"Error creating item for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create item: {str(e)}"
        )

@router.get("/", response_model=List[PlaidItemResponse])
async def get_items(
    current_user: User = Depends(get_current_user),
    plaid_service: PlaidService = Depends(get_plaid_service),
    environment: Optional[str] = Query(None, description="Filter by environment (sandbox/production)")
):
    """
    Get all Plaid items for the current user.
    
    Optionally filter by environment (sandbox or production).
    """
    try:
        items = await plaid_service.get_user_items_db(current_user.id)
        
        # Filter by environment if specified
        if environment:
            items = [item for item in items if item.environment == environment]
        
        return items
    except Exception as e:
        logger.error(f"Error fetching items for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch items"
        )

@router.get("/{item_id}", response_model=PlaidItemResponse)
async def get_item(
    item_id: str,
    current_user: User = Depends(get_current_user),
    plaid_service: PlaidService = Depends(get_plaid_service)
):
    """Get a specific Plaid item by ID."""
    try:
        # This will need to be implemented in the service
        # For now, get all items and filter
        items = await plaid_service.get_user_items_db(current_user.id)
        item = next((item for item in items if item.id == item_id), None)
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        
        return item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching item {item_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch item"
        )

@router.delete("/{item_id}")
async def delete_item(
    item_id: str,
    current_user: User = Depends(get_current_user),
    plaid_service: PlaidService = Depends(get_plaid_service)
):
    """
    Delete a Plaid item and all associated data.
    
    This action is irreversible and will remove all accounts,
    transactions, and other data associated with this item.
    """
    try:
        # Pass the ULID directly to the service (no conversion needed)
        success = await plaid_service.delete_item_db(current_user.id, item_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found or already deleted"
            )
        return {
            "message": "Item deleted successfully",
            "item_id": item_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting item {item_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item"
        )

@router.post("/{item_id}/webhook")
async def update_item_webhook(
    item_id: str,
    request: ItemUpdateWebhookRequest,
    current_user: User = Depends(get_current_user),
    plaid_service: PlaidService = Depends(get_plaid_service)
):
    """
    Update the webhook URL for a Plaid item.
    
    The webhook URL is used to receive notifications about item events
    such as transaction updates, errors, and consent expirations.
    """
    try:
        # This will need to be implemented in the service
        return {
            "message": "Webhook update functionality coming soon",
            "item_id": item_id,
            "webhook_url": request.webhook_url
        }
    except Exception as e:
        logger.error(f"Error updating webhook for item {item_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update webhook"
        )

@router.post("/{item_id}/refresh")
async def refresh_item(
    item_id: str,
    request: ItemRefreshRequest,
    current_user: User = Depends(get_current_user),
    plaid_service: PlaidService = Depends(get_plaid_service)
):
    """
    Refresh an item to get the latest data from the institution.
    
    This can help resolve connectivity issues or update item status.
    """
    try:
        # This will need to be implemented in the service
        return {
            "message": "Item refresh functionality coming soon",
            "item_id": item_id,
            "force_refresh": request.force_refresh
        }
    except Exception as e:
        logger.error(f"Error refreshing item {item_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh item"
        )

# ==========================================
# Item Data Sync Routes
# ==========================================

@router.post("/{item_id}/sync/accounts", response_model=List[PlaidAccountResponse])
async def sync_item_accounts(
    item_id: str,
    current_user: User = Depends(get_current_user),
    plaid_service: PlaidService = Depends(get_plaid_service)
):
    """
    Sync accounts for a specific item.
    
    This will fetch the latest account information from Plaid
    and update the local database.
    """
    try:
        # Pass the ULID directly to the service (no conversion needed)
        return await plaid_service.sync_item_accounts_db(current_user.id, item_id)
    except Exception as e:
        logger.error(f"Error syncing accounts for item {item_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync accounts"
        )

@router.post("/{item_id}/sync/transactions")
async def sync_item_transactions(
    item_id: str,
    days: int = Query(default=30, ge=1, le=730, description="Number of days to sync (1-730)"),
    current_user: User = Depends(get_current_user),
    plaid_service: PlaidService = Depends(get_plaid_service)
):
    """
    Sync transactions for a specific item.
    
    This will fetch transactions from the specified number of days ago
    until today and update the local database.
    """
    try:
        # Pass the ULID directly to the service (no conversion needed)
        count = await plaid_service.sync_item_transactions_db(current_user.id, item_id, days)
        return {
            "message": f"Successfully synced {count} transactions",
            "item_id": item_id,
            "transactions_synced": count,
            "days_synced": days
        }
    except Exception as e:
        logger.error(f"Error syncing transactions for item {item_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync transactions"
        )
