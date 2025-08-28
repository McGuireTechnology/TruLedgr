"""
Transactions Router

FastAPI router for transaction management endpoints.
Provides REST API for transaction CRUD operations, search, reconciliation, and bulk operations.
"""

from typing import List, Optional, Dict, Any
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from api.deps import get_db, get_current_user
from .service import transaction_service, user_category_service, category_rule_service
from .schemas import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionListResponse,
    TransactionSummaryResponse,
    TransactionSearchRequest,
    TransactionReconciliationRequest,
    TransactionReconciliationResponse,
    RecurringTransactionCreate,
    RecurringTransactionResponse,
    PlaidTransactionSyncRequest,
    BulkTransactionUpdateRequest,
    TransactionDuplicateCheckRequest,
    TransactionDuplicateResponse,
    UserCategoryCreate,
    UserCategoryUpdate,
    UserCategoryResponse,
    UserCategoryTreeResponse,
    UserCategoryListResponse,
    UserCategoryMoveRequest,
    CategoryRuleCreate,
    CategoryRuleUpdate,
    CategoryRuleResponse,
    CategoryRuleListResponse,
    CategoryRuleTestRequest,
    CategoryRuleTestResponse
)
from .models import TransactionCategory, TransactionSubcategory, TransactionStatus, TransactionSource

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
    responses={
        404: {"description": "Transaction not found"},
        400: {"description": "Invalid request"},
        500: {"description": "Internal server error"}
    }
)


@router.post(
    "/",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Transaction",
    description="Create a new transaction with automatic duplicate detection"
)
async def create_transaction(
    request: TransactionCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TransactionResponse:
    """
    Create a new transaction

    - **request**: Transaction creation data
    - **current_user**: Authenticated user
    - **db**: Database session

    Returns the created transaction with duplicate detection results
    """
    try:
        # Ensure user owns the transaction
        if request.user_id != current_user["id"]:
            raise HTTPException(
                status_code=403,
                detail="Cannot create transaction for another user"
            )

        result = await transaction_service.create_transaction(db, request)
        logger.info(f"Created transaction {result.id} for user {current_user['id']}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating transaction: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create transaction"
        )


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    summary="Get Transaction",
    description="Retrieve a specific transaction by ID"
)
async def get_transaction(
    transaction_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TransactionResponse:
    """
    Get transaction by ID

    - **transaction_id**: Transaction identifier
    - **current_user**: Authenticated user
    - **db**: Database session

    Returns the transaction if found and user has access
    """
    try:
        transaction = await transaction_service.get_transaction_by_id(db, transaction_id)

        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )

        # Check if user owns the transaction
        if transaction.user_id != current_user["id"]:
            raise HTTPException(
                status_code=403,
                detail="Access denied to transaction"
            )

        return transaction

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving transaction {transaction_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve transaction"
        )


@router.put(
    "/{transaction_id}",
    response_model=TransactionResponse,
    summary="Update Transaction",
    description="Update an existing transaction"
)
async def update_transaction(
    transaction_id: str,
    request: TransactionUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TransactionResponse:
    """
    Update transaction

    - **transaction_id**: Transaction identifier
    - **request**: Update data
    - **current_user**: Authenticated user
    - **db**: Database session

    Returns the updated transaction
    """
    try:
        # First check if transaction exists and user has access
        existing = await transaction_service.get_transaction_by_id(db, transaction_id)

        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )

        if existing.user_id != current_user["id"]:
            raise HTTPException(
                status_code=403,
                detail="Access denied to transaction"
            )

        result = await transaction_service.update_transaction(
            db, transaction_id, request, current_user["id"]
        )

        if not result:
            raise HTTPException(
                status_code=404,
                detail="Transaction not found"
            )

        logger.info(f"Updated transaction {transaction_id} by user {current_user['id']}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating transaction {transaction_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update transaction"
        )


