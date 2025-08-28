"""
Plaid Transactions Router

Router endpoints for transaction retrieval and management.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from datetime import datetime
import logging

from api.authentication.deps import get_current_user
from api.users.models import User
from ..service import PlaidService, get_plaid_service
from ..items.models import PlaidEnvironment
from .models import (
    TransactionsRequest, 
    TransactionsResponse, 
    TransactionsRefreshRequest,
    PlaidTransactionResponse
)
from .service import TransactionsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/transactions", tags=["Plaid Transactions"])

# ==========================================
# Database-backed Transaction Routes
# ==========================================

@router.get("/")
async def get_transactions_db(
    account_id: Optional[int] = Query(default=None, description="Filter by account ID"),
    start_date: Optional[datetime] = Query(default=None, description="Start date for transactions"),
    end_date: Optional[datetime] = Query(default=None, description="End date for transactions"),
    limit: int = Query(default=100, ge=1, le=500, description="Number of transactions to retrieve"),
    offset: int = Query(default=0, ge=0, description="Number of transactions to skip"),
    environment: Optional[PlaidEnvironment] = Query(default=None, description="Filter by environment"),
    current_user: User = Depends(get_current_user),
    plaid_service: PlaidService = Depends(get_plaid_service)
):
    """Get transactions for the current user from database"""
    env_str = environment.value if environment else None
    transactions, total = await plaid_service.get_user_transactions_db(
        current_user.id,
        account_id=account_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )
    
    return {
        "transactions": transactions,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + len(transactions) < total
    }

# ==========================================
# Legacy insecure transaction endpoints removed for security compliance
# All transaction access must go through proper authenticated endpoints in the main transactions router
# ==========================================
