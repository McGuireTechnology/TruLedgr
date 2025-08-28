"""
Institutions Router

FastAPI endpoints for institution management - handles both manual institutions
and Plaid-synced institutions in a unified interface.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession
import logging

from api.deps import get_db, get_current_user
from api.users.models import User
from .service import institution_service
from .models import Institution, InstitutionType, InstitutionSource
from .schemas import (
    InstitutionResponse,
    InstitutionCreate,
    InstitutionUpdate,
    InstitutionSearchRequest,
    PlaidInstitutionSyncRequest,
    InstitutionListResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/institutions", tags=["institutions"])


@router.get("/", response_model=InstitutionListResponse)
async def list_institutions(
    skip: int = Query(0, ge=0, description="Number of institutions to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of institutions to return"),
    institution_type: Optional[InstitutionType] = Query(None, description="Filter by institution type"),
    primary_source: Optional[InstitutionSource] = Query(None, description="Filter by primary source"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    plaid_enabled: Optional[bool] = Query(None, description="Filter by Plaid enabled status"),
    supports_transactions: Optional[bool] = Query(None, description="Filter by transaction support"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List institutions with optional filtering and pagination.
    
    Returns a paginated list of institutions with support for various filters.
    """
    try:
        # Build search request from query parameters
        search_request = None
        if any([institution_type, primary_source, is_active, plaid_enabled, supports_transactions]):
            search_request = InstitutionSearchRequest(
                institution_type=institution_type,
                primary_source=primary_source,
                is_active=is_active,
                plaid_enabled=plaid_enabled,
                supports_transactions=supports_transactions
            )
        
        institutions, total = await institution_service.list_institutions(
            db, skip=skip, limit=limit, search_request=search_request
        )
        
        return InstitutionListResponse(
            institutions=institutions,
            total=total,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Error listing institutions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve institutions"
        )


@router.get("/{institution_id}", response_model=InstitutionResponse)
async def get_institution(
    institution_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific institution by ID.
    
    Returns detailed information about a single institution.
    """
    try:
        institution = await institution_service.get_institution_by_id(db, institution_id)
        
        if not institution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Institution with ID {institution_id} not found"
            )
        
        return institution
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving institution {institution_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve institution"
        )


@router.post("/", response_model=InstitutionResponse, status_code=status.HTTP_201_CREATED)
async def create_institution(
    request: InstitutionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new institution.
    
    Creates a new institution with the provided details.
    """
    try:
        institution = await institution_service.create_institution(db, request)
        
        logger.info(f"Created institution {institution.id} by user {current_user.id}")
        return institution
        
    except Exception as e:
        logger.error(f"Error creating institution: {str(e)}")
        if "already exists" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create institution"
        )


@router.put("/{institution_id}", response_model=InstitutionResponse)
async def update_institution(
    institution_id: str,
    request: InstitutionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing institution.
    
    Updates the specified institution with the provided details.
    """
    try:
        institution = await institution_service.update_institution(db, institution_id, request)
        
        if not institution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Institution with ID {institution_id} not found"
            )
        
        logger.info(f"Updated institution {institution_id} by user {current_user.id}")
        return institution
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating institution {institution_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update institution"
        )


@router.delete("/{institution_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_institution(
    institution_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an institution (soft delete).
    
    Marks the institution as inactive rather than permanently deleting it.
    """
    try:
        success = await institution_service.delete_institution(db, institution_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Institution with ID {institution_id} not found"
            )
        
        logger.info(f"Deleted institution {institution_id} by user {current_user.id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting institution {institution_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete institution"
        )


@router.get("/search/query", response_model=List[InstitutionResponse])
async def search_institutions(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search institutions by text query.
    
    Searches institution names and returns matching results.
    """
    try:
        institutions = await institution_service.search_institutions_by_query(db, q, limit)
        return institutions
        
    except Exception as e:
        logger.error(f"Error searching institutions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search institutions"
        )


@router.post("/sync/plaid", response_model=InstitutionResponse)
async def sync_plaid_institution(
    request: PlaidInstitutionSyncRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Sync institution data from Plaid.
    
    Creates or updates an institution with data from Plaid's API.
    """
    try:
        institution = await institution_service.sync_plaid_institution(db, request)
        
        logger.info(f"Synced Plaid institution {request.plaid_institution_id} by user {current_user.id}")
        return institution
        
    except Exception as e:
        logger.error(f"Error syncing Plaid institution: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync Plaid institution"
        )


@router.get("/plaid/{plaid_institution_id}", response_model=List[InstitutionResponse])
async def get_institutions_by_plaid_id(
    plaid_institution_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get institutions by Plaid institution ID.
    
    Returns all institutions associated with a specific Plaid institution ID.
    """
    try:
        institutions = await institution_service.get_institutions_by_plaid_id(db, plaid_institution_id)
        return institutions
        
    except Exception as e:
        logger.error(f"Error retrieving institutions by Plaid ID: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve institutions"
        )