@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Transaction",
    description="Soft delete a transaction (mark as cancelled)"
)
async def delete_transaction(
    transaction_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete transaction (soft delete)

    - **transaction_id**: Transaction identifier
    - **current_user**: Authenticated user
    - **db**: Database session

    Returns 204 No Content on success
    """
    try:
        # First check if transaction exists and user has access
        existing = await transaction_service.get_transaction_by_id(db, transaction_id)

        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )

        if existing.user_id != current_user["id"]:
            raise HTTPException(
                status_code=403,
                detail="Access denied to transaction"
            )

        success = await transaction_service.delete_transaction(
            db, transaction_id, current_user["id"]
        )

        if not success:
            raise HTTPException(
                status_code=404,
                detail="Transaction not found"
            )

        logger.info(f"Deleted transaction {transaction_id} by user {current_user['id']}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting transaction {transaction_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete transaction"
        )


@router.get(
    "/",
    response_model=TransactionListResponse,
    summary="List Transactions",
    description="List transactions with advanced filtering and pagination"
)
async def list_transactions(
    # Pagination
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),

    # Date filtering
    start_date: Optional[date] = Query(None, description="Start date for filtering"),
    end_date: Optional[date] = Query(None, description="End date for filtering"),

    # Basic filtering
    account_id: Optional[str] = Query(None, description="Filter by account ID"),
    institution_id: Optional[str] = Query(None, description="Filter by institution ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    subcategory: Optional[str] = Query(None, description="Filter by subcategory"),
    status: Optional[str] = Query(None, description="Filter by status"),
    source: Optional[str] = Query(None, description="Filter by source"),

    # Advanced filtering
    min_amount: Optional[float] = Query(None, description="Minimum transaction amount"),
    max_amount: Optional[float] = Query(None, description="Maximum transaction amount"),
    search_text: Optional[str] = Query(None, description="Search in name, description, merchant"),
    merchant_name: Optional[str] = Query(None, description="Filter by merchant name"),
    merchant_entity_id: Optional[str] = Query(None, description="Filter by merchant entity ID"),
    is_pending: Optional[bool] = Query(None, description="Filter by pending status"),
    is_reconciled: Optional[bool] = Query(None, description="Filter by reconciliation status"),
    is_recurring: Optional[bool] = Query(None, description="Filter by recurring status"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),

    # Sorting
    sort_by: Optional[str] = Query("transaction_date", description="Field to sort by"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$", description="Sort order"),

    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TransactionListResponse:
    """
    List transactions with comprehensive filtering

    Supports pagination, date ranges, amount ranges, text search, and categorization filters
    """
    try:
        # Build search request
        search_request = TransactionSearchRequest(
            start_date=start_date,
            end_date=end_date,
            min_amount=min_amount,
            max_amount=max_amount,
            category=TransactionCategory(category) if category else None,
            subcategory=TransactionSubcategory(subcategory) if subcategory else None,
            custom_category=None,  # Not exposed in query params for now
            status=TransactionStatus(status) if status else None,
            is_pending=is_pending,
            is_reconciled=is_reconciled,
            source=TransactionSource(source) if source else None,
            plaid_transaction_id=None,  # Not exposed in query params for now
            account_id=account_id,
            institution_id=institution_id,
            user_id=current_user["id"],  # Ensure user can only see their own transactions
            search_text=search_text,
            merchant_name=merchant_name,
            merchant_entity_id=merchant_entity_id,
            is_recurring=is_recurring,
            recurrence_id=None,  # Not exposed in query params for now
            tags=tags,
            sort_by=sort_by,
            sort_order=sort_order
        )

        transactions, total = await transaction_service.list_transactions(
            db, skip, limit, search_request
        )

        return TransactionListResponse(
            transactions=transactions,
            total=total,
            skip=skip,
            limit=limit
        )

    except Exception as e:
        logger.error(f"Error listing transactions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve transactions"
        )


@router.get(
    "/summary",
    response_model=TransactionSummaryResponse,
    summary="Transaction Summary",
    description="Get transaction summary statistics and breakdowns"
)
async def get_transaction_summary(
    user_id: Optional[str] = Query(None, description="User ID (admin only)"),
    start_date: Optional[date] = Query(None, description="Start date for summary"),
    end_date: Optional[date] = Query(None, description="End date for summary"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TransactionSummaryResponse:
    """
    Get transaction summary with statistics

    Returns comprehensive statistics including totals, breakdowns by category/source,
    and reconciliation status
    """
    try:
        # Admin can specify user_id, regular users see their own data
        target_user_id = user_id if current_user.get("role") == "admin" else current_user["id"]

        # If admin specifies different user, ensure they have permission
        if user_id and user_id != current_user["id"] and current_user.get("role") != "admin":
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )

        summary = await transaction_service.get_transaction_summary(
            db, target_user_id, start_date, end_date
        )

        return summary

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transaction summary: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get transaction summary"
        )


@router.post(
    "/reconcile",
    response_model=TransactionReconciliationResponse,
    summary="Reconcile Transactions",
    description="Perform transaction reconciliation for an account"
)
async def reconcile_transactions(
    request: TransactionReconciliationRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TransactionReconciliationResponse:
    """
    Reconcile transactions for an account

    Compares statement balance with calculated balance from transactions
    and marks transactions as reconciled
    """
    try:
        # TODO: Add permission check to ensure user owns the account
        # This would require checking account ownership through accounts service

        result = await transaction_service.reconcile_transactions(
            db, request, current_user["id"]
        )

        logger.info(f"Reconciliation completed for account {request.account_id} by user {current_user['id']}")
        return result

    except Exception as e:
        logger.error(f"Error performing reconciliation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to perform reconciliation"
        )


@router.post(
    "/bulk-update",
    response_model=List[TransactionResponse],
    summary="Bulk Update Transactions",
    description="Update multiple transactions at once"
)
async def bulk_update_transactions(
    request: BulkTransactionUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[TransactionResponse]:
    """
    Bulk update multiple transactions

    Useful for batch operations like categorization or status updates
    """
    try:
        # TODO: Add permission checks for each transaction

        if not request.transaction_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No transaction IDs provided"
            )

        if len(request.transaction_ids) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update more than 100 transactions at once"
            )

        result = await transaction_service.bulk_update_transactions(
            db, request, current_user["id"]
        )

        logger.info(f"Bulk updated {len(result)} transactions by user {current_user['id']}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error performing bulk update: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to perform bulk update"
        )


@router.post(
    "/check-duplicates",
    response_model=TransactionDuplicateResponse,
    summary="Check for Duplicates",
    description="Check if a transaction might be a duplicate"
)
async def check_duplicates(
    request: TransactionDuplicateCheckRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TransactionDuplicateResponse:
    """
    Check for potential duplicate transactions

    Useful before creating new transactions to avoid duplicates
    """
    try:
        # Ensure user owns the account
        # TODO: Add account ownership check

        result = await transaction_service.check_duplicates(db, request)
        return result

    except Exception as e:
        logger.error(f"Error checking for duplicates: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to check for duplicates"
        )


@router.post(
    "/sync-plaid",
    summary="Sync Plaid Transactions",
    description="Sync transactions from Plaid (placeholder for future implementation)"
)
async def sync_plaid_transactions(
    request: PlaidTransactionSyncRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Sync transactions from Plaid

    This is a placeholder endpoint for future Plaid integration.
    The actual implementation would integrate with the existing Plaid transactions module.
    """
    try:
        # TODO: Implement Plaid sync logic
        # This would involve:
        # 1. Calling Plaid API to get new transactions
        # 2. Processing and normalizing the data
        # 3. Creating/updating transactions in our system
        # 4. Handling duplicates and conflicts

        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Plaid sync not yet implemented"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing Plaid transactions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to sync Plaid transactions"
        )


