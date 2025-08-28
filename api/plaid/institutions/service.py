"""
Plaid Institutions Service

Service layer for handling Institution search, retrieval, and database operations.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlmodel import Session, select
from fastapi import HTTPException, status
import logging

from plaid.model.institutions_get_request import InstitutionsGetRequest
from plaid.model.institutions_search_request import InstitutionsSearchRequest
from plaid.model.institutions_get_by_id_request import InstitutionsGetByIdRequest
from plaid.model.country_code import CountryCode
from plaid.model.products import Products

from api.db.deps import get_db
from .models import PlaidInstitution, PlaidInstitutionResponse, PlaidProduct
from ..service import get_plaid_service

logger = logging.getLogger(__name__)

class InstitutionsService:
    """Service for handling Plaid Institution database operations and API queries"""
    
    def __init__(self, parent_service=None):
        if parent_service:
            self.plaid_service = parent_service
        else:
            self.plaid_service = get_plaid_service()
    
    # ==========================================
    # Plaid API Methods
    # ==========================================
    
    async def search_institutions_plaid(
        self, 
        query: str, 
        products: Optional[List[str]] = None, 
        country_codes: Optional[List[str]] = None,
        environment: str = "sandbox"
    ) -> List[Dict[str, Any]]:
        """Search institutions using Plaid API"""
        try:
            if not self.plaid_service.is_environment_available(environment):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Plaid environment '{environment}' is not available"
                )
            
            client = self.plaid_service._get_client(environment)
            
            # Default values
            if products is None:
                products = ["transactions"]
            if country_codes is None:
                country_codes = ["US"]
            
            # Convert strings to Plaid enums
            plaid_products = [Products(p) for p in products]
            plaid_countries = [CountryCode(c) for c in country_codes]
            
            request = InstitutionsSearchRequest(
                query=query,
                products=plaid_products,
                country_codes=plaid_countries
            )
            
            response = client.institutions_search(request)
            
            institutions = []
            for inst in response['institutions']:
                institutions.append({
                    'institution_id': inst['institution_id'],
                    'name': inst['name'],
                    'products': inst['products'],
                    'country_codes': inst['country_codes'],
                    'url': inst.get('url'),
                    'primary_color': inst.get('primary_color'),
                    'logo': inst.get('logo'),
                    'oauth': inst.get('oauth', False),
                    'routing_numbers': inst.get('routing_numbers', []),
                    'dtc_numbers': inst.get('dtc_numbers', []),
                    'environment': environment
                })
            
            logger.info(f"Found {len(institutions)} institutions for query '{query}' in {environment}")
            return institutions
            
        except Exception as e:
            logger.error(f"Error searching institutions in Plaid {environment}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to search institutions: {str(e)}"
            )
    
    async def get_institutions_plaid(
        self,
        count: int = 100,
        offset: int = 0,
        country_codes: Optional[List[str]] = None,
        products: Optional[List[str]] = None,
        environment: str = "sandbox"
    ) -> Dict[str, Any]:
        """Get institutions from Plaid API"""
        try:
            if not self.plaid_service.is_environment_available(environment):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Plaid environment '{environment}' is not available"
                )
            
            client = self.plaid_service._get_client(environment)
            
            # Default values
            if country_codes is None:
                country_codes = ["US"]
            
            # Convert strings to Plaid enums
            plaid_countries = [CountryCode(c) for c in country_codes]
            plaid_products = [PlaidProduct(p) for p in products] if products else None
            
            request = InstitutionsGetRequest(
                count=count,
                offset=offset,
                country_codes=plaid_countries,
                products=plaid_products
            )
            
            response = client.institutions_get(request)
            
            institutions = []
            for inst in response['institutions']:
                institutions.append({
                    'institution_id': inst['institution_id'],
                    'name': inst['name'],
                    'products': inst['products'],
                    'country_codes': inst['country_codes'],
                    'url': inst.get('url'),
                    'primary_color': inst.get('primary_color'),
                    'logo': inst.get('logo'),
                    'oauth': inst.get('oauth', False),
                    'routing_numbers': inst.get('routing_numbers', []),
                    'dtc_numbers': inst.get('dtc_numbers', []),
                    'environment': environment
                })
            
            result = {
                'institutions': institutions,
                'total': response['total'],
                'request_id': response['request_id'],
                'environment': environment
            }
            
            logger.info(f"Retrieved {len(institutions)} institutions from Plaid {environment}")
            return result
            
        except Exception as e:
            logger.error(f"Error getting institutions from Plaid {environment}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get institutions from Plaid: {str(e)}"
            )
    
    async def get_institution_by_id_plaid(
        self, 
        institution_id: str,
        country_codes: Optional[List[str]] = None,
        include_optional_metadata: bool = False,
        include_status: bool = False,
        environment: str = "sandbox"
    ) -> Dict[str, Any]:
        """Get institution by ID from Plaid API"""
        try:
            if not self.plaid_service.is_environment_available(environment):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Plaid environment '{environment}' is not available"
                )
            
            client = self.plaid_service._get_client(environment)
            
            # Default values
            if country_codes is None:
                country_codes = ["US"]
            
            # Convert strings to Plaid enums
            plaid_countries = [CountryCode(c) for c in country_codes]
            
            request = InstitutionsGetByIdRequest(
                institution_id=institution_id,
                country_codes=plaid_countries,
                include_optional_metadata=include_optional_metadata,
                include_status=include_status
            )
            
            response = client.institutions_get_by_id(request)
            institution = response['institution']
            
            result = {
                'institution_id': institution['institution_id'],
                'name': institution['name'],
                'products': institution['products'],
                'country_codes': institution['country_codes'],
                'url': institution.get('url'),
                'primary_color': institution.get('primary_color'),
                'logo': institution.get('logo'),
                'oauth': institution.get('oauth', False),
                'routing_numbers': institution.get('routing_numbers', []),
                'dtc_numbers': institution.get('dtc_numbers', []),
                'status': institution.get('status'),
                'environment': environment,
                'request_id': response['request_id']
            }
            
            logger.info(f"Retrieved institution {institution_id} from Plaid {environment}")
            return result
            
        except Exception as e:
            logger.error(f"Error getting institution {institution_id} from Plaid {environment}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get institution from Plaid: {str(e)}"
            )
    
    async def import_institution_from_plaid(
        self, 
        institution_id: str,
        environment: str = "sandbox"
    ) -> PlaidInstitutionResponse:
        """Import an institution from Plaid API into the database"""
        try:
            # Get institution data from Plaid
            institution_data = await self.get_institution_by_id_plaid(
                institution_id=institution_id,
                include_optional_metadata=True,
                include_status=True,
                environment=environment
            )
            
            # Store in database
            response = self.sync_institution_db(institution_id, institution_data)
            
            logger.info(f"Imported institution {institution_id} from Plaid {environment} into database")
            return response
            
        except Exception as e:
            logger.error(f"Error importing institution {institution_id} from Plaid: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to import institution: {str(e)}"
            )
    
    async def bulk_import_institutions_from_plaid(
        self,
        institution_ids: List[str],
        environment: str = "sandbox"
    ) -> Dict[str, Any]:
        """Import multiple institutions from Plaid API into the database"""
        try:
            imported = []
            failed = []
            
            for institution_id in institution_ids:
                try:
                    response = await self.import_institution_from_plaid(
                        institution_id=institution_id,
                        environment=environment
                    )
                    imported.append({
                        'institution_id': institution_id,
                        'name': response.name,
                        'status': 'imported'
                    })
                except Exception as e:
                    failed.append({
                        'institution_id': institution_id,
                        'error': str(e),
                        'status': 'failed'
                    })
                    logger.warning(f"Failed to import institution {institution_id}: {str(e)}")
            
            result = {
                'imported_count': len(imported),
                'failed_count': len(failed),
                'imported': imported,
                'failed': failed,
                'environment': environment
            }
            
            logger.info(f"Bulk import completed: {len(imported)} imported, {len(failed)} failed")
            return result
            
        except Exception as e:
            logger.error(f"Error during bulk import: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to bulk import institutions: {str(e)}"
            )
    
    # ==========================================
    # Database Methods
    # ==========================================
    
    def get_institutions_db(self, limit: int = 100, offset: int = 0) -> List[PlaidInstitutionResponse]:
        """Get institutions from the database"""
        try:
            with get_db() as session:
                institutions = session.exec(
                    select(PlaidInstitution).offset(offset).limit(limit)
                ).all()
                
                responses = []
                for institution in institutions:
                    # TODO: Count items for this institution when items module is available
                    items_count = 0
                    
                    response = PlaidInstitutionResponse(
                        id=institution.id or "",
                        institution_id=institution.institution_id,
                        name=institution.name,
                        logo=institution.logo,
                        primary_color=institution.primary_color,
                        url=institution.url,
                        products=institution.products_list,
                        country_codes=institution.country_codes_list,
                        routing_numbers=institution.routing_numbers_list,
                        dtc_numbers=institution.dtc_numbers_list,
                        oauth=institution.oauth,
                        status=institution.status_dict,
                        created_at=institution.created_at,
                        updated_at=institution.updated_at,
                        items_count=items_count
                    )
                    responses.append(response)
                
                return responses
        
        except Exception as e:
            logger.error(f"Error getting institutions from database: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get institutions: {str(e)}"
            )

    def get_institution_by_id_db(self, institution_id: str) -> Optional[PlaidInstitutionResponse]:
        """Get institution by Plaid institution ID from database"""
        try:
            with get_db() as session:
                institution = session.exec(
                    select(PlaidInstitution).where(PlaidInstitution.institution_id == institution_id)
                ).first()
                
                if not institution:
                    return None
                
                # TODO: Count items for this institution when items module is available
                items_count = 0
                
                return PlaidInstitutionResponse(
                    id=institution.id or "",
                    institution_id=institution.institution_id,
                    name=institution.name,
                    logo=institution.logo,
                    primary_color=institution.primary_color,
                    url=institution.url,
                    products=institution.products_list,
                    country_codes=institution.country_codes_list,
                    routing_numbers=institution.routing_numbers_list,
                    dtc_numbers=institution.dtc_numbers_list,
                    oauth=institution.oauth,
                    status=institution.status_dict,
                    created_at=institution.created_at,
                    updated_at=institution.updated_at,
                    items_count=items_count
                )
                
        except Exception as e:
            logger.error(f"Error getting institution {institution_id} from database: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get institution: {str(e)}"
            )

    def sync_institution_db(self, institution_id: str, institution_data: Dict[str, Any]) -> PlaidInstitutionResponse:
        """Sync institution data to database"""
        try:
            with get_db() as session:
                # Check if institution already exists
                existing = session.exec(
                    select(PlaidInstitution).where(PlaidInstitution.institution_id == institution_id)
                ).first()
                
                if existing:
                    # Update existing institution
                    existing.name = institution_data.get('name', existing.name)
                    existing.logo = institution_data.get('logo')
                    existing.primary_color = institution_data.get('primary_color')
                    existing.url = institution_data.get('url')
                    existing.products_list = institution_data.get('products', [])
                    existing.country_codes_list = institution_data.get('country_codes', [])
                    existing.routing_numbers_list = institution_data.get('routing_numbers', [])
                    existing.dtc_numbers_list = institution_data.get('dtc_numbers', [])
                    existing.oauth = institution_data.get('oauth', False)
                    existing.status_dict = institution_data.get('status', {})
                    existing.updated_at = datetime.utcnow()
                    
                    session.add(existing)
                    session.commit()
                    session.refresh(existing)
                    institution = existing
                else:
                    # Create new institution
                    institution = PlaidInstitution(
                        institution_id=institution_id,
                        name=institution_data.get('name', ''),
                        logo=institution_data.get('logo'),
                        primary_color=institution_data.get('primary_color'),
                        url=institution_data.get('url'),
                        oauth=institution_data.get('oauth', False)
                    )
                    institution.products_list = institution_data.get('products', [])
                    institution.country_codes_list = institution_data.get('country_codes', [])
                    institution.routing_numbers_list = institution_data.get('routing_numbers', [])
                    institution.dtc_numbers_list = institution_data.get('dtc_numbers', [])
                    institution.status_dict = institution_data.get('status', {})
                    
                    session.add(institution)
                    session.commit()
                    session.refresh(institution)
                
                # TODO: Count items for this institution when items module is available
                items_count = 0
                
                return PlaidInstitutionResponse(
                    id=institution.id or "",
                    institution_id=institution.institution_id,
                    name=institution.name,
                    logo=institution.logo,
                    primary_color=institution.primary_color,
                    url=institution.url,
                    products=institution.products_list,
                    country_codes=institution.country_codes_list,
                    routing_numbers=institution.routing_numbers_list,
                    dtc_numbers=institution.dtc_numbers_list,
                    oauth=institution.oauth,
                    status=institution.status_dict,
                    created_at=institution.created_at,
                    updated_at=institution.updated_at,
                    items_count=items_count
                )
                
        except Exception as e:
            logger.error(f"Error syncing institution {institution_id} to database: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to sync institution: {str(e)}"
            )

    def ensure_institution_exists_db(self, institution_id: str, institution_data: Dict[str, Any]) -> PlaidInstitution:
        """Ensure institution exists in database, create if it doesn't exist"""
        try:
            with get_db() as session:
                # Check if institution already exists
                existing = session.exec(
                    select(PlaidInstitution).where(PlaidInstitution.institution_id == institution_id)
                ).first()
                
                if existing:
                    return existing
                
                logger.info(f"Creating new institution {institution_id} in database")
                
                # Create new institution
                institution = PlaidInstitution(
                    institution_id=institution_id,
                    name=institution_data.get('name', ''),
                    logo=institution_data.get('logo'),
                    primary_color=institution_data.get('primary_color'),
                    url=institution_data.get('url'),
                    oauth=institution_data.get('oauth', False)
                )
                institution.products_list = institution_data.get('products', [])
                institution.country_codes_list = institution_data.get('country_codes', [])
                institution.routing_numbers_list = institution_data.get('routing_numbers', [])
                institution.dtc_numbers_list = institution_data.get('dtc_numbers', [])
                institution.status_dict = institution_data.get('status', {})
                
                session.add(institution)
                session.commit()
                session.refresh(institution)
                
                logger.info(f"Created institution {institution_id}: {institution.name}")
                return institution
                
        except Exception as e:
            logger.error(f"Error ensuring institution {institution_id} exists in database: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to ensure institution exists: {str(e)}"
            )

    def search_institutions_db(self, query: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[PlaidInstitutionResponse]:
        """Search institutions in database"""
        try:
            with get_db() as session:
                stmt = select(PlaidInstitution)
                
                if query:
                    # Search in institution name and ID
                    search_term = f"%{query.lower()}%"
                    from sqlalchemy import func
                    stmt = stmt.where(
                        func.lower(PlaidInstitution.name).like(search_term) |
                        func.lower(PlaidInstitution.institution_id).like(search_term)
                    )
                
                institutions = session.exec(
                    stmt.offset(offset).limit(limit).order_by(PlaidInstitution.name)
                ).all()
                
                responses = []
                for institution in institutions:
                    # TODO: Count items for this institution when items module is available
                    items_count = 0
                    
                    response = PlaidInstitutionResponse(
                        id=institution.id or "",
                        institution_id=institution.institution_id,
                        name=institution.name,
                        logo=institution.logo,
                        primary_color=institution.primary_color,
                        url=institution.url,
                        products=institution.products_list,
                        country_codes=institution.country_codes_list,
                        routing_numbers=institution.routing_numbers_list,
                        dtc_numbers=institution.dtc_numbers_list,
                        oauth=institution.oauth,
                        status=institution.status_dict,
                        created_at=institution.created_at,
                        updated_at=institution.updated_at,
                        items_count=items_count
                    )
                    responses.append(response)
                
                return responses
                
        except Exception as e:
            logger.error(f"Error searching institutions in database: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to search institutions: {str(e)}"
            )

    def delete_institution_db(self, institution_id: str) -> bool:
        """Delete institution from database"""
        try:
            with get_db() as session:
                # Check if institution exists
                institution = session.exec(
                    select(PlaidInstitution).where(PlaidInstitution.institution_id == institution_id)
                ).first()
                
                if not institution:
                    return False
                
                # TODO: Check for existing items/accounts/transactions before deletion
                # For now, proceed with deletion
                
                session.delete(institution)
                session.commit()
                
                logger.info(f"Deleted institution {institution_id} from database")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting institution {institution_id} from database: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete institution: {str(e)}"
            )


