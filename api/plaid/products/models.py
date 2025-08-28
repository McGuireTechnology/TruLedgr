"""
Plaid Products Models

Database and API models for Plaid products information and status.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class PlaidProductStatus(str, Enum):
    """Status of Plaid product integration"""
    SUPPORTED = "supported"
    PLANNED = "planned"
    DEPRECATED = "deprecated"
    NOT_APPLICABLE = "not_applicable"


class PlaidProductInfo(BaseModel):
    """Information about a Plaid product"""
    name: str = Field(..., description="Product identifier")
    display_name: str = Field(..., description="Human-readable product name")
    description: str = Field(..., description="Product description")
    features: List[str] = Field(default_factory=list, description="List of product features")
    use_cases: List[str] = Field(default_factory=list, description="Common use cases")
    supported: bool = Field(..., description="Whether the product is supported")
    documentation_url: Optional[str] = Field(None, description="Link to Plaid documentation")


class PlaidProductResponse(BaseModel):
    """Response model for single product"""
    product: PlaidProductInfo
    available_in_environments: List[str] = Field(default_factory=list)
    integration_notes: Dict[str, Any] = Field(default_factory=dict)


class PlaidProductsResponse(BaseModel):
    """Response model for multiple products"""
    products: List[PlaidProductInfo]
    supported_count: int
    total_count: int
    integration_status: Dict[str, str] = Field(default_factory=dict)


class SupportedProductsResponse(BaseModel):
    """Response model for supported products only"""
    products: List[PlaidProductInfo]
    count: int
    supported_products: List[str]