@router.post(
    "/recurring",
    response_model=RecurringTransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Recurring Transaction",
    description="Create a recurring transaction pattern"
)
async def create_recurring_transaction(
    request: RecurringTransactionCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> RecurringTransactionResponse:
    """
    Create a recurring transaction pattern

    This is a placeholder for future recurring transaction functionality
    """
    try:
        # TODO: Implement recurring transaction creation
        # This would involve:
        # 1. Creating RecurringTransaction record
        # 2. Setting up pattern detection
        # 3. Linking to existing transactions

        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Recurring transaction creation not yet implemented"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating recurring transaction: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create recurring transaction"
        )


# User Category Routes

@router.post(
    "/categories",
    response_model=UserCategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create User Category",
    description="Create a new user-defined transaction category"
)
async def create_user_category(
    request: UserCategoryCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserCategoryResponse:
    """
    Create a new user category

    - **request**: Category creation data
    - **current_user**: Authenticated user
    - **db**: Database session

    Returns the created category
    """
    try:
        # Ensure user owns the category
        if request.user_id != current_user["id"]:
            raise HTTPException(
                status_code=403,
                detail="Cannot create category for another user"
            )

        result = await user_category_service.create_category(db, request)
        logger.info(f"Created category {result.id} for user {current_user['id']}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating category: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create category"
        )


@router.get(
    "/categories/{category_id}",
    response_model=UserCategoryResponse,
    summary="Get User Category",
    description="Retrieve a specific user category by ID"
)
async def get_user_category(
    category_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserCategoryResponse:
    """
    Get user category by ID

    - **category_id**: Category identifier
    - **current_user**: Authenticated user
    - **db**: Database session

    Returns the category if found and user has access
    """
    try:
        category = await user_category_service.get_category_by_id(db, category_id)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

        # Check if user owns the category
        if category.user_id != current_user["id"]:
            raise HTTPException(
                status_code=403,
                detail="Access denied to category"
            )

        return category

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving category {category_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve category"
        )


@router.put(
    "/categories/{category_id}",
    response_model=UserCategoryResponse,
    summary="Update User Category",
    description="Update an existing user category"
)
async def update_user_category(
    category_id: str,
    request: UserCategoryUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserCategoryResponse:
    """
    Update user category

    - **category_id**: Category identifier
    - **request**: Update data
    - **current_user**: Authenticated user
    - **db**: Database session

    Returns the updated category
    """
    try:
        # First check if category exists and user has access
        existing = await user_category_service.get_category_by_id(db, category_id)

        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

        if existing.user_id != current_user["id"]:
            raise HTTPException(
                status_code=403,
                detail="Access denied to category"
            )

        result = await user_category_service.update_category(db, category_id, request)

        if not result:
            raise HTTPException(
                status_code=404,
                detail="Category not found"
            )

        logger.info(f"Updated category {category_id} by user {current_user['id']}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating category {category_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update category"
        )


@router.delete(
    "/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete User Category",
    description="Delete a user category and optionally reassign transactions"
)
async def delete_user_category(
    category_id: str,
    reassign_to: Optional[str] = Query(None, description="Category ID to reassign transactions to"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete user category

    - **category_id**: Category identifier
    - **reassign_to**: Optional category ID to reassign transactions to
    - **current_user**: Authenticated user
    - **db**: Database session

    Returns 204 No Content on success
    """
    try:
        # First check if category exists and user has access
        existing = await user_category_service.get_category_by_id(db, category_id)

        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

        if existing.user_id != current_user["id"]:
            raise HTTPException(
                status_code=403,
                detail="Access denied to category"
            )

        success = await user_category_service.delete_category(db, category_id, reassign_to)

        if not success:
            raise HTTPException(
                status_code=404,
                detail="Category not found"
            )

        logger.info(f"Deleted category {category_id} by user {current_user['id']}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting category {category_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete category"
        )


@router.get(
    "/categories",
    response_model=UserCategoryListResponse,
    summary="List User Categories",
    description="List user categories with pagination"
)
async def list_user_categories(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    include_inactive: bool = Query(False, description="Include inactive categories"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserCategoryListResponse:
    """
    List user categories

    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    - **include_inactive**: Whether to include inactive categories
    - **current_user**: Authenticated user
    - **db**: Database session

    Returns paginated list of user's categories
    """
    try:
        categories, total = await user_category_service.list_categories(
            db, current_user["id"], skip, limit, include_inactive
        )

        return UserCategoryListResponse(
            categories=categories,
            total=total,
            skip=skip,
            limit=limit
        )

    except Exception as e:
        logger.error(f"Error listing categories for user {current_user['id']}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve categories"
        )


@router.get(
    "/categories/tree",
    response_model=List[UserCategoryTreeResponse],
    summary="Get Category Tree",
    description="Get hierarchical category tree for the user"
)
async def get_category_tree(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[UserCategoryTreeResponse]:
    """
    Get category tree

    - **current_user**: Authenticated user
    - **db**: Database session

    Returns hierarchical tree of user's categories
    """
    try:
        tree = await user_category_service.get_category_tree(db, current_user["id"])
        return tree

    except Exception as e:
        logger.error(f"Error getting category tree for user {current_user['id']}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get category tree"
        )


@router.post(
    "/categories/{category_id}/move",
    response_model=UserCategoryResponse,
    summary="Move User Category",
    description="Move a category to a new parent in the hierarchy"
)
async def move_user_category(
    category_id: str,
    request: UserCategoryMoveRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserCategoryResponse:
    """
    Move user category

    - **category_id**: Category identifier
    - **request**: Move request data
    - **current_user**: Authenticated user
    - **db**: Database session

    Returns the moved category
    """
    try:
        # First check if category exists and user has access
        existing = await user_category_service.get_category_by_id(db, category_id)

        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

        if existing.user_id != current_user["id"]:
            raise HTTPException(
                status_code=403,
                detail="Access denied to category"
            )

        result = await user_category_service.move_category(
            db, category_id, request.new_parent_id, request.sort_order
        )

        if not result:
            raise HTTPException(
                status_code=404,
                detail="Category not found"
            )

        logger.info(f"Moved category {category_id} by user {current_user['id']}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error moving category {category_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to move category"
        )


# Category Rule Routes

@router.post(
    "/rules",
    response_model=CategoryRuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Category Rule",
    description="Create a new category rule for automatic categorization"
)
async def create_category_rule(
    request: CategoryRuleCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> CategoryRuleResponse:
    """
    Create a new category rule

    - **request**: Rule creation data
    - **current_user**: Authenticated user
    - **db**: Database session

    Returns the created rule
    """
    try:
        # Ensure user owns the rule
        if request.user_id != current_user["id"]:
            raise HTTPException(
                status_code=403,
                detail="Cannot create rule for another user"
            )

        result = await category_rule_service.create_rule(db, request)
        logger.info(f"Created rule {result.id} for user {current_user['id']}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating rule: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create rule"
        )


@router.get(
    "/rules/{rule_id}",
    response_model=CategoryRuleResponse,
    summary="Get Category Rule",
    description="Retrieve a specific category rule by ID"
)
async def get_category_rule(
    rule_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> CategoryRuleResponse:
    """
    Get category rule by ID

    - **rule_id**: Rule identifier
    - **current_user**: Authenticated user
    - **db**: Database session

    Returns the rule if found and user has access
    """
    try:
        rule = await category_rule_service.get_rule_by_id(db, rule_id)

        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rule not found"
            )

        # Check if user owns the rule
        if rule.user_id != current_user["id"]:
            raise HTTPException(
                status_code=403,
                detail="Access denied to rule"
            )

        return rule

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving rule {rule_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve rule"
        )


@router.put(
    "/rules/{rule_id}",
    response_model=CategoryRuleResponse,
    summary="Update Category Rule",
    description="Update an existing category rule"
)
async def update_category_rule(
    rule_id: str,
    request: CategoryRuleUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> CategoryRuleResponse:
    """
    Update category rule

    - **rule_id**: Rule identifier
    - **request**: Update data
    - **current_user**: Authenticated user
    - **db**: Database session

    Returns the updated rule
    """
    try:
        # First check if rule exists and user has access
        existing = await category_rule_service.get_rule_by_id(db, rule_id)

        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rule not found"
            )

        if existing.user_id != current_user["id"]:
            raise HTTPException(
                status_code=403,
                detail="Access denied to rule"
            )

        result = await category_rule_service.update_rule(db, rule_id, request)

        if not result:
            raise HTTPException(
                status_code=404,
                detail="Rule not found"
            )

        logger.info(f"Updated rule {rule_id} by user {current_user['id']}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating rule {rule_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update rule"
        )


@router.delete(
    "/rules/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Category Rule",
    description="Delete a category rule"
)
async def delete_category_rule(
    rule_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete category rule

    - **rule_id**: Rule identifier
    - **current_user**: Authenticated user
    - **db**: Database session

    Returns 204 No Content on success
    """
    try:
        # First check if rule exists and user has access
        existing = await category_rule_service.get_rule_by_id(db, rule_id)

        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rule not found"
            )

        if existing.user_id != current_user["id"]:
            raise HTTPException(
                status_code=403,
                detail="Access denied to rule"
            )

        success = await category_rule_service.delete_rule(db, rule_id)

        if not success:
            raise HTTPException(
                status_code=404,
                detail="Rule not found"
            )

        logger.info(f"Deleted rule {rule_id} by user {current_user['id']}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting rule {rule_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete rule"
        )


@router.get(
    "/rules",
    response_model=CategoryRuleListResponse,
    summary="List Category Rules",
    description="List category rules with pagination"
)
async def list_category_rules(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    include_inactive: bool = Query(False, description="Include inactive rules"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> CategoryRuleListResponse:
    """
    List category rules

    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    - **include_inactive**: Whether to include inactive rules
    - **current_user**: Authenticated user
    - **db**: Database session

    Returns paginated list of user's rules
    """
    try:
        rules, total = await category_rule_service.list_rules(
            db, current_user["id"], skip, limit, include_inactive
        )

        return CategoryRuleListResponse(
            rules=rules,
            total=total,
            skip=skip,
            limit=limit
        )

    except Exception as e:
        logger.error(f"Error listing rules for user {current_user['id']}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve rules"
        )


@router.post(
    "/rules/{rule_id}/test",
    response_model=CategoryRuleTestResponse,
    summary="Test Category Rule",
    description="Test a category rule against specific transactions"
)
async def test_category_rule(
    rule_id: str,
    request: CategoryRuleTestRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> CategoryRuleTestResponse:
    """
    Test category rule

    - **rule_id**: Rule identifier
    - **request**: Test request data
    - **current_user**: Authenticated user
    - **db**: Database session

    Returns test results showing which transactions match the rule
    """
    try:
        # First check if rule exists and user has access
        existing = await category_rule_service.get_rule_by_id(db, rule_id)

        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rule not found"
            )

        if existing.user_id != current_user["id"]:
            raise HTTPException(
                status_code=403,
                detail="Access denied to rule"
            )

        result = await category_rule_service.test_rule(db, rule_id, request.transaction_ids)
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing rule {rule_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to test rule"
        )


# Export router
__all__ = ["router"]
