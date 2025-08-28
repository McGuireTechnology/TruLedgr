"""
Accounts Router

FastAPI router for account management endpoints.
Provides REST API for CRUD operations on accounts.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer
from sqlmodel.ext.asyncio.session import AsyncSession
import logging

from api.deps import get_db, get_current_user
from .service import account_service
from .schemas import (
    AccountCreate,
    AccountUpdate,
    AccountResponse,
    AccountListResponse,
    AccountSummaryResponse,
    AccountSearchRequest,
    AccountBalanceUpdate,
    PlaidAccountSyncRequest,
    AccountBalanceHistoryResponse,
    AccountStatusHistoryResponse
)
from .models import AccountType, AccountSubtype, AccountSource, HolderCategory, AccountStatus

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

# Create router
router = APIRouter(
    prefix="/accounts",
    tags=["accounts"],
    dependencies=[Depends(security)]
)


@router.post("/", response_model=AccountResponse)
async def create_account(
    request: AccountCreate,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new account

    Args:
        request: Account creation data
        session: Database session
        current_user: Current authenticated user

    Returns:
        Created account response
    """
    try:
        # Override user_id with current user if not provided
        if not request.user_id:
            request.user_id = current_user["id"]

        # Ensure user can only create accounts for themselves (unless admin)
        if request.user_id != current_user["id"] and current_user.get("role") != "admin":
            raise HTTPException(
                status_code=403,
                detail="Cannot create accounts for other users"
            )

        account = await account_service.create_account(session, request)
        logger.info(f"Created account {account.id} for user {current_user['id']}")
        return account

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating account: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create account"
        )


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: str,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get account by ID

    Args:
        account_id: Account ID
        session: Database session
        current_user: Current authenticated user

    Returns:
        Account response
    """
    try:
        account = await account_service.get_account_by_id(session, account_id)

        if not account:
            raise HTTPException(
                status_code=404,
                detail="Account not found"
            )

        # Check ownership
        if account.user_id != current_user["id"] and current_user.get("role") != "admin":
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )

        return account

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving account {account_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve account"
        )


@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: str,
    request: AccountUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing account

    Args:
        account_id: Account ID
        request: Update data
        session: Database session
        current_user: Current authenticated user

    Returns:
        Updated account response
    """
    try:
        # Check if account exists and user has access
        existing = await account_service.get_account_by_id(session, account_id)
        if not existing:
            raise HTTPException(
                status_code=404,
                detail="Account not found"
            )

        if existing.user_id != current_user["id"] and current_user.get("role") != "admin":
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )

        account = await account_service.update_account(session, account_id, request)

        if not account:
            raise HTTPException(
                status_code=404,
                detail="Account not found"
            )

        logger.info(f"Updated account {account_id} by user {current_user['id']}")
        return account

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating account {account_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update account"
        )


