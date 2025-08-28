"""
Institutions module for TruLedgr

This module provides institution management functionality, aggregating data from:
- Plaid institutions (raw data from Plaid API)
- Manual institution entries
- Other banking integrations (future)

The institution module serves as the central source of truth for all financial 
institutions in the system, providing unified access and management.
"""

from .models import Institution, InstitutionSourceMapping, InstitutionType, InstitutionSource
from .schemas import (
    InstitutionCreate,
    InstitutionUpdate, 
    InstitutionResponse,
    InstitutionListResponse,
    InstitutionSearchRequest,
    PlaidInstitutionSyncRequest
)
from .service import institution_service
from .router import router

__all__ = [
    # Models
    "Institution",
    "InstitutionSourceMapping", 
    "InstitutionType",
    "InstitutionSource",
    
    # Schemas
    "InstitutionCreate",
    "InstitutionUpdate",
    "InstitutionResponse", 
    "InstitutionListResponse",
    "InstitutionSearchRequest",
    "PlaidInstitutionSyncRequest",
    
    # Service
    "institution_service",
    
    # Router
    "router"
]
