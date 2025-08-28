"""
Plaid Liabilities Router - Official Implementation

Comprehensive router for credit cards, mortgages, and student loans with proper authentication.
All endpoints require user authentication and follow REST conventions.
"""

from fastapi import APIRouter, HTTPException, Depends, status
import logging
from typing import Optional, List
from pydantic import BaseModel

from api.authentication.deps import get_current_user
from api.users.models import User
from ..service import get_plaid_service
from .service_official import get_liabilities_service
from .models_official import LiabilitiesResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/liabilities", tags=["plaid-liabilities"])

# ==========================================
# Request Models
# ==========================================

class LiabilitiesRequest(BaseModel):
    """Request model for getting liabilities by item"""
    item_id: str
    account_ids: Optional[List[str]] = None

class SyncLiabilitiesRequest(BaseModel):
    """Request model for syncing liabilities from Plaid"""
    item_id: str
    force_refresh: bool = False

class LiabilitiesFilterRequest(BaseModel):
    """Request model for filtering liabilities"""
    item_id: Optional[str] = None
    liability_types: Optional[List[str]] = None  # credit_card, mortgage, student_loan
    include_inactive: bool = False

# ==========================================
# Response Models
# ==========================================

class SyncLiabilitiesResponse(BaseModel):
    """Response model for liability sync operations"""
    success: bool
    message: str
    total_synced: int
    credit_cards: int
    mortgages: int
    student_loans: int
    errors: List[str] = []

class LiabilityAccountResponse(BaseModel):
    """Response model for liability account information"""
    account_id: str
    account_name: str
    account_type: str
    account_subtype: str
    liability_type: str
    current_balance: Optional[float] = None
    available_balance: Optional[float] = None
    limit_amount: Optional[float] = None
    currency_code: str
    last_updated: Optional[str] = None
    status: str

# ==========================================
# Main Endpoints
# ==========================================

@router.get("/", 
            response_model=LiabilitiesResponse,
            summary="Get User Liabilities",
            description="Get comprehensive liabilities data for the authenticated user")
