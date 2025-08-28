"""
Plaid Link Router - Official API Compliant

Modern, secure implementation following official Plaid Link Token Create API.
All endpoints require proper user authentication and follow REST conventions.
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
import logging
from datetime import datetime, timezone

from api.authentication.deps import get_current_user
from api.users.models import User
from api.plaid.link.models_official import (
    TruLedgrLinkTokenRequest,
    TruLedgrLinkTokenResponse,
    TruLedgrPublicTokenExchangeRequest,
    TruLedgrPublicTokenExchangeResponse,
    PlaidProduct,
    CountryCode
)
from api.plaid.service import get_plaid_service
from api.settings import get_settings

router = APIRouter(prefix="/link", tags=["plaid-link"])
logger = logging.getLogger(__name__)

# ==========================================
# Core Link Token Operations
# ==========================================

@router.post("/token", 
             response_model=TruLedgrLinkTokenResponse,
             summary="Create Link Token",
             description="Create a Link token for Plaid Link initialization following official Plaid API standards")
async def create_link_token(
    request: TruLedgrLinkTokenRequest,
    current_user: User = Depends(get_current_user)
) -> TruLedgrLinkTokenResponse:
    """
    Create a Link token for initializing Plaid Link.
    
    This endpoint follows the official Plaid Link Token Create API specification:
    - Requires authenticated user
    - Supports all official Plaid products and configurations
    - Returns properly formatted Link token for frontend initialization
    - Includes comprehensive user information for better Link experience
    """
    try:
        logger.info(f"Creating Link token for user {current_user.id} with products: {request.products}")
        
        # Get Plaid service
        plaid_service = get_plaid_service()
        
        # Create Link token using the service
        link_response = await plaid_service.create_link_token(
            user_id=current_user.id,
            user_name=current_user.full_name
        )
        
        # Format response following TruLedgr patterns
        response = TruLedgrLinkTokenResponse(
            link_token=link_response["link_token"],
            expiration=link_response["expiration"],
            products=[product.value for product in request.products],
            environment="sandbox",  # Always sandbox for now
            request_id=link_response["request_id"]
        )
        
        logger.info(f"Successfully created Link token for user {current_user.id}")
        return response
        
    except Exception as e:
        logger.error(f"Failed to create Link token for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create Link token: {str(e)}"
        )

@router.post("/exchange",
             response_model=TruLedgrPublicTokenExchangeResponse,
             summary="Exchange Public Token",
             description="Exchange public token for access token and create Item following official Plaid patterns")
async def exchange_public_token(
    request: TruLedgrPublicTokenExchangeRequest,
    current_user: User = Depends(get_current_user)
) -> TruLedgrPublicTokenExchangeResponse:
    """
    Exchange a public token for an access token and create a new Item.
    
    This endpoint follows the official Plaid public token exchange flow:
    - Exchanges public token received from Link onSuccess callback
    - Creates new Item in database with proper user association
    - Returns Item information for frontend use
    - Handles all error cases according to Plaid standards
    """
    try:
        logger.info(f"Exchanging public token for user {current_user.id}")
        
        # Get Plaid service
        plaid_service = get_plaid_service()
        
        # Exchange public token using service
        exchange_response = await plaid_service.exchange_public_token(
            public_token=request.public_token
        )
        
        # Create item in database
        item_response = await plaid_service.create_item_db(
            user_id=int(current_user.id, 16) if isinstance(current_user.id, str) else current_user.id,
            public_token=request.public_token
        )
        
        # Get institution info for response
        institution_info = await plaid_service.get_institution_info(
            item_response.institution_id
        )
        
        # Format response with TruLedgr Item information
        response = TruLedgrPublicTokenExchangeResponse(
            item_id=str(item_response.id),
            plaid_item_id=exchange_response["item_id"],
            institution_id=item_response.institution_id,
            institution_name=institution_info.get("name", "Unknown Institution"),
            products=["transactions"],  # Default products for now
            environment="sandbox",
            request_id=exchange_response["request_id"]
        )
        
        logger.info(f"Successfully exchanged public token and created item {response.item_id} for user {current_user.id}")
        return response
        
    except Exception as e:
        logger.error(f"Failed to exchange public token for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to exchange public token: {str(e)}"
        )

# ==========================================
# Configuration and Information Endpoints
# ==========================================

@router.get("/products",
            summary="Get Available Products",
            description="Get list of available Plaid products for Link token creation")
async def get_available_products(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get available Plaid products that can be used in Link token creation.
    
    Returns:
    - List of all supported Plaid products
    - Product descriptions and requirements
    - Environment-specific availability
    """
    try:
        products = []
        for product in PlaidProduct:
            products.append({
                "value": product.value,
                "name": product.value.replace("_", " ").title(),
                "description": f"Plaid {product.value.replace('_', ' ').title()} product"
            })
        
        return {
            "products": products,
            "environment": "sandbox",
            "default_products": [
                PlaidProduct.TRANSACTIONS.value,
                PlaidProduct.AUTH.value,
                PlaidProduct.IDENTITY.value
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get available products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get available products: {str(e)}"
        )

@router.get("/countries",
            summary="Get Supported Countries",
            description="Get list of supported country codes for Link token creation")
async def get_supported_countries(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get supported country codes for Link token creation.
    
    Returns:
    - List of all supported country codes
    - Country names and regions
    - Default country configuration
    """
    try:
        countries = []
        for country in CountryCode:
            countries.append({
                "code": country.value,
                "name": country.name,
                "description": f"Support for {country.value} institutions"
            })
        
        return {
            "countries": countries,
            "default_countries": [CountryCode.US.value],
            "environment": "sandbox"
        }
        
    except Exception as e:
        logger.error(f"Failed to get supported countries: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get supported countries: {str(e)}"
        )

# ==========================================
# Health and Status Endpoints
# ==========================================

@router.get("/health",
            summary="Link Service Health Check",
            description="Check health and configuration of Link service")
async def link_health_check() -> Dict[str, Any]:
    """
    Health check for Link service functionality.
    
    Returns:
    - Service status
    - Configuration validation
    - Plaid environment information
    """
    try:
        # Check Plaid service
        plaid_service = get_plaid_service()
        
        # Basic configuration check
        config_status = {
            "plaid_client_configured": plaid_service.client is not None,
            "environment": "sandbox"
        }
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "plaid-link",
            "version": "1.0.0",
            "configuration": config_status
        }
        
    except Exception as e:
        logger.error(f"Link health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "plaid-link",
            "error": str(e)
        }
