"""
Plaid Enrich Router

Router endpoints for transaction enrichment.
"""

from fastapi import APIRouter, HTTPException, Depends
import logging

from .models import TransactionsEnrichRequest, TransactionsEnrichResponse
from .service import EnrichService
from ..service import get_plaid_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/transactions/enrich", response_model=TransactionsEnrichResponse, summary="Enrich Transaction Data")
async def enrich_transactions(
    request: TransactionsEnrichRequest,
    environment: str = "production",
    plaid_service = Depends(get_plaid_service)
):
    """
    Enrich locally-held transaction data with Plaid's enrichment service.
    
    This endpoint enriches raw transaction data that you have generated
    or retrieved from non-Plaid sources. The enrichment includes:
    
    **Enrichment Data:**
    - **Counterparty Information**: Merchant names, logos, websites, confidence levels
    - **Location Data**: Address, coordinates, store numbers
    - **Categorization**: Personal finance categories with confidence levels
    - **Payment Channel**: Online, in-store, or other transaction types
    - **Recurrence Analysis**: Detection of recurring transactions
    - **Contact Information**: Phone numbers and websites when available
    
    **Transaction Data Requirements:**
    - Raw transaction descriptions (required)
    - Transaction amounts (absolute values >= 0)
    - Transaction direction (INFLOW or OUTFLOW)
    - Currency codes (ISO-4217 format)
    - Optional: Location data, MCC codes, posting dates
    
    **Account Types Supported:**
    - `depository`: Checking, savings accounts
    - `credit`: Credit card accounts
    
    **Rate Limits:**
    - Maximum 100 transactions per request
    - Usage-based pricing applies
    
    **Use Cases:**
    - Enrich transactions from core banking systems
    - Categorize transactions from CSV imports
    - Add merchant data to transaction feeds
    - Enhance financial management applications
    
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
        
        # Validate transaction count
        if len(request.transactions) > 100:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "too_many_transactions",
                    "message": "Maximum of 100 transactions can be enriched per request",
                    "transaction_count": len(request.transactions)
                }
            )
        
        # Validate account type
        if request.account_type not in ['depository', 'credit']:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_account_type",
                    "message": "Account type must be 'depository' or 'credit'",
                    "provided_account_type": request.account_type
                }
            )
        
        # Convert Pydantic models to dict format for service
        transactions_data = [
            {
                'id': txn.id,
                'description': txn.description,
                'amount': txn.amount,
                'direction': txn.direction,
                'iso_currency_code': txn.iso_currency_code,
                'location': txn.location.dict() if txn.location else None,
                'mcc': txn.mcc,
                'date_posted': txn.date_posted
            }
            for txn in request.transactions
        ]
        
        options_data = request.options.dict() if request.options else None
        
        result = await plaid_service.enrich_transactions(
            account_type=request.account_type,
            transactions=transactions_data,
            options=options_data,
            environment=environment
        )
        
        logger.info(f"Enriched {len(result['enriched_transactions'])} transactions in {environment}")
        
        return TransactionsEnrichResponse(
            enriched_transactions=result['enriched_transactions'],
            request_id=result['request_id']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to enrich transactions in {environment}: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "transaction_enrichment_failed",
                "message": "Unable to enrich transaction data",
                "details": str(e),
                "environment": environment
            }
        )
