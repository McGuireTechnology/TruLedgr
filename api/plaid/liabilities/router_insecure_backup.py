"""
Plaid Liabilities Router

Router endpoints for credit cards, mortgages, and student loans.
"""

from fastapi import APIRouter, HTTPException, Depends
import logging

from .models import LiabilitiesRequest, LiabilitiesResponse
from .service import LiabilitiesService
from ..service import get_plaid_service
from ..models import Account

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/liabilities", response_model=LiabilitiesResponse, summary="Get Liabilities Data")
async def get_liabilities(
    request: LiabilitiesRequest,
    environment: str = "production",
    plaid_service = Depends(get_plaid_service)
):
    """
    Retrieve detailed liabilities information for supported account types.
    
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
        
        result = await plaid_service.get_liabilities(
            access_token=request.access_token,
            account_ids=request.account_ids,
            environment=environment
        )
        
        logger.info(f"Retrieved liabilities data for {len(result['accounts'])} accounts from {environment}")
        
        return LiabilitiesResponse(
            accounts=[Account(**account) for account in result['accounts']],
            liabilities=result['liabilities'], 
            request_id=result['request_id']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve liabilities from {environment}: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "liabilities_retrieval_failed",
                "message": "Unable to retrieve liabilities data",
                "details": str(e),
                "environment": environment
            }
        )
