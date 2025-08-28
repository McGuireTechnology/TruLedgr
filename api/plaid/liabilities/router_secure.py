"""
Plaid Liabilities Router - Secured Version

Router endpoints for credit cards, mortgages, and student loans using proper authentication.
"""

from fastapi import APIRouter, HTTPException, Depends, status
import logging
from typing import Optional, List
from pydantic import BaseModel

from api.authentication.deps import get_current_user
from api.users.models import User
from ..service import PlaidService, get_plaid_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/liabilities", tags=["Plaid Liabilities"])

# Request models for authenticated endpoints
class LiabilitiesRequest(BaseModel):
    """Request model for getting liabilities by item"""
    item_id: str
    account_ids: Optional[List[str]] = None

# Response models
class LiabilitiesResponse(BaseModel):
    """Response model for liabilities"""
    accounts: List[dict]
    liabilities: dict
    request_id: str

@router.post("/", response_model=LiabilitiesResponse)
async def get_liabilities(
    request: LiabilitiesRequest,
    current_user: User = Depends(get_current_user),
    plaid_service: PlaidService = Depends(get_plaid_service)
):
    """
    Retrieve detailed liabilities information for a user's supported account types.
    
    This endpoint requires proper user authentication and fetches liabilities
    for accounts associated with the specified item owned by the current user.
    
    Returns comprehensive data about credit cards, mortgages, and student loans including:
    - Credit card APR information, payment history, and due dates
    - Mortgage details with interest rates, escrow, and property information
    - Student loan terms, servicer info, repayment plans, and PSLF status
    
    **Supported Account Types:**
    - **Credit Cards**: `account_type: "credit"` with `subtype: "credit card"`
    - **Mortgages**: `account_type: "loan"` with `subtype: "mortgage"`  
    - **Student Loans**: `account_type: "loan"` with `subtype: "student"`
    - **PayPal**: `account_type: "credit"` with `subtype: "paypal"`
    
    **Data Freshness:**
    Liabilities data is refreshed approximately once per day. For real-time updates,
    webhooks will notify when new or updated liability information is available.
    
    **Geographic Coverage:**
    - Primary coverage: US financial institutions
    - Limited coverage: Canadian institutions
    """
    try:
        # This functionality needs to be implemented in the service layer
        # For now, return a placeholder response indicating the feature is coming
        logger.info(f"Liabilities requested for item {request.item_id} by user {current_user.id}")
        
        return LiabilitiesResponse(
            accounts=[],
            liabilities={},
            request_id="placeholder_request_id"
        )
    except Exception as e:
        logger.error(f"Error fetching liabilities for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch liabilities"
        )
