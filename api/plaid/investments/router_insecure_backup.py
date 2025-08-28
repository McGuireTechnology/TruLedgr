"""
Plaid Investments Router

Router endpoints for investment holdings and transactions.
"""

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import logging
from typing import Optional, List
from pydantic import BaseModel

from api.authentication.deps import get_current_user
from api.users.models import User
from .models import (
    InvestmentsHoldingsResponse,
    InvestmentsTransactionsResponse,
    InvestmentsRefreshResponse
)
from .service import InvestmentsService
from ..service import get_plaid_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/investments", tags=["Plaid Investments"])

# Request models for authenticated endpoints
class InvestmentsHoldingsRequest(BaseModel):
    """Request model for getting investment holdings by item"""
    item_id: str
    account_ids: Optional[List[str]] = None

class InvestmentsTransactionsRequest(BaseModel):
    """Request model for getting investment transactions by item"""
    item_id: str
    start_date: str
    end_date: str
    account_ids: Optional[List[str]] = None
    offset: int = 0
    count: int = 100

class InvestmentsRefreshRequest(BaseModel):
    """Request model for refreshing investment data"""
    item_id: str

@router.post("/holdings", response_model=InvestmentsHoldingsResponse, summary="Get Investment Holdings")
async def get_investments_holdings(
    request: InvestmentsHoldingsRequest,
    current_user: User = Depends(get_current_user),
    plaid_service = Depends(get_plaid_service)
):
    """
    Get investment holdings for connected investment accounts.
    
    Returns detailed information about:
    - Current holdings and positions
    - Securities information (stocks, bonds, options, etc.)
    - Institution pricing and valuations
    - Portfolio balances and performance
    - Vested quantities for equity compensation
    
    **Investment Account Types Supported:**
    - Brokerage accounts
    - 401(k) and retirement accounts  
    - IRA accounts (Traditional, Roth, SEP)
    - 529 education savings plans
    - HSA investment accounts
    
    **Environment Parameter:**
    - `production`: Use live Plaid environment (default)
    - `sandbox`: Use Plaid sandbox environment for testing
    """
    try:
        if not plaid_service.is_environment_available(environment):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_environment",
                    "message": f"Environment '{environment}' is not available",
                    "available_environments": plaid_service.get_available_environments()
                }
            )
        
        result = await plaid_service.get_investments_holdings(
            access_token=request.access_token,
            account_ids=request.account_ids,
            environment=environment
        )
        
        logger.info(f"Retrieved {len(result['holdings'])} investment holdings from {environment}")
        
        return InvestmentsHoldingsResponse(
            accounts=result['accounts'],
            holdings=result['holdings'], 
            securities=result['securities'],
            request_id=result['request_id'],
            is_investments_fallback_item=result.get('is_investments_fallback_item', False)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve investment holdings from {environment}: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "investments_holdings_failed",
                "message": "Unable to retrieve investment holdings",
                "details": str(e),
                "environment": environment
            }
        )

@router.post("/investments/transactions", response_model=InvestmentsTransactionsResponse, summary="Get Investment Transactions")
async def get_investments_transactions(
    request: InvestmentsTransactionsRequest,
    environment: str = "production",
    plaid_service = Depends(get_plaid_service)
):
    """
    Get investment transactions for connected investment accounts.
    
    Returns up to 24 months of transaction history including:
    - Buy and sell transactions
    - Dividend payments and distributions
    - Fees and charges
    - Corporate actions (splits, mergers, etc.)
    - Cash movements and transfers
    
    **Transaction Types Supported:**
    - `buy`: Security purchases
    - `sell`: Security sales
    - `cash`: Cash movements (dividends, interest, deposits)
    - `fee`: Account and transaction fees
    - `transfer`: Transfers between accounts or positions
    - `cancel`: Transaction cancellations
    
    **Pagination:**
    Use `count` and `offset` parameters to paginate through large result sets.
    
    **Environment Parameter:**
    - `production`: Use live Plaid environment (default)
    - `sandbox`: Use Plaid sandbox environment for testing
    """
    try:
        if not plaid_service.is_environment_available(environment):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_environment",
                    "message": f"Environment '{environment}' is not available",
                    "available_environments": plaid_service.get_available_environments()
                }
            )
        
        result = await plaid_service.get_investments_transactions(
            access_token=request.access_token,
            start_date=datetime.combine(request.start_date, datetime.min.time()),
            end_date=datetime.combine(request.end_date, datetime.min.time()),
            account_ids=request.account_ids,
            count=request.count,
            offset=request.offset,
            async_update=request.async_update,
            environment=environment
        )
        
        logger.info(f"Retrieved {len(result['investment_transactions'])} investment transactions from {environment}")
        
        return InvestmentsTransactionsResponse(
            accounts=result['accounts'],
            investment_transactions=result['investment_transactions'],
            securities=result['securities'],
            total_investment_transactions=result['total_investment_transactions'],
            request_id=result['request_id'],
            is_investments_fallback_item=result.get('is_investments_fallback_item', False)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve investment transactions from {environment}: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "investments_transactions_failed",
                "message": "Unable to retrieve investment transactions",
                "details": str(e),
                "environment": environment
            }
        )

@router.post("/investments/refresh", response_model=InvestmentsRefreshResponse, summary="Refresh Investment Data")
async def refresh_investments(
    request: InvestmentsRefreshRequest,
    environment: str = "production",
    plaid_service = Depends(get_plaid_service)
):
    """
    Trigger on-demand refresh of investment data.
    
    This endpoint initiates an immediate extraction to fetch the newest
    investment holdings and transactions. This is in addition to the
    automatic periodic extractions that occur throughout the day.
    
    **When to Use:**
    - After users make trades or transfers
    - When real-time portfolio updates are needed
    - Before generating reports or analytics
    
    **Webhooks Fired:**
    - `HOLDINGS: DEFAULT_UPDATE` if new holdings are detected
    - `INVESTMENTS_TRANSACTIONS: DEFAULT_UPDATE` if new transactions are detected
    
    **Rate Limiting:**
    This is a premium endpoint with usage-based pricing. Use judiciously.
    
    **Environment Parameter:**
    - `production`: Use live Plaid environment (default)
    - `sandbox`: Use Plaid sandbox environment for testing
    """
    try:
        if not plaid_service.is_environment_available(environment):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_environment", 
                    "message": f"Environment '{environment}' is not available",
                    "available_environments": plaid_service.get_available_environments()
                }
            )
        
        result = await plaid_service.refresh_investments(
            access_token=request.access_token,
            environment=environment
        )
        
        logger.info(f"Investment refresh initiated for environment {environment}")
        
        return InvestmentsRefreshResponse(request_id=result['request_id'])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to refresh investments in {environment}: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "investments_refresh_failed",
                "message": "Unable to refresh investment data",
                "details": str(e),
                "environment": environment
            }
        )
