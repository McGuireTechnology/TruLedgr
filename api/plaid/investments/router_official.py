"""
Plaid Investments Router - Official Implementation

REST API endpoints for investment accounts, holdings, transactions, and securities.
Provides comprehensive investment data management with proper authentication.
"""

from datetime import date, datetime
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from api.authentication.deps import get_current_user
from api.db.deps import get_db
from api.users.models import User
from ..service import get_plaid_service
from .service_official import get_investments_service, InvestmentsService
from .models_official import (
    InvestmentHoldingsResponse,
    InvestmentTransactionsResponse,
    InvestmentAccountResponse,
    InvestmentHoldingResponse,
    InvestmentSecurityResponse,
    InvestmentTransactionResponse
)

router = APIRouter(prefix="/plaid/investments", tags=["investments"])


@router.post("/sync/holdings/{item_id}")
async def sync_holdings(
    item_id: str,
    current_user: User = Depends(get_current_user),
    investments_service: InvestmentsService = Depends(get_investments_service)
) -> Dict[str, Any]:
    """
    Sync investment holdings data from Plaid for a specific item.
    
    This endpoint fetches the latest holdings data from Plaid and stores it in the database.
    Holdings include securities owned, quantities, current values, and pricing information.
    
    Args:
        item_id: Plaid item ID to sync holdings for
        current_user: Authenticated user
        investments_service: Investments service dependency
        
    Returns:
        Sync results with counts of synced data and any errors
        
    Raises:
        HTTPException: If sync fails or item not found
    """
    try:
        sync_results = await investments_service.sync_holdings_data(
            user_id=current_user.id,
            item_id=item_id,
            environment="sandbox"
        )
        
        if not sync_results.get("success"):
            raise HTTPException(
                status_code=400,
                detail=f"Holdings sync failed: {sync_results.get('message', 'Unknown error')}"
            )
        
        return {
            "message": "Holdings synced successfully",
            "item_id": item_id,
            "results": sync_results
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Holdings sync failed: {str(e)}")


@router.post("/sync/transactions/{item_id}")
async def sync_transactions(
    item_id: str,
    start_date: str = Query(..., description="Start date for transactions (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date for transactions (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    investments_service: InvestmentsService = Depends(get_investments_service)
) -> Dict[str, Any]:
    """
    Sync investment transactions data from Plaid for a specific item and date range.
    
    This endpoint fetches investment transactions (buy, sell, dividend, etc.) from Plaid
    and stores them in the database for the specified date range.
    
    Args:
        item_id: Plaid item ID to sync transactions for
        start_date: Start date for transaction sync (YYYY-MM-DD)
        end_date: End date for transaction sync (YYYY-MM-DD)
        current_user: Authenticated user
        investments_service: Investments service dependency
        
    Returns:
        Sync results with counts of synced data and any errors
        
    Raises:
        HTTPException: If sync fails, item not found, or invalid date format
    """
    try:
        # Validate date format
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
        
        sync_results = await investments_service.sync_transactions_data(
            user_id=current_user.id,
            item_id=item_id,
            start_date=start_date,
            end_date=end_date,
            environment="sandbox"
        )
        
        if not sync_results.get("success"):
            raise HTTPException(
                status_code=400,
                detail=f"Transaction sync failed: {sync_results.get('message', 'Unknown error')}"
            )
        
        return {
            "message": "Investment transactions synced successfully",
            "item_id": item_id,
            "date_range": {
                "start_date": start_date,
                "end_date": end_date
            },
            "results": sync_results
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transaction sync failed: {str(e)}")


@router.get("/holdings", response_model=InvestmentHoldingsResponse)
async def get_holdings(
    item_id: Optional[str] = Query(None, description="Filter by specific Plaid item ID"),
    account_ids: Optional[str] = Query(None, description="Comma-separated list of account IDs to filter by"),
    current_user: User = Depends(get_current_user),
    investments_service: InvestmentsService = Depends(get_investments_service)
) -> InvestmentHoldingsResponse:
    """
    Get investment holdings for the authenticated user.
    
    Returns holdings data including securities owned, quantities, current values,
    and associated account and security information.
    
    Args:
        item_id: Optional Plaid item ID to filter results
        account_ids: Optional comma-separated account IDs to filter results
        current_user: Authenticated user
        investments_service: Investments service dependency
        
    Returns:
        Holdings response with accounts, holdings, and securities data
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        # Parse account IDs if provided
        account_ids_list = None
        if account_ids:
            account_ids_list = [acc_id.strip() for acc_id in account_ids.split(",") if acc_id.strip()]
        
        holdings_response = await investments_service.get_user_holdings(
            user_id=current_user.id,
            item_id=item_id,
            account_ids=account_ids_list
        )
        
        return holdings_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve holdings: {str(e)}")


@router.get("/transactions", response_model=InvestmentTransactionsResponse)
async def get_transactions(
    item_id: Optional[str] = Query(None, description="Filter by specific Plaid item ID"),
    account_ids: Optional[str] = Query(None, description="Comma-separated list of account IDs to filter by"),
    start_date: Optional[str] = Query(None, description="Filter transactions from this date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter transactions until this date (YYYY-MM-DD)"),
    transaction_types: Optional[str] = Query(None, description="Comma-separated list of transaction types to filter by"),
    count: int = Query(100, ge=1, le=500, description="Number of transactions to return (1-500)"),
    offset: int = Query(0, ge=0, description="Number of transactions to skip for pagination"),
    current_user: User = Depends(get_current_user),
    investments_service: InvestmentsService = Depends(get_investments_service)
) -> InvestmentTransactionsResponse:
    """
    Get investment transactions for the authenticated user.
    
    Returns transaction data including buy/sell orders, dividends, fees, and transfers
    with associated account and security information.
    
    Args:
        item_id: Optional Plaid item ID to filter results
        account_ids: Optional comma-separated account IDs to filter results
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
        transaction_types: Optional comma-separated transaction types filter
        count: Number of transactions to return (1-500)
        offset: Number of transactions to skip for pagination
        current_user: Authenticated user
        investments_service: Investments service dependency
        
    Returns:
        Transactions response with accounts, transactions, and securities data
        
    Raises:
        HTTPException: If retrieval fails or invalid parameters
    """
    try:
        # Validate date formats if provided
        if start_date:
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid start_date format. Use YYYY-MM-DD"
                )
        
        if end_date:
            try:
                datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid end_date format. Use YYYY-MM-DD"
                )
        
        # Parse account IDs if provided
        account_ids_list = None
        if account_ids:
            account_ids_list = [acc_id.strip() for acc_id in account_ids.split(",") if acc_id.strip()]
        
        # Parse transaction types if provided
        transaction_types_list = None
        if transaction_types:
            transaction_types_list = [tx_type.strip() for tx_type in transaction_types.split(",") if tx_type.strip()]
        
        transactions_response = await investments_service.get_user_transactions(
            user_id=current_user.id,
            item_id=item_id,
            account_ids=account_ids_list,
            start_date=start_date,
            end_date=end_date,
            transaction_types=transaction_types_list,
            count=count,
            offset=offset
        )
        
        return transactions_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve transactions: {str(e)}")


@router.post("/webhook/process")
async def process_webhook(
    webhook_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    investments_service: InvestmentsService = Depends(get_investments_service)
) -> Dict[str, Any]:
    """
    Process Plaid investment webhook events.
    
    Handles webhook notifications for holdings updates and transaction updates,
    triggering appropriate data sync operations.
    
    Args:
        webhook_data: Webhook payload from Plaid
        current_user: Authenticated user
        investments_service: Investments service dependency
        
    Returns:
        Processing result status
        
    Raises:
        HTTPException: If webhook processing fails
    """
    try:
        webhook_type = webhook_data.get("webhook_type")
        webhook_code = webhook_data.get("webhook_code")
        item_id = webhook_data.get("item_id")
        
        if not all([webhook_type, webhook_code, item_id]):
            raise HTTPException(
                status_code=400,
                detail="Missing required webhook fields: webhook_type, webhook_code, item_id"
            )
        
        # Validate webhook type for investments
        if webhook_type not in ["HOLDINGS", "INVESTMENTS_TRANSACTIONS"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid webhook type for investments: {webhook_type}"
            )
        
        success = await investments_service.process_webhook_event(
            webhook_type=webhook_type,
            webhook_code=webhook_code,
            item_id=item_id,
            webhook_data=webhook_data,
            environment="sandbox"
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Webhook processing failed"
            )
        
        return {
            "message": "Webhook processed successfully",
            "webhook_type": webhook_type,
            "webhook_code": webhook_code,
            "item_id": item_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")


@router.get("/accounts", response_model=List[InvestmentAccountResponse])
async def get_investment_accounts(
    item_id: Optional[str] = Query(None, description="Filter by specific Plaid item ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[InvestmentAccountResponse]:
    """
    Get investment accounts for the authenticated user.
    
    Returns a list of investment accounts with balance information,
    account types, and verification status.
    
    Args:
        item_id: Optional Plaid item ID to filter results
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List of investment account responses
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        from sqlmodel import select
        from .models_official import PlaidInvestmentAccount
        
        # Build query
        query = select(PlaidInvestmentAccount).where(
            PlaidInvestmentAccount.user_id == current_user.id,
            PlaidInvestmentAccount.status == "active"
        )
        
        if item_id:
            query = query.where(PlaidInvestmentAccount.item_id == item_id)
        
        accounts = db.exec(query).all()
        
        # Format response
        account_responses = []
        for account in accounts:
            account_responses.append(InvestmentAccountResponse(
                account_id=account.plaid_account_id,
                balances={
                    "available": account.available_balance,
                    "current": account.current_balance,
                    "limit": account.limit_amount,
                    "iso_currency_code": account.iso_currency_code,
                    "unofficial_currency_code": account.unofficial_currency_code,
                    "last_updated_datetime": account.last_updated_datetime.isoformat() if account.last_updated_datetime else None
                },
                mask=account.account_mask,
                name=account.account_name,
                official_name=account.account_official_name,
                type=account.account_type,
                subtype=account.account_subtype,
                verification_status=account.verification_status,
                persistent_account_id=account.persistent_account_id,
                holder_category=account.holder_category
            ))
        
        return account_responses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve investment accounts: {str(e)}")


@router.get("/securities", response_model=List[InvestmentSecurityResponse])
async def get_securities(
    security_ids: Optional[str] = Query(None, description="Comma-separated list of security IDs to filter by"),
    security_types: Optional[str] = Query(None, description="Comma-separated list of security types to filter by"),
    current_user: User = Depends(get_current_user),
    investments_service: InvestmentsService = Depends(get_investments_service),
    db: Session = Depends(get_db)
) -> List[InvestmentSecurityResponse]:
    """
    Get investment securities information.
    
    Returns security details including pricing, identifiers, and metadata
    for securities in the user's investment accounts.
    
    Args:
        security_ids: Optional comma-separated security IDs to filter by
        security_types: Optional comma-separated security types to filter by
        current_user: Authenticated user
        investments_service: Investments service dependency
        db: Database session
        
    Returns:
        List of investment security responses
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        from sqlmodel import select
        from .models_official import PlaidInvestmentSecurity
        
        # Build query - get securities that appear in user's holdings
        query = select(PlaidInvestmentSecurity).where(
            PlaidInvestmentSecurity.environment == "sandbox"
        )
        
        # Filter by security IDs if provided
        if security_ids:
            security_ids_list = [sec_id.strip() for sec_id in security_ids.split(",") if sec_id.strip()]
            if security_ids_list:
                query = query.where(PlaidInvestmentSecurity.security_id.in_(security_ids_list))
        
        # Filter by security types if provided
        if security_types:
            security_types_list = [sec_type.strip() for sec_type in security_types.split(",") if sec_type.strip()]
            if security_types_list:
                query = query.where(PlaidInvestmentSecurity.security_type.in_(security_types_list))
        
        securities = db.exec(query).all()
        
        # Format response
        security_responses = []
        for security in securities:
            security_response = await investments_service._format_security(db, security)
            security_responses.append(security_response)
        
        return security_responses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve securities: {str(e)}")


@router.get("/stats")
async def get_investment_stats(
    item_id: Optional[str] = Query(None, description="Filter by specific Plaid item ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get investment statistics for the authenticated user.
    
    Returns aggregated statistics including total portfolio value,
    number of accounts, holdings count, and recent transaction counts.
    
    Args:
        item_id: Optional Plaid item ID to filter results
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Investment statistics dictionary
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        from sqlmodel import select, func
        from .models_official import (
            PlaidInvestmentAccount,
            PlaidInvestmentHolding,
            PlaidInvestmentTransaction
        )
        
        stats = {}
        
        # Get account stats
        account_query = select(PlaidInvestmentAccount).where(
            PlaidInvestmentAccount.user_id == current_user.id,
            PlaidInvestmentAccount.status == "active"
        )
        
        if item_id:
            account_query = account_query.where(PlaidInvestmentAccount.item_id == item_id)
        
        accounts = db.exec(account_query).all()
        account_ids = [acc.plaid_account_id for acc in accounts]
        
        stats["accounts_count"] = len(accounts)
        
        # Calculate total portfolio value
        total_value = sum(acc.current_balance or 0 for acc in accounts)
        stats["total_portfolio_value"] = total_value
        
        # Get holdings stats
        if account_ids:
            holdings_query = select(PlaidInvestmentHolding).where(
                PlaidInvestmentHolding.user_id == current_user.id,
                PlaidInvestmentHolding.account_id.in_(account_ids),
                PlaidInvestmentHolding.status == "active"
            )
            
            holdings = db.exec(holdings_query).all()
            stats["holdings_count"] = len(holdings)
            
            # Calculate total holdings value
            holdings_value = sum(holding.institution_value or 0 for holding in holdings)
            stats["total_holdings_value"] = holdings_value
            
            # Get recent transactions count (last 30 days)
            from datetime import date, timedelta
            thirty_days_ago = date.today() - timedelta(days=30)
            
            transactions_query = select(PlaidInvestmentTransaction).where(
                PlaidInvestmentTransaction.user_id == current_user.id,
                PlaidInvestmentTransaction.account_id.in_(account_ids),
                PlaidInvestmentTransaction.transaction_date >= thirty_days_ago
            )
            
            recent_transactions = db.exec(transactions_query).all()
            stats["recent_transactions_count"] = len(recent_transactions)
        else:
            stats["holdings_count"] = 0
            stats["total_holdings_value"] = 0
            stats["recent_transactions_count"] = 0
        
        return {
            "user_id": current_user.id,
            "item_id": item_id,
            "statistics": stats,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve investment statistics: {str(e)}")
