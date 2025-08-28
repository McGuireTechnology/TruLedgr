"""
Plaid Institutions API Router

FastAPI routes for institution-related operations following REST conventions.
Standard CRUD operations on /plaid/institutions
Remote Plaid API access on /plaid/institutions/remote
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status, Body, Path
from pydantic import BaseModel
from api.authentication.deps import get_current_user
from api.users.models import User
from .service import InstitutionsService
from .models import PlaidInstitutionResponse, PlaidInstitution
from ..service import PlaidService, get_plaid_service
from ..items.models import PlaidEnvironment

router = APIRouter(prefix="/institutions", tags=["Plaid Institutions"])

institutions_service = InstitutionsService()

# ==========================================
# Request/Response Models
# ==========================================

class InstitutionCreateRequest(BaseModel):
    """Request model for creating institution"""
    institution_id: str
    name: str
    products: List[str] = []
    country_codes: List[str] = []
    url: Optional[str] = None
    primary_color: Optional[str] = None
    logo: Optional[str] = None
    routing_numbers: List[str] = []
    dtc_numbers: List[str] = []
    oauth: bool = False

class InstitutionUpdateRequest(BaseModel):
    """Request model for updating institution"""
    name: Optional[str] = None
    products: Optional[List[str]] = None
    country_codes: Optional[List[str]] = None
    url: Optional[str] = None
    primary_color: Optional[str] = None
    logo: Optional[str] = None
    routing_numbers: Optional[List[str]] = None
    dtc_numbers: Optional[List[str]] = None
    oauth: Optional[bool] = None

class BulkImportRequest(BaseModel):
    """Request model for bulk import from remote API"""
    institution_ids: List[str]
    environment: str = "sandbox"

class PlaidInstitutionSearchResponse(BaseModel):
    """Response model for Plaid institution search"""
    institution_id: str
    name: str
    products: List[str]
    country_codes: List[str]
    url: Optional[str] = None
    primary_color: Optional[str] = None
    logo: Optional[str] = None
    oauth: bool = False
    routing_numbers: List[str] = []
    dtc_numbers: List[str] = []
    environment: str

class PlaidInstitutionsResponse(BaseModel):
    """Response model for Plaid institutions list"""
    institutions: List[PlaidInstitutionSearchResponse]
    total: int
    request_id: str
    environment: str

class BulkImportResponse(BaseModel):
    """Response model for bulk import"""
    imported_count: int
    failed_count: int
    imported: List[dict]
    failed: List[dict]
    environment: str

# ==========================================
# Standard REST Endpoints (Database CRUD)
# ==========================================

@router.get("/", response_model=List[PlaidInstitutionResponse])
async def get_institutions(
    limit: int = Query(default=100, ge=1, le=500, description="Number of institutions to retrieve"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    search: Optional[str] = Query(default=None, description="Search in institution name and ID"),
    current_user: User = Depends(get_current_user)
):
    """Get institutions from local database with optional search"""
    try:
        if search:
            return institutions_service.search_institutions_db(
                query=search,
                limit=limit,
                offset=offset
            )
        else:
            return institutions_service.get_institutions_db(
                limit=limit,
                offset=offset
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve institutions: {str(e)}"
        )

@router.get("/{institution_id}", response_model=PlaidInstitutionResponse)
async def get_institution_by_id(
    institution_id: str = Path(..., description="Plaid institution ID"),
    current_user: User = Depends(get_current_user)
):
    """Get a specific institution by ID from local database"""
    try:
        institution = institutions_service.get_institution_by_id_db(institution_id)
        if not institution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Institution not found"
            )
        return institution
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve institution: {str(e)}"
        )

@router.post("/", response_model=PlaidInstitutionResponse)
async def create_institution(
    request: InstitutionCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new institution in the local database"""
    try:
        # Convert request to institution data format
        institution_data = {
            "name": request.name,
            "products": request.products,
            "country_codes": request.country_codes,
            "url": request.url,
            "primary_color": request.primary_color,
            "logo": request.logo,
            "routing_numbers": request.routing_numbers,
            "dtc_numbers": request.dtc_numbers,
            "oauth": request.oauth
        }
        
        return institutions_service.sync_institution_db(request.institution_id, institution_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create institution: {str(e)}"
        )

@router.patch("/{institution_id}", response_model=PlaidInstitutionResponse)
async def update_institution(
    institution_id: str = Path(..., description="Plaid institution ID"),
    request: InstitutionUpdateRequest = Body(...),
    current_user: User = Depends(get_current_user)
):
    """Update an existing institution in the local database"""
    try:
        # Get existing institution
        existing = institutions_service.get_institution_by_id_db(institution_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Institution not found"
            )
        
        # Prepare update data with only provided fields
        update_data = {}
        if request.name is not None:
            update_data["name"] = request.name
        if request.products is not None:
            update_data["products"] = request.products
        if request.country_codes is not None:
            update_data["country_codes"] = request.country_codes
        if request.url is not None:
            update_data["url"] = request.url
        if request.primary_color is not None:
            update_data["primary_color"] = request.primary_color
        if request.logo is not None:
            update_data["logo"] = request.logo
        if request.routing_numbers is not None:
            update_data["routing_numbers"] = request.routing_numbers
        if request.dtc_numbers is not None:
            update_data["dtc_numbers"] = request.dtc_numbers
        if request.oauth is not None:
            update_data["oauth"] = request.oauth
        
        return institutions_service.sync_institution_db(institution_id, update_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update institution: {str(e)}"
        )

