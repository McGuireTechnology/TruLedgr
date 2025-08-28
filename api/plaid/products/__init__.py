"""
Plaid Products module

This module contains information about Plaid products, their features,
and integration status within the TruLedgr platform.
"""

from .models import PlaidProductInfo, PlaidProductResponse, PlaidProductStatus
from .service import ProductsService
from .router import router

__all__ = [
    "PlaidProductInfo",
    "PlaidProductResponse", 
    "PlaidProductStatus",
    "ProductsService",
    "router"
]
