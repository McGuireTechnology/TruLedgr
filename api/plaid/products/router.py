"""
Plaid Products API Router

FastAPI routes for Plaid products information and status.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status, Path
from api.authentication.deps import get_current_user
from api.users.models import User
from fastapi import Depends

from .service import ProductsService
from .models import PlaidProductsResponse, SupportedProductsResponse, PlaidProductResponse

router = APIRouter(prefix="/products", tags=["Plaid Products"])

# Initialize the products service
products_service = ProductsService()


@router.get("/", response_model=PlaidProductsResponse)
async def get_plaid_products():
    """Get all available Plaid products and their descriptions"""
    return products_service.get_all_products()


@router.get("/supported", response_model=SupportedProductsResponse)
async def get_supported_plaid_products():
    """Get only the Plaid products that are currently supported"""
    return products_service.get_supported_products()


@router.get("/{product_name}", response_model=PlaidProductResponse)
async def get_plaid_product_by_name(
    product_name: str = Path(..., description="Name of the Plaid product")
):
    """Get details for a specific Plaid product"""
    product_details = products_service.get_product_details(product_name)
    
    if not product_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product '{product_name}' not found"
        )
    
    return product_details


@router.get("/category/{category}")
async def get_products_by_category(
    category: str = Path(..., description="Product category (supported, unsupported, all)")
):
    """Get products filtered by category"""
    products = products_service.get_products_by_category(category)
    
    return {
        "category": category,
        "products": products,
        "count": len(products)
    }