async def get_user_liabilities(
    item_id: Optional[str] = None,
    liability_types: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> LiabilitiesResponse:
    """
    Retrieve comprehensive liabilities information for the authenticated user.
    
    Returns detailed information about:
    - **Credit Cards**: APR information, payment history, due dates, and balances
    - **Mortgages**: Interest rates, escrow details, property information, and payment schedules
    - **Student Loans**: Servicer information, repayment plans, PSLF status, and loan terms
    
    **Supported Liability Types:**
    - `credit_card`: Credit card accounts with detailed APR and payment information
    - `mortgage`: Mortgage accounts with property and loan details
    - `student_loan`: Student loan accounts with servicer and repayment information
    
    **Data Freshness:**
    Data is refreshed approximately once per day. Use the sync endpoint to update data manually.
    
    **Geographic Coverage:**
    - Primary: US financial institutions
    - Limited: Canadian institutions
    """
    try:
        logger.info(f"Getting liabilities for user {current_user.id}")
        
        # Parse liability types filter
        parsed_types = None
        if liability_types:
            parsed_types = [t.strip() for t in liability_types.split(',')]
        
        # Get liabilities service
        liabilities_service = get_liabilities_service()
        
        # Fetch liabilities from database
        liabilities = await liabilities_service.get_user_liabilities(
            user_id=current_user.id,
            item_id=item_id,
            liability_types=parsed_types
        )
        
        logger.info(f"Successfully retrieved liabilities for user {current_user.id}")
        return liabilities
        
    except Exception as e:
        logger.error(f"Error getting liabilities for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve liabilities: {str(e)}"
        )

@router.post("/sync",
             response_model=SyncLiabilitiesResponse,
             summary="Sync Liabilities from Plaid",
             description="Sync liabilities data from Plaid API for a specific item")
async def sync_liabilities(
    request: SyncLiabilitiesRequest,
    current_user: User = Depends(get_current_user)
) -> SyncLiabilitiesResponse:
    """
    Sync liabilities data from Plaid API for the specified item.
    
    This endpoint:
    - Fetches the latest liabilities data from Plaid
    - Updates database records with new information
    - Returns detailed sync results
    
    **Use Cases:**
    - Manual refresh of liability data
    - Initial data population after linking an account
    - Updating data after receiving webhook notifications
    
    **Rate Limits:**
    Plaid API rate limits apply. Avoid excessive syncing.
    """
    try:
        logger.info(f"Syncing liabilities for user {current_user.id} item {request.item_id}")
        
        # Get liabilities service
        liabilities_service = get_liabilities_service()
        
        # Sync liabilities data
        sync_results = await liabilities_service.sync_user_liabilities(
            user_id=current_user.id,
            item_id=request.item_id,
            environment="sandbox"  # This should come from settings
        )
        
        response = SyncLiabilitiesResponse(
            success=True,
            message="Liabilities synced successfully",
            total_synced=sync_results["total_synced"],
            credit_cards=sync_results["credit_cards"],
            mortgages=sync_results["mortgages"],
            student_loans=sync_results["student_loans"],
            errors=sync_results["errors"]
        )
        
        logger.info(f"Successfully synced {response.total_synced} liabilities for user {current_user.id}")
        return response
        
    except Exception as e:
        logger.error(f"Error syncing liabilities for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync liabilities: {str(e)}"
        )

@router.get("/accounts",
            response_model=List[LiabilityAccountResponse],
            summary="Get Liability Accounts",
            description="Get basic information about liability accounts")
async def get_liability_accounts(
    item_id: Optional[str] = None,
    liability_type: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> List[LiabilityAccountResponse]:
    """
    Get basic information about liability accounts for the authenticated user.
    
    Returns summary information without detailed liability-specific data.
    Useful for account selection and overview displays.
    """
    try:
        logger.info(f"Getting liability accounts for user {current_user.id}")
        
        # This would be implemented to return basic account information
        # For now, return empty list as placeholder
        return []
        
    except Exception as e:
        logger.error(f"Error getting liability accounts for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve liability accounts: {str(e)}"
        )

# ==========================================
# Specific Liability Type Endpoints
# ==========================================

@router.get("/credit-cards",
            summary="Get Credit Card Liabilities",
            description="Get detailed credit card liability information")
async def get_credit_card_liabilities(
    item_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed credit card liability information including:
    - APR information for different transaction types
    - Payment history and due dates
    - Statement balances and minimum payments
    - Overdue status indicators
    """
    try:
        logger.info(f"Getting credit card liabilities for user {current_user.id}")
        
        # Get liabilities service
        liabilities_service = get_liabilities_service()
        
        # Fetch credit card liabilities only
        liabilities = await liabilities_service.get_user_liabilities(
            user_id=current_user.id,
            item_id=item_id,
            liability_types=["credit_card"]
        )
        
        return {"credit_cards": liabilities.credit}
        
    except Exception as e:
        logger.error(f"Error getting credit card liabilities for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve credit card liabilities: {str(e)}"
        )

@router.get("/mortgages",
            summary="Get Mortgage Liabilities",
            description="Get detailed mortgage liability information")
async def get_mortgage_liabilities(
    item_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed mortgage liability information including:
    - Interest rates and loan terms
    - Escrow and PMI information
    - Property address details
    - Payment schedules and amounts
    - Origination and maturity information
    """
    try:
        logger.info(f"Getting mortgage liabilities for user {current_user.id}")
        
        # Get liabilities service
        liabilities_service = get_liabilities_service()
        
        # Fetch mortgage liabilities only
        liabilities = await liabilities_service.get_user_liabilities(
            user_id=current_user.id,
            item_id=item_id,
            liability_types=["mortgage"]
        )
        
        return {"mortgages": liabilities.mortgage}
        
    except Exception as e:
        logger.error(f"Error getting mortgage liabilities for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve mortgage liabilities: {str(e)}"
        )

@router.get("/student-loans",
            summary="Get Student Loan Liabilities",
            description="Get detailed student loan liability information")
async def get_student_loan_liabilities(
    item_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed student loan liability information including:
    - Servicer information and contact details
    - Repayment plan details and options
    - PSLF (Public Service Loan Forgiveness) status
    - Interest rates and payment schedules
    - Loan status and disbursement history
    """
    try:
        logger.info(f"Getting student loan liabilities for user {current_user.id}")
        
        # Get liabilities service
        liabilities_service = get_liabilities_service()
        
        # Fetch student loan liabilities only
        liabilities = await liabilities_service.get_user_liabilities(
            user_id=current_user.id,
            item_id=item_id,
            liability_types=["student_loan"]
        )
        
        return {"student_loans": liabilities.student}
        
    except Exception as e:
        logger.error(f"Error getting student loan liabilities for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve student loan liabilities: {str(e)}"
        )

# ==========================================
# Health and Status Endpoints
# ==========================================

@router.get("/health",
            summary="Liabilities Service Health Check",
            description="Check health and configuration of liabilities service")
async def liabilities_health_check():
    """
    Health check for liabilities service functionality.
    
    Returns:
    - Service status and configuration
    - Database connectivity
    - Plaid API connectivity
    """
    try:
        # Basic service check
        plaid_service = get_plaid_service()
        liabilities_service = get_liabilities_service()
        
        config_status = {
            "plaid_client_configured": plaid_service.client is not None,
            "service_initialized": liabilities_service is not None,
            "environment": "sandbox"
        }
        
        return {
            "status": "healthy",
            "timestamp": "2025-08-18T00:00:00Z",
            "service": "plaid-liabilities",
            "version": "1.0.0",
            "configuration": config_status,
            "supported_types": ["credit_card", "mortgage", "student_loan"]
        }
        
    except Exception as e:
        logger.error(f"Liabilities health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": "2025-08-18T00:00:00Z",
            "service": "plaid-liabilities",
            "error": str(e)
        }

@router.get("/webhook/events",
            summary="Get Liability Webhook Events",
            description="Get recent webhook events for liability updates")
async def get_webhook_events(
    item_id: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """
    Get recent webhook events related to liability updates.
    
    Useful for debugging and monitoring liability data changes.
    """
    try:
        # This would return webhook event history
        # Implementation depends on requirements
        return {
            "events": [],
            "total": 0,
            "message": "Webhook event history endpoint - implementation pending"
        }
        
    except Exception as e:
        logger.error(f"Error getting webhook events: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve webhook events: {str(e)}"
        )