@router.put("/{institution_id}", response_model=PlaidInstitutionResponse)
async def replace_institution(
    institution_id: str = Path(..., description="Plaid institution ID"),
    request: InstitutionCreateRequest = Body(...),
    current_user: User = Depends(get_current_user)
):
    """Replace an existing institution in the local database"""
    try:
        # Convert request to institution data format
        institution_data = {
            "name": request.name,
            "products": request.products,
            "country_codes": request.country_codes,
            "url": request.url,
            "primary_color": request.primary_color,
            "logo": request.logo,
            "routing_numbers": request.routing_numbers,
            "dtc_numbers": request.dtc_numbers,
            "oauth": request.oauth
        }
        
        return institutions_service.sync_institution_db(institution_id, institution_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to replace institution: {str(e)}"
        )

@router.delete("/{institution_id}")
async def delete_institution(
    institution_id: str = Path(..., description="Plaid institution ID"),
    current_user: User = Depends(get_current_user)
):
    """Delete an institution from the local database"""
    try:
        deleted = institutions_service.delete_institution_db(institution_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Institution not found"
            )
        
        return {"message": f"Institution {institution_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete institution: {str(e)}"
        )

# ==========================================
# Remote Plaid API Endpoints
# ==========================================

@router.get("/remote/search", response_model=List[PlaidInstitutionSearchResponse])
async def search_institutions_remote(
    query: str = Query(..., description="Search query for institution name"),
    products: Optional[str] = Query(default="transactions", description="Comma-separated list of products (e.g. 'transactions,auth')"),
    country_codes: Optional[str] = Query(default="US", description="Comma-separated list of country codes"),
    environment: str = Query(default="sandbox", description="Plaid environment (sandbox or production)"),
    current_user: User = Depends(get_current_user)
):
    """Search institutions using remote Plaid API"""
    try:
        products_list = [p.strip() for p in products.split(",")] if products else ["transactions"]
        countries_list = [c.strip() for c in country_codes.split(",")] if country_codes else ["US"]
        
        institutions = await institutions_service.search_institutions_plaid(
            query=query,
            products=products_list,
            country_codes=countries_list,
            environment=environment
        )
        
        return [PlaidInstitutionSearchResponse(**inst) for inst in institutions]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search institutions: {str(e)}"
        )

@router.get("/remote", response_model=PlaidInstitutionsResponse)
async def get_institutions_remote(
    count: int = Query(default=100, ge=1, le=500, description="Number of institutions to retrieve"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    country_codes: Optional[str] = Query(default="US", description="Comma-separated list of country codes"),
    environment: str = Query(default="sandbox", description="Plaid environment (sandbox or production)"),
    current_user: User = Depends(get_current_user)
):
    """Get institutions from remote Plaid API"""
    try:
        countries_list = [c.strip() for c in country_codes.split(",")] if country_codes else ["US"]
        
        result = await institutions_service.get_institutions_plaid(
            count=count,
            offset=offset,
            country_codes=countries_list,
            environment=environment
        )
        
        return PlaidInstitutionsResponse(
            institutions=[PlaidInstitutionSearchResponse(**inst) for inst in result['institutions']],
            total=result['total'],
            request_id=result['request_id'],
            environment=result['environment']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get institutions: {str(e)}"
        )

@router.get("/remote/{institution_id}", response_model=PlaidInstitutionSearchResponse)
async def get_institution_by_id_remote(
    institution_id: str = Path(..., description="Plaid institution ID"),
    country_codes: Optional[str] = Query(default="US", description="Comma-separated list of country codes"),
    include_optional_metadata: bool = Query(default=False, description="Include optional metadata"),
    include_status: bool = Query(default=False, description="Include status information"),
    environment: str = Query(default="sandbox", description="Plaid environment (sandbox or production)"),
    current_user: User = Depends(get_current_user)
):
    """Get a specific institution by ID from remote Plaid API"""
    try:
        countries_list = [c.strip() for c in country_codes.split(",")] if country_codes else ["US"]
        
        institution = await institutions_service.get_institution_by_id_plaid(
            institution_id=institution_id,
            country_codes=countries_list,
            include_optional_metadata=include_optional_metadata,
            include_status=include_status,
            environment=environment
        )
        
        return PlaidInstitutionSearchResponse(**institution)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get institution: {str(e)}"
        )

@router.post("/remote/import/{institution_id}", response_model=PlaidInstitutionResponse)
async def import_institution_from_remote(
    institution_id: str = Path(..., description="Plaid institution ID"),
    environment: str = Query(default="sandbox", description="Plaid environment (sandbox or production)"),
    current_user: User = Depends(get_current_user)
):
    """Import an institution from remote Plaid API into the local database"""
    try:
        return await institutions_service.import_institution_from_plaid(
            institution_id=institution_id,
            environment=environment
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import institution: {str(e)}"
        )

@router.post("/remote/import/bulk", response_model=BulkImportResponse)
async def bulk_import_institutions_from_remote(
    request: BulkImportRequest,
    current_user: User = Depends(get_current_user)
):
    """Import multiple institutions from remote Plaid API into the local database"""
    try:
        if not request.institution_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Institution IDs list cannot be empty"
            )
        
        if len(request.institution_ids) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot import more than 50 institutions at once"
            )
        
        result = await institutions_service.bulk_import_institutions_from_plaid(
            institution_ids=request.institution_ids,
            environment=request.environment
        )
        
        return BulkImportResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk import institutions: {str(e)}"
        )

