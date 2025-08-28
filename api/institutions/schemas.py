"""
Institution Schemas

Request and response schemas for institution API endpoints.
"""

from sqlmodel import SQLModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import Field, validator

from .models import InstitutionType, InstitutionSource


class InstitutionCreate(SQLModel):
    """Schema for creating a new institution"""
    name: str = Field(..., min_length=1, max_length=255, description="Institution display name")
    official_name: Optional[str] = Field(None, max_length=255, description="Official legal name")
    common_name: Optional[str] = Field(None, max_length=255, description="Commonly used name")
    institution_type: InstitutionType = Field(default=InstitutionType.BANK)
    
    # External identifiers
    plaid_institution_id: Optional[str] = Field(None, description="Plaid institution ID")
    routing_numbers: Optional[str] = Field(None, description="Comma-separated routing numbers")
    swift_code: Optional[str] = Field(None, description="SWIFT/BIC code")
    
    # Contact information
    website: Optional[str] = None
    phone: Optional[str] = None
    primary_color: Optional[str] = Field(None, description="Brand primary color (hex)")
    logo_url: Optional[str] = None
    
    # Geographic information
    country_codes: Optional[str] = Field(None, description="Comma-separated country codes")
    headquarters_city: Optional[str] = None
    headquarters_state: Optional[str] = None
    headquarters_country: str = Field(default="US")
    
    # Capabilities
    supports_transactions: bool = Field(default=True)
    supports_auth: bool = Field(default=False)
    supports_identity: bool = Field(default=False)
    supports_investments: bool = Field(default=False)
    supports_liabilities: bool = Field(default=False)
    supports_assets: bool = Field(default=False)
    
    # Settings
    manual_entry_allowed: bool = Field(default=True)
    notes: Optional[str] = Field(None, description="Internal notes")
    tags: Optional[str] = Field(None, description="Comma-separated tags")


class InstitutionUpdate(SQLModel):
    """Schema for updating an institution"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    official_name: Optional[str] = Field(None, max_length=255)
    common_name: Optional[str] = Field(None, max_length=255)
    institution_type: Optional[InstitutionType] = None
    
    # External identifiers
    routing_numbers: Optional[str] = None
    swift_code: Optional[str] = None
    
    # Contact information
    website: Optional[str] = None
    phone: Optional[str] = None
    primary_color: Optional[str] = None
    logo_url: Optional[str] = None
    
    # Geographic information
    country_codes: Optional[str] = None
    headquarters_city: Optional[str] = None
    headquarters_state: Optional[str] = None
    headquarters_country: Optional[str] = None
    
    # Capabilities
    supports_transactions: Optional[bool] = None
    supports_auth: Optional[bool] = None
    supports_identity: Optional[bool] = None
    supports_investments: Optional[bool] = None
    supports_liabilities: Optional[bool] = None
    supports_assets: Optional[bool] = None
    
    # Settings
    is_active: Optional[bool] = None
    manual_entry_allowed: Optional[bool] = None
    notes: Optional[str] = None
    tags: Optional[str] = None


class InstitutionResponse(SQLModel):
    """Schema for institution API responses"""
    id: str
    name: str
    official_name: Optional[str] = None
    common_name: Optional[str] = None
    institution_type: InstitutionType
    primary_source: InstitutionSource
    
    # External identifiers
    plaid_institution_id: Optional[str] = None
    routing_numbers: Optional[str] = None
    swift_code: Optional[str] = None
    
    # Contact information
    website: Optional[str] = None
    phone: Optional[str] = None
    primary_color: Optional[str] = None
    logo_url: Optional[str] = None
    
    # Geographic information
    country_codes: Optional[str] = None
    headquarters_city: Optional[str] = None
    headquarters_state: Optional[str] = None
    headquarters_country: str
    
    # Capabilities
    supports_transactions: bool
    supports_auth: bool
    supports_identity: bool
    supports_investments: bool
    supports_liabilities: bool
    supports_assets: bool
    
    # Status
    is_active: bool
    plaid_enabled: bool
    manual_entry_allowed: bool
    health_status: str
    last_health_check: Optional[datetime] = None
    plaid_sync_errors: int
    
    # Metadata
    notes: Optional[str] = None
    tags: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    last_plaid_sync: Optional[datetime] = None
    
    # Helper fields
    routing_numbers_list: List[str] = Field(default=[], description="Routing numbers as list")
    country_codes_list: List[str] = Field(default=[], description="Country codes as list")
    tags_list: List[str] = Field(default=[], description="Tags as list")


class InstitutionListResponse(SQLModel):
    """Schema for paginated institution list responses"""
    institutions: List[InstitutionResponse]
    total: int
    skip: int
    limit: int


class InstitutionSearchRequest(SQLModel):
    """Schema for institution search requests"""
    name: Optional[str] = Field(None, description="Search by name (partial match)")
    institution_type: Optional[InstitutionType] = None
    primary_source: Optional[InstitutionSource] = None
    plaid_institution_id: Optional[str] = None
    country_codes: Optional[List[str]] = None
    supports_transactions: Optional[bool] = None
    is_active: Optional[bool] = None
    plaid_enabled: Optional[bool] = None


class PlaidInstitutionSyncRequest(SQLModel):
    """Schema for syncing Plaid institution data"""
    plaid_institution_id: str = Field(..., description="Plaid institution ID to sync")
    force_update: bool = Field(default=False, description="Force update even if recently synced")


class InstitutionHealthCheck(SQLModel):
    """Schema for institution health check responses"""
    institution_id: str
    health_status: str
    last_check: datetime
    error_count: int
    error_details: Optional[Dict[str, Any]] = None


class BulkInstitutionOperation(SQLModel):
    """Schema for bulk operations on institutions"""
    institution_ids: List[str] = Field(..., description="Institution IDs to operate on")
    operation: str = Field(..., description="activate, deactivate, sync, health_check")
    parameters: Optional[Dict[str, Any]] = None
    
    @validator('institution_ids')
    def validate_institution_ids(cls, v):
        if len(v) < 1:
            raise ValueError("At least one institution ID is required")
        if len(v) > 100:
            raise ValueError("Maximum 100 institution IDs allowed")
        return v
