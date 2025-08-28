"""
Institution Service Layer

Business logic for institution management, aggregating data from:
- Plaid institutions
- Manual institution entries  
- Other banking integrations

Provides unified institution operations and data validation.
"""

from typing import Optional, List, Dict, Any, Tuple
from sqlmodel import select, or_, and_, func
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime, timedelta
import asyncio
from api.common.utils import generate_id

from .models import Institution, InstitutionSourceMapping, InstitutionType, InstitutionSource
from .schemas import (
    InstitutionCreate, 
    InstitutionUpdate, 
    InstitutionResponse, 
    InstitutionSearchRequest,
    PlaidInstitutionSyncRequest
)
from api.common.exceptions import ValidationError, NotFoundError


class InstitutionService:
    """Service class for institution operations"""
    
    async def create_institution(
        self, 
        session: AsyncSession, 
        request: InstitutionCreate
    ) -> InstitutionResponse:
        """Create a new institution with validation"""
        
        # Check for existing institution with same name
        existing = await session.exec(
            select(Institution).where(Institution.name == request.name)
        )
        if existing.first():
            raise ValidationError(f"Institution with name '{request.name}' already exists")
        
        # Create institution with all required fields
        institution = Institution(
            id=generate_id(),
            name=request.name,
            official_name=request.official_name,
            common_name=request.common_name,
            institution_type=request.institution_type,
            primary_source=InstitutionSource.MANUAL,
            plaid_institution_id=request.plaid_institution_id,
            routing_numbers=request.routing_numbers,
            swift_code=request.swift_code,
            website=request.website,
            phone=request.phone,
            primary_color=request.primary_color,
            logo_url=request.logo_url,
            country_codes=request.country_codes,
            headquarters_city=request.headquarters_city,
            headquarters_state=request.headquarters_state,
            headquarters_country=request.headquarters_country,
            supports_transactions=request.supports_transactions,
            supports_auth=request.supports_auth,
            supports_identity=request.supports_identity,
            supports_investments=request.supports_investments,
            supports_liabilities=request.supports_liabilities,
            supports_assets=request.supports_assets,
            manual_entry_allowed=request.manual_entry_allowed,
            notes=request.notes,
            tags=request.tags,
            last_plaid_sync=None
        )
        
        session.add(institution)
        await session.commit()
        await session.refresh(institution)
        
        return self._institution_to_response(institution)
    
    async def get_institution_by_id(
        self, 
        session: AsyncSession, 
        institution_id: str
    ) -> Optional[InstitutionResponse]:
        """Get institution by ID"""
        
        result = await session.exec(
            select(Institution).where(Institution.id == institution_id)
        )
        institution = result.first()
        
        if not institution:
            return None
            
        return self._institution_to_response(institution)
    
    async def list_institutions(
        self, 
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        search_request: Optional[InstitutionSearchRequest] = None
    ) -> Tuple[List[InstitutionResponse], int]:
        """List institutions with filtering and pagination"""
        
        # Build base query
        query = select(Institution)
        
        # Apply filters if search request provided
        if search_request:
            filters = []
            
            if search_request.institution_type:
                filters.append(Institution.institution_type == search_request.institution_type)
            
            if search_request.primary_source:
                filters.append(Institution.primary_source == search_request.primary_source)
            
            if search_request.plaid_institution_id:
                filters.append(Institution.plaid_institution_id == search_request.plaid_institution_id)
            
            if search_request.is_active is not None:
                filters.append(Institution.is_active == search_request.is_active)
            
            if search_request.plaid_enabled is not None:
                filters.append(Institution.plaid_enabled == search_request.plaid_enabled)
            
            if search_request.supports_transactions is not None:
                filters.append(Institution.supports_transactions == search_request.supports_transactions)
            
            if filters:
                query = query.where(and_(*filters))
        
        # Get total count
        count_result = await session.exec(query)
        total = len(count_result.all())
        
        # Apply pagination and get results
        paginated_query = query.offset(skip).limit(limit).order_by(Institution.name)
        result = await session.exec(paginated_query)
        institutions = result.all()
        
        responses = [self._institution_to_response(inst) for inst in institutions]
        return responses, total
    
    async def update_institution(
        self, 
        session: AsyncSession,
        institution_id: str,
        request: InstitutionUpdate
    ) -> Optional[InstitutionResponse]:
        """Update an institution"""
        
        result = await session.exec(
            select(Institution).where(Institution.id == institution_id)
        )
        institution = result.first()
        
        if not institution:
            return None
        
        # Update fields
        update_data = request.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(institution, field, value)
        
        institution.updated_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(institution)
        
        return self._institution_to_response(institution)
    
    async def delete_institution(
        self, 
        session: AsyncSession,
        institution_id: str
    ) -> bool:
        """Delete an institution (soft delete by setting is_active=False)"""
        
        result = await session.exec(
            select(Institution).where(Institution.id == institution_id)
        )
        institution = result.first()
        
        if not institution:
            return False
        
        institution.is_active = False
        institution.updated_at = datetime.utcnow()
        
        await session.commit()
        return True
    
    async def search_institutions_by_query(
        self, 
        session: AsyncSession,
        query: str,
        limit: int = 20
    ) -> List[InstitutionResponse]:
        """Search institutions by text query - TODO: Implement text search"""
        
        # For now, just return active institutions
        search_query = select(Institution).where(
            Institution.is_active == True
        ).limit(limit).order_by(Institution.name)
        
        result = await session.exec(search_query)
        institutions = result.all()
        
        return [self._institution_to_response(inst) for inst in institutions]
    
    async def sync_plaid_institution(
        self, 
        session: AsyncSession,
        request: PlaidInstitutionSyncRequest
    ) -> InstitutionResponse:
        """Sync institution data with Plaid"""
        
        # Check if institution already exists
        result = await session.exec(
            select(Institution).where(
                Institution.plaid_institution_id == request.plaid_institution_id
            )
        )
        institution = result.first()
        
        if institution and not request.force_update:
            # Check if recently synced (within last hour)
            if (institution.last_plaid_sync and 
                institution.last_plaid_sync > datetime.utcnow() - timedelta(hours=1)):
                return self._institution_to_response(institution)
        
        # TODO: Implement actual Plaid API call to get institution data
        # For now, create/update with placeholder data
        
        if institution:
            # Update existing
            institution.last_plaid_sync = datetime.utcnow()
            institution.updated_at = datetime.utcnow()
        else:
            # Create new from Plaid data
            institution = self._create_institution_from_plaid_data(
                request.plaid_institution_id, 
                {}  # Placeholder - would be actual Plaid data
            )
            session.add(institution)
        
        await session.commit()
        await session.refresh(institution)
        
        return self._institution_to_response(institution)
    
    async def get_institutions_by_plaid_id(
        self, 
        session: AsyncSession,
        plaid_institution_id: str
    ) -> List[InstitutionResponse]:
        """Get institutions by Plaid institution ID"""
        
        result = await session.exec(
            select(Institution).where(
                Institution.plaid_institution_id == plaid_institution_id
            )
        )
        institutions = result.all()
        
        return [self._institution_to_response(inst) for inst in institutions]
    
    def _institution_to_response(self, institution: Institution) -> InstitutionResponse:
        """Convert Institution model to response schema"""
        
        return InstitutionResponse(
            id=institution.id or "",
            name=institution.name,
            official_name=institution.official_name,
            common_name=institution.common_name,
            institution_type=institution.institution_type,
            primary_source=institution.primary_source,
            plaid_institution_id=institution.plaid_institution_id,
            routing_numbers=institution.routing_numbers,
            swift_code=institution.swift_code,
            website=institution.website,
            phone=institution.phone,
            primary_color=institution.primary_color,
            logo_url=institution.logo_url,
            country_codes=institution.country_codes,
            headquarters_city=institution.headquarters_city,
            headquarters_state=institution.headquarters_state,
            headquarters_country=institution.headquarters_country,
            supports_transactions=institution.supports_transactions,
            supports_auth=institution.supports_auth,
            supports_identity=institution.supports_identity,
            supports_investments=institution.supports_investments,
            supports_liabilities=institution.supports_liabilities,
            supports_assets=institution.supports_assets,
            is_active=institution.is_active,
            plaid_enabled=institution.plaid_enabled,
            manual_entry_allowed=institution.manual_entry_allowed,
            health_status=institution.health_status,
            last_health_check=institution.last_health_check,
            plaid_sync_errors=institution.plaid_sync_errors,
            notes=institution.notes,
            tags=institution.tags,
            created_at=institution.created_at,
            updated_at=institution.updated_at,
            last_plaid_sync=institution.last_plaid_sync,
            routing_numbers_list=institution.routing_numbers_list,
            country_codes_list=institution.country_codes_list,
            tags_list=institution.tags_list
        )
    
    def _create_institution_from_plaid_data(
        self, 
        plaid_institution_id: str, 
        plaid_data: Dict[str, Any]
    ) -> Institution:
        """Create Institution from Plaid API data"""
        
        return Institution(
            id=generate_id(),
            name=plaid_data.get('name', f'Plaid Institution {plaid_institution_id}'),
            official_name=plaid_data.get('name'),
            common_name=None,
            plaid_institution_id=plaid_institution_id,
            primary_source=InstitutionSource.PLAID,
            institution_type=InstitutionType.BANK,
            routing_numbers=None,
            swift_code=None,
            website=plaid_data.get('url'),
            phone=None,
            primary_color=plaid_data.get('primary_color'),
            logo_url=plaid_data.get('logo'),
            country_codes=','.join(plaid_data.get('country_codes', ['US'])),
            headquarters_city=None,
            headquarters_state=None,
            headquarters_country='US',
            supports_transactions=True,
            supports_auth=True,
            supports_identity=plaid_data.get('products', {}).get('identity', False),
            supports_investments=plaid_data.get('products', {}).get('investments', False),
            supports_liabilities=plaid_data.get('products', {}).get('liabilities', False),
            supports_assets=plaid_data.get('products', {}).get('assets', False),
            plaid_enabled=True,
            manual_entry_allowed=False,
            notes='Automatically created from Plaid data',
            tags='plaid,automated',
            last_plaid_sync=datetime.utcnow()
        )


# Create service instance
institution_service = InstitutionService()