@router.delete("/{account_id}")
async def delete_account(
    account_id: str,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete (soft delete) an account

    Args:
        account_id: Account ID
        session: Database session
        current_user: Current authenticated user

    Returns:
        Success message
    """
    try:
        # Check if account exists and user has access
        existing = await account_service.get_account_by_id(session, account_id)
        if not existing:
            raise HTTPException(
                status_code=404,
                detail="Account not found"
            )

        if existing.user_id != current_user["id"] and current_user.get("role") != "admin":
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )

        success = await account_service.delete_account(session, account_id)

        if not success:
            raise HTTPException(
                status_code=404,
                detail="Account not found"
            )

        logger.info(f"Deleted account {account_id} by user {current_user['id']}")
        return {"message": "Account deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting account {account_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete account"
        )


@router.get("/", response_model=List[AccountResponse])
async def list_accounts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    name: Optional[str] = None,
    account_type: Optional[str] = None,
    account_subtype: Optional[str] = None,
    primary_source: Optional[str] = None,
    institution_id: Optional[str] = None,
    holder_category: Optional[str] = None,
    status: Optional[str] = None,
    is_closed: Optional[bool] = None,
    plaid_enabled: Optional[bool] = None,
    min_balance: Optional[float] = None,
    max_balance: Optional[float] = None,
    tags: Optional[str] = None,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List accounts with optional filtering

    Args:
        Various filter parameters
        session: Database session
        current_user: Current authenticated user

    Returns:
        List of account responses
    """
    try:
        # Build search request
        search_request = AccountSearchRequest(
            name=name,
            account_type=AccountType(account_type) if account_type else None,
            account_subtype=AccountSubtype(account_subtype) if account_subtype else None,
            primary_source=AccountSource(primary_source) if primary_source else None,
            institution_id=institution_id,
            holder_category=HolderCategory(holder_category) if holder_category else None,
            status=AccountStatus(status) if status else None,
            is_closed=is_closed,
            plaid_enabled=plaid_enabled,
            min_balance=min_balance,
            max_balance=max_balance,
            tags=tags
        )

        accounts, total = await account_service.list_accounts(
            session, skip, limit, search_request
        )

        # Filter by user access (unless admin)
        if current_user.get("role") != "admin":
            accounts = [acc for acc in accounts if acc.user_id == current_user["id"]]

        return accounts

    except Exception as e:
        logger.error(f"Error listing accounts: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve accounts"
        )


@router.get("/institution/{institution_id}", response_model=List[AccountResponse])
async def get_accounts_by_institution(
    institution_id: str,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all accounts for a specific institution

    Args:
        institution_id: Institution ID
        session: Database session
        current_user: Current authenticated user

    Returns:
        List of account responses
    """
    try:
        accounts = await account_service.get_accounts_by_institution(session, institution_id)

        # Filter by user access (unless admin)
        if current_user.get("role") != "admin":
            accounts = [acc for acc in accounts if acc.user_id == current_user["id"]]

        return accounts

    except Exception as e:
        logger.error(f"Error retrieving accounts for institution {institution_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve accounts"
        )


@router.get("/user/{user_id}", response_model=List[AccountResponse])
async def get_accounts_by_user(
    user_id: str,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all accounts for a specific user

    Args:
        user_id: User ID
        session: Database session
        current_user: Current authenticated user

    Returns:
        List of account responses
    """
    try:
        # Check access permissions
        if user_id != current_user["id"] and current_user.get("role") != "admin":
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )

        accounts = await account_service.get_accounts_by_user(session, user_id)
        return accounts

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving accounts for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve accounts"
        )


@router.put("/{account_id}/balance", response_model=AccountResponse)
async def update_account_balance(
    account_id: str,
    balance_update: AccountBalanceUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update account balance

    Args:
        account_id: Account ID
        balance_update: Balance update data
        session: Database session
        current_user: Current authenticated user

    Returns:
        Updated account response
    """
    try:
        # Check if account exists and user has access
        existing = await account_service.get_account_by_id(session, account_id)
        if not existing:
            raise HTTPException(
                status_code=404,
                detail="Account not found"
            )

        if existing.user_id != current_user["id"] and current_user.get("role") != "admin":
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )

        account = await account_service.update_account_balance(
            session, account_id, balance_update
        )

        if not account:
            raise HTTPException(
                status_code=404,
                detail="Account not found"
            )

        logger.info(f"Updated balance for account {account_id} by user {current_user['id']}")
        return account

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating account balance {account_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update account balance"
        )


@router.get("/summary", response_model=AccountSummaryResponse)
async def get_account_summary(
    user_id: Optional[str] = None,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get account summary statistics

    Args:
        user_id: Optional user ID to filter by
        session: Database session
        current_user: Current authenticated user

    Returns:
        Account summary response
    """
    try:
        # Set user_id to current user if not specified
        if not user_id:
            user_id = current_user["id"]
        elif user_id != current_user["id"] and current_user.get("role") != "admin":
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )

        summary = await account_service.get_account_summary(session, user_id)
        return summary

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting account summary: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get account summary"
        )


@router.post("/sync-plaid", response_model=AccountResponse)
async def sync_plaid_account(
    request: PlaidAccountSyncRequest,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Sync account data from Plaid

    Args:
        request: Plaid sync request
        session: Database session
        current_user: Current authenticated user

    Returns:
        Synced account response
    """
    try:
        # Check if user has access to the account
        if request.user_id and request.user_id != current_user["id"] and current_user.get("role") != "admin":
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )

        account = await account_service.sync_plaid_account(session, request)
        logger.info(f"Synced Plaid account {request.plaid_account_id} by user {current_user['id']}")
        return account

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing Plaid account: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to sync Plaid account"
        )


# Include router in main API
__all__ = ["router"]
