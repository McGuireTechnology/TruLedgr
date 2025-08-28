"""
Plaid Webhooks Router

Router endpoints for webhook verification and processing.
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Header
from typing import Optional
import logging

from .models import (
    WebhookVerificationRequest, WebhookResponse, WebhookStatusResponse,
    ItemWebhookRequest, AuthWebhookRequest
)
from .service import WebhooksService
from ..transactions.models import TransactionsWebhookRequest
from ..investments.models import HoldingsWebhookRequest, InvestmentsTransactionsWebhookRequest
from ..liabilities.models import LiabilitiesWebhookRequest

logger = logging.getLogger(__name__)

router = APIRouter()

# Create webhooks service instance
webhooks_service = WebhooksService()

@router.get("/webhooks/status", response_model=WebhookStatusResponse, summary="Get Webhook Status")
async def get_webhook_status():
    """
    Get webhook configuration status and supported webhook types.
    
    Returns information about:
    - Whether webhooks are properly configured
    - Supported webhook types and codes
    - Webhook processing statistics
    """
    import os
    
    webhook_secret_set = bool(os.getenv('PLAID_WEBHOOK_SECRET'))
    
    return WebhookStatusResponse(
        webhook_configured=webhook_secret_set,
        webhook_secret_set=webhook_secret_set,
        supported_webhook_types=webhooks_service.get_webhook_types(),
        webhook_codes_by_type={
            webhook_type: webhooks_service.get_webhook_codes_for_type(webhook_type)
            for webhook_type in webhooks_service.get_webhook_types()
        },
        last_webhook_received=None,  # TODO: Implement webhook logging
        total_webhooks_processed=None  # TODO: Implement webhook logging
    )

@router.post("/webhooks/plaid", response_model=WebhookResponse, summary="Plaid Webhook Endpoint")
async def handle_plaid_webhook(
    request: Request,
    plaid_signature: Optional[str] = Header(None, alias="Plaid-Signature")
):
    """
    Handle incoming webhooks from Plaid.
    
    This endpoint receives notifications from Plaid about:
    - New transactions available
    - Account connection issues
    - Item errors requiring user attention
    - Authentication status changes
    
    **Security**: Webhooks are verified using HMAC-SHA256 signatures.
    Set PLAID_WEBHOOK_SECRET environment variable to enable verification.
    
    **Webhook Types Supported:**
    - `TRANSACTIONS`: Transaction updates and availability
    - `ITEM`: Item status changes and errors
    - `AUTH`: Account verification events  
    - `ASSETS`: Assets product events
    """
    try:
        # Get raw request body for signature verification
        request_body = await request.body()
        
        # Verify webhook signature
        if plaid_signature:
            is_valid = webhooks_service.verify_webhook(request_body, plaid_signature)
            if not is_valid:
                logger.warning("Invalid webhook signature received")
                raise HTTPException(
                    status_code=401,
                    detail={
                        "error": "invalid_signature",
                        "message": "Webhook signature verification failed"
                    }
                )
        else:
            logger.warning("Webhook received without signature - verification skipped")
        
        # Parse webhook payload
        try:
            payload = webhooks_service.parse_webhook_payload(request_body)
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_payload",
                    "message": str(e)
                }
            )
        
        # Extract webhook type and code
        webhook_type = payload.get('webhook_type')
        webhook_code = payload.get('webhook_code')
        item_id = payload.get('item_id')
        
        if not all([webhook_type, webhook_code, item_id]):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "missing_required_fields",
                    "message": "Webhook must include webhook_type, webhook_code, and item_id"
                }
            )
        
        logger.info(f"Processing Plaid webhook: {webhook_type}.{webhook_code} for item {item_id}")
        
        # Process the webhook (webhook_type and webhook_code are guaranteed to be strings here)
        result = await webhooks_service.handle_webhook_event(str(webhook_type), str(webhook_code), payload)
        
        return WebhookResponse(
            status=result.get('status', 'processed'),
            action=result.get('action'),
            item_id=item_id,
            message=result.get('message', 'Webhook processed successfully'),
            error=result.get('error'),
            details=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing webhook: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "webhook_processing_failed",
                "message": "Internal error processing webhook",
                "details": str(e)
            }
        )

@router.post("/webhooks/transactions", response_model=WebhookResponse, summary="Handle Transactions Webhook")
async def handle_transactions_webhook(webhook_data: TransactionsWebhookRequest):
    """
    Handle TRANSACTIONS webhook events specifically.
    
    This is a typed endpoint for processing transaction-related webhooks:
    - `INITIAL_UPDATE`: Historical transactions are ready
    - `HISTORICAL_UPDATE`: Historical transactions have been updated  
    - `DEFAULT_UPDATE`: New transactions are available
    
    **Note**: This endpoint is for testing or direct integration.
    The main `/webhooks/plaid` endpoint handles all webhook types.
    """
    try:
        payload = webhook_data.dict()
        result = await webhooks_service.handle_webhook_event(
            webhook_data.webhook_type,
            webhook_data.webhook_code,
            payload
        )
        
        return WebhookResponse(
            status=result.get('status', 'processed'),
            action=result.get('action'),
            item_id=webhook_data.item_id,
            message=result.get('message', 'Transaction webhook processed'),
            error=result.get('error'),
            details=result
        )
        
    except Exception as e:
        logger.error(f"Error processing transactions webhook: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "transactions_webhook_failed",
                "message": str(e)
            }
        )

@router.get("/webhooks/test", summary="Test Webhook Configuration")
async def test_webhook_configuration():
    """
    Test webhook configuration and return diagnostic information.
    
    This endpoint helps verify that:
    - Webhook secret is configured
    - Webhook endpoints are accessible
    - Signature verification works
    
    Useful for debugging webhook integration issues.
    """
    import os
    
    webhook_secret = os.getenv('PLAID_WEBHOOK_SECRET')
    
    # Test signature verification with dummy data
    test_payload = b'{"test": "webhook"}'
    test_signature = None
    
    if webhook_secret:
        import hmac
        import hashlib
        test_signature = hmac.new(
            webhook_secret.encode('utf-8'),
            test_payload,
            hashlib.sha256
        ).hexdigest()
    
    verification_test = webhooks_service.verify_webhook(test_payload, test_signature) if test_signature else None
    
    return {
        "webhook_secret_configured": bool(webhook_secret),
        "webhook_secret_length": len(webhook_secret) if webhook_secret else 0,
        "supported_webhook_types": webhooks_service.get_webhook_types(),
        "signature_verification_test": verification_test,
        "test_signature": test_signature,
        "webhook_url": "/plaid/webhooks/plaid",  # Relative to your API base URL
        "configuration_notes": [
            "Set PLAID_WEBHOOK_SECRET environment variable",
            "Configure webhook URL in Plaid Dashboard", 
            "Ensure webhook endpoint is publicly accessible",
            "Test with Plaid webhook simulator in Dashboard"
        ]
    }

@router.post("/webhooks/holdings", response_model=WebhookResponse, summary="Handle Holdings Webhook")
async def handle_holdings_webhook(webhook_data: HoldingsWebhookRequest):
    """
    Handle HOLDINGS webhook events specifically.
    
    This endpoint processes holdings-related webhooks:
    - `DEFAULT_UPDATE`: New or updated holdings detected
    
    Holdings webhooks fire when:
    - New securities are added to investment accounts
    - Existing holdings quantities or values change
    - Market prices are updated (typically after market close)
    
    **Note**: This endpoint is for testing or direct integration.
    The main `/webhooks/plaid` endpoint handles all webhook types.
    """
    try:
        payload = webhook_data.dict()
        result = await webhooks_service.handle_webhook_event(
            webhook_data.webhook_type,
            webhook_data.webhook_code,
            payload
        )
        
        return WebhookResponse(
            status=result.get('status', 'processed'),
            action=result.get('action'),
            item_id=webhook_data.item_id,
            message=result.get('message', 'Holdings webhook processed'),
            error=result.get('error'),
            details=result
        )
        
    except Exception as e:
        logger.error(f"Error processing holdings webhook: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "holdings_webhook_failed",
                "message": str(e)
            }
        )

@router.post("/webhooks/investments-transactions", response_model=WebhookResponse, summary="Handle Investment Transactions Webhook") 
async def handle_investments_transactions_webhook(webhook_data: InvestmentsTransactionsWebhookRequest):
    """
    Handle INVESTMENTS_TRANSACTIONS webhook events specifically.
    
    This endpoint processes investment transaction webhooks:
    - `DEFAULT_UPDATE`: New investment transactions available
    - `HISTORICAL_UPDATE`: Asynchronous data extraction completed
    
    Investment transaction webhooks fire when:
    - New trades, dividends, or fees are detected
    - Historical data extraction completes (for async_update flows)
    - Transaction cancellations occur
    
    **Webhook Codes:**
    - `DEFAULT_UPDATE`: Regular updates with new transactions
    - `HISTORICAL_UPDATE`: Initial historical data ready after async extraction
    
    **Note**: This endpoint is for testing or direct integration.
    The main `/webhooks/plaid` endpoint handles all webhook types.
    """
    try:
        payload = webhook_data.dict()
        result = await webhooks_service.handle_webhook_event(
            webhook_data.webhook_type,
            webhook_data.webhook_code,
            payload
        )
        
        return WebhookResponse(
            status=result.get('status', 'processed'),
            action=result.get('action'),
            item_id=webhook_data.item_id,
            message=result.get('message', 'Investment transactions webhook processed'),
            error=result.get('error'),
            details=result
        )
        
    except Exception as e:
        logger.error(f"Error processing investment transactions webhook: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "investments_transactions_webhook_failed",
                "message": str(e)
            }
        )

@router.post("/webhooks/liabilities", response_model=WebhookResponse, summary="Handle Liabilities Webhook")
async def handle_liabilities_webhook(webhook_data: LiabilitiesWebhookRequest):
    """
    Handle LIABILITIES webhook events specifically.
    
    This endpoint processes liabilities-specific webhooks:
    - `DEFAULT_UPDATE`: New or updated liability information is available
    
    **Webhook Data Includes:**
    - Account IDs with new liabilities detected
    - Account IDs with updated liability fields and what fields changed
    - Supports credit cards, mortgages, and student loans
    
    **Common Liability Updates:**
    - New loan accounts or credit cards
    - Changed payment due dates
    - Updated minimum payment amounts
    - Modified interest rates or APR changes
    - Loan status changes (deferment, forbearance, etc.)
    
    **Note**: This endpoint is for testing or direct integration.
    The main `/webhooks/plaid` endpoint handles all webhook types.
    """
    try:
        payload = webhook_data.dict()
        result = await webhooks_service.handle_webhook_event(
            webhook_data.webhook_type,
            webhook_data.webhook_code,
            payload
        )
        
        return WebhookResponse(
            status=result.get('status', 'processed'),
            action=result.get('action'),
            item_id=webhook_data.item_id,
            message=result.get('message', 'Liabilities webhook processed'),
            error=result.get('error'),
            details=result
        )
        
    except Exception as e:
        logger.error(f"Error processing liabilities webhook: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "liabilities_webhook_failed",
                "message": str(e)
            }
        )
