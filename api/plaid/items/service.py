"""
Plaid Items Service

Service layer for handling Item management, status operations, and database operations.
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlmodel import Session, select, desc
from fastapi import HTTPException, status
import logging

from api.db.deps import get_db
from api.users.models import User
from .models import PlaidItem, PlaidItemResponse, PlaidEnvironment, ItemStatus

logger = logging.getLogger(__name__)

class ItemsService:
    """Service for handling Plaid Item operations"""
    
    def __init__(self, plaid_client):
        self.client = plaid_client
    
    # Database Operations
    async def create_item(self, user_id: int, public_token: str, environment: PlaidEnvironment = PlaidEnvironment.SANDBOX) -> PlaidItemResponse:
        """Create a new Plaid item from a public token"""
        try:
            # Exchange public token for access token
            token_data = await self.exchange_public_token(public_token, environment.value)
            
            access_token = token_data['access_token']
            item_id = token_data['item_id']
            
            # Get item details to extract institution info
            item_details = await self.get_item_details(access_token, environment.value)
            institution_id = item_details.get('institution_id', 'unknown')
            
            # Get institution details and ensure it exists in our database
            from ..institutions.service import InstitutionsService
            institutions_service = InstitutionsService(self.client)
            institution = await institutions_service.ensure_institution_exists(institution_id, environment.value)
            institution_name = institution.name if institution else "Unknown Institution"
            
            with get_db() as session:
                # Get user first
                user = session.exec(
                    select(User).where(User.id == user_id)
                ).first()
                
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User not found"
                    )
                
                # Check if item already exists
                existing_item = session.exec(
                    select(PlaidItem).where(PlaidItem.item_id == item_id)
                ).first()
                
                if existing_item:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="This account is already connected"
                    )
                
                # Create new item with comprehensive Plaid data
                new_item = PlaidItem(
                    user_id=str(user.id) if user.id else "",
                    item_id=item_id,
                    environment=environment.value,
                    access_token=access_token,
                    institution_id=institution_id,
                    institution_name=institution_name,
                    status=ItemStatus.ACTIVE.value,
                    
                    # Product information
                    available_products=json.dumps(item_details.get('available_products', [])),
                    billed_products=json.dumps(item_details.get('billed_products', [])),
                    products=json.dumps(item_details.get('products', [])),
                    consented_products=json.dumps(item_details.get('consented_products', [])),
                    
                    # Consent and authorization
                    auth_method=item_details.get('auth_method'),
                    consent_expiration_time=self._parse_consent_expiration(item_details.get('consent_expiration_time')),
                    consented_use_cases=json.dumps(item_details.get('consented_use_cases', [])),
                    consented_data_scopes=json.dumps(item_details.get('consented_data_scopes', [])),
                    
                    # Update behavior
                    update_type=item_details.get('update_type', 'background'),
                    
                    # Plaid creation timestamp
                    plaid_created_at=self._parse_plaid_timestamp(item_details.get('created_at')),
                    
                    # Webhook
                    webhook_url=item_details.get('webhook')
                )
                
                session.add(new_item)
                session.commit()
                session.refresh(new_item)
                
                # Sync accounts immediately after creating item
                from ..accounts.service import AccountsService
                accounts_service = AccountsService(self.client)
                # TODO: Implement sync_item_accounts method in AccountsService
                # await accounts_service.sync_item_accounts(new_item.id or "", session)
                
                logger.info(f"Created Plaid item {item_id} for user {user.id}")
                
                return self._item_to_response(new_item)
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating Plaid item: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create item: {str(e)}"
            )

    async def get_user_items(self, user_id: int) -> List[PlaidItemResponse]:
        """Get all Plaid items for a user"""
        with get_db() as session:
            items = session.exec(
                select(PlaidItem).where(PlaidItem.user_id == str(user_id))
                .order_by(desc(PlaidItem.created_at))
            ).all()
            
            responses = []
            for item in items:
                # Count accounts for this item
                from ..accounts.models import PlaidAccount
                accounts_count = session.exec(
                    select(PlaidAccount).where(
                        PlaidAccount.item_id == item.id,
                        PlaidAccount.is_active == True
                    )
                ).fetchall()
                
                response = self._item_to_response(item)
                response.accounts_count = len(accounts_count)
                responses.append(response)
            
            logger.info(f"Retrieved {len(responses)} items for user {user_id}")
            return responses

    async def delete_item(self, user_id: int, item_id: str) -> bool:
        """Delete a Plaid item and its associated data"""
        with get_db() as session:
            item = session.exec(
                select(PlaidItem).where(
                    PlaidItem.id == item_id,
                    PlaidItem.user_id == str(user_id)
                )
            ).first()
            
            if not item:
                return False
            
            # Delete associated transactions
            from ..transactions.models import PlaidTransaction
            from ..accounts.models import PlaidAccount
            
            transactions = session.exec(
                select(PlaidTransaction).where(
                    PlaidTransaction.user_id == str(user_id)
                )
            ).all()
            for transaction in transactions:
                # Only delete transactions for accounts belonging to this item
                account = session.exec(
                    select(PlaidAccount).where(
                        PlaidAccount.id == transaction.account_id,
                        PlaidAccount.item_id == item_id
                    )
                ).first()
                if account:
                    session.delete(transaction)
            
            # Delete associated accounts
            accounts = session.exec(
                select(PlaidAccount).where(PlaidAccount.item_id == item_id)
            ).all()
            for account in accounts:
                session.delete(account)
            
            # Delete the item
            session.delete(item)
            session.commit()
            
            logger.info(f"Deleted Plaid item {item_id} for user {user_id}")
            return True

    async def sync_item_from_plaid(self, item_id: str, user_id: int) -> PlaidItemResponse:
        """Sync item data from Plaid API and update database"""
        with get_db() as session:
            # Get item from database
            item = session.exec(
                select(PlaidItem).where(
                    PlaidItem.id == item_id,
                    PlaidItem.user_id == str(user_id)
                )
            ).first()
            
            if not item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Item not found"
                )
            
            try:
                # Get fresh data from Plaid
                plaid_data = await self.get_item(item.access_token, item.environment)
                plaid_item_data = plaid_data['item']
                
                # Update item with fresh data
                self._update_item_from_plaid_data(item, plaid_item_data)
                
                session.add(item)
                session.commit()
                session.refresh(item)
                
                logger.info(f"Synced Plaid item {item.item_id} for user {user_id}")
                return self._item_to_response(item)
                
            except Exception as e:
                logger.error(f"Error syncing item {item_id}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to sync item: {str(e)}"
                )

    async def handle_webhook_event(self, webhook_data: Dict[str, Any]) -> bool:
        """Handle item webhook event and update database"""
        try:
            webhook_type = webhook_data.get('webhook_type')
            webhook_code = webhook_data.get('webhook_code')
            item_id = webhook_data.get('item_id')
            environment = webhook_data.get('environment', 'production')
            
            if webhook_type != 'ITEM':
                return False
                
            with get_db() as session:
                # Find item by plaid item_id
                item = session.exec(
                    select(PlaidItem).where(PlaidItem.item_id == item_id)
                ).first()
                
                if not item:
                    logger.warning(f"Received webhook for unknown item: {item_id}")
                    return False
                
                # Create webhook event record
                from .models import PlaidItemWebhookEvent
                webhook_event = PlaidItemWebhookEvent(
                    item_id=item.id or "",
                    webhook_type=webhook_type or "ITEM",
                    webhook_code=webhook_code or "UNKNOWN",
                    webhook_payload=json.dumps(webhook_data),
                    environment=environment
                )
                
                session.add(webhook_event)
                
                # Handle specific webhook events
                if webhook_code == 'ERROR':
                    # Update item status to error
                    error_data = webhook_data.get('error', {})
                    item.status = ItemStatus.ERROR.value
                    item.error_type = error_data.get('error_type')
                    item.error_code = error_data.get('error_code')
                    item.error_message = error_data.get('error_message')
                    item.error_display_message = error_data.get('display_message')
                    
                elif webhook_code == 'LOGIN_REPAIRED':
                    # Clear error status
                    item.status = ItemStatus.ACTIVE.value
                    item.error_type = None
                    item.error_code = None
                    item.error_message = None
                    item.error_display_message = None
                    
                elif webhook_code == 'USER_PERMISSION_REVOKED':
                    # Mark item as inactive
                    item.status = ItemStatus.INACTIVE.value
                    
                # Update webhook event as processed
                webhook_event.processed = True
                webhook_event.processed_at = datetime.utcnow()
                
                session.add(item)
                session.commit()
                
                logger.info(f"Processed webhook {webhook_code} for item {item_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error handling webhook event: {str(e)}")
            return False

    async def create_link_token(self, user_id: int, environment: PlaidEnvironment = PlaidEnvironment.SANDBOX) -> Dict[str, Any]:
        """Create a link token for Plaid Link initialization"""
        try:
            # Use the existing Plaid client to create the link token
            result = await self.create_link_token_api(
                user_id=str(user_id),
                user_name=f"user_{user_id}",
                environment=environment.value
            )
            
            logger.info(f"Created link token for user {user_id} in {environment.value}")
            return result
            
        except Exception as e:
            logger.error(f"Error creating link token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create link token: {str(e)}"
            )

    # Plaid API Operations
    async def exchange_public_token(self, public_token: str, environment: str) -> Dict[str, Any]:
        """Exchange public token for access token"""
        try:
            from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
            
            client = self.client._get_client(environment)
            
            request = ItemPublicTokenExchangeRequest(public_token=public_token)
            response = client.item_public_token_exchange(request)
            
            return response.to_dict()
            
        except Exception as e:
            logger.error(f"Error exchanging public token: {str(e)}")
            raise

    async def get_item_details(self, access_token: str, environment: str) -> Dict[str, Any]:
        """Get item details from Plaid"""
        try:
            item_data = await self.get_item(access_token, environment)
            return item_data['item']
            
        except Exception as e:
            logger.error(f"Error getting item details: {str(e)}")
            raise

    async def create_link_token_api(self, user_id: str, user_name: str, environment: str) -> Dict[str, Any]:
        """Create link token via Plaid API"""
        try:
            from plaid.model.link_token_create_request import LinkTokenCreateRequest
            from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
            from plaid.model.country_code import CountryCode
            from plaid.model.products import Products
            
            client = self.client._get_client(environment)
            
            # Configure user
            user = LinkTokenCreateRequestUser(client_user_id=user_id)
            
            # Configure request
            request = LinkTokenCreateRequest(
                products=[Products('transactions'), Products('auth')],
                client_name="TruLedgr",
                country_codes=[CountryCode('US')],
                language='en',
                user=user
            )
            
            response = client.link_token_create(request)
            return response.to_dict()
            
        except Exception as e:
            logger.error(f"Error creating link token: {str(e)}")
            raise

    # Private helper methods
    def _item_to_response(self, item: PlaidItem) -> PlaidItemResponse:
        """Convert PlaidItem to response model"""
        return PlaidItemResponse(
            id=item.id or "",
            item_id=item.item_id,
            institution_id=item.institution_id,
            institution_name=item.institution_name,
            environment=PlaidEnvironment(item.environment) if item.environment else PlaidEnvironment.SANDBOX,
            status=ItemStatus(item.status) if item.status else ItemStatus.ACTIVE,
            
            # Error information
            error_type=item.error_type,
            error_code=item.error_code,
            error_message=item.error_message,
            error_display_message=item.error_display_message,
            error_documentation_url=item.error_documentation_url,
            error_suggested_action=item.error_suggested_action,
            
            # Product information
            available_products=item.available_products_list,
            billed_products=item.billed_products_list,
            products=item.products_list,
            consented_products=item.consented_products_list,
            
            # Consent and authorization
            auth_method=item.auth_method,
            consent_expiration_time=item.consent_expiration_time,
            consented_use_cases=item.consented_use_cases_list,
            consented_data_scopes=item.consented_data_scopes_list,
            
            # Update behavior
            update_type=item.update_type,
            
            # Timestamps
            plaid_created_at=item.plaid_created_at,
            created_at=item.created_at,
            updated_at=item.updated_at,
            last_sync=item.last_sync,
            
            # Additional metadata
            webhook_url=item.webhook_url
        )

    def _parse_consent_expiration(self, consent_expiration_str: Optional[str]) -> Optional[datetime]:
        """Parse consent expiration time from Plaid API response"""
        if not consent_expiration_str:
            return None
        try:
            from dateutil import parser
            return parser.isoparse(consent_expiration_str.replace('Z', '+00:00'))
        except Exception as e:
            logger.warning(f"Failed to parse consent expiration time {consent_expiration_str}: {e}")
            return None

    def _parse_plaid_timestamp(self, timestamp_str: Optional[str]) -> Optional[datetime]:
        """Parse timestamp from Plaid API response"""
        if not timestamp_str:
            return None
        try:
            from dateutil import parser
            return parser.isoparse(timestamp_str.replace('Z', '+00:00'))
        except Exception as e:
            logger.warning(f"Failed to parse Plaid timestamp {timestamp_str}: {e}")
            return None

    def _update_item_from_plaid_data(self, item: PlaidItem, plaid_item_data: Dict[str, Any]) -> None:
        """Update PlaidItem with data from Plaid API response"""
        # Update product information
        item.available_products_list = plaid_item_data.get('available_products', [])
        item.billed_products_list = plaid_item_data.get('billed_products', [])
        item.products_list = plaid_item_data.get('products', [])
        item.consented_products_list = plaid_item_data.get('consented_products', [])
        
        # Update consent and authorization
        item.auth_method = plaid_item_data.get('auth_method')
        item.consent_expiration_time = self._parse_consent_expiration(plaid_item_data.get('consent_expiration_time'))
        item.consented_use_cases_list = plaid_item_data.get('consented_use_cases', [])
        item.consented_data_scopes_list = plaid_item_data.get('consented_data_scopes', [])
        
        # Update behavior and metadata
        item.update_type = plaid_item_data.get('update_type', 'background')
        item.webhook_url = plaid_item_data.get('webhook')
        
        # Update error information if present
        error_data = plaid_item_data.get('error')
        if error_data:
            item.error_type = error_data.get('error_type')
            item.error_code = error_data.get('error_code')
            item.error_message = error_data.get('error_message')
            item.error_display_message = error_data.get('display_message')
            item.error_documentation_url = error_data.get('documentation_url')
            item.error_suggested_action = error_data.get('suggested_action')
            item.status = ItemStatus.ERROR.value
        else:
            # Clear error information if no error
            item.error_type = None
            item.error_code = None
            item.error_message = None
            item.error_display_message = None
            item.error_documentation_url = None
            item.error_suggested_action = None
            if item.status == ItemStatus.ERROR.value:
                item.status = ItemStatus.ACTIVE.value
        
        # Update timestamps
        item.plaid_created_at = self._parse_plaid_timestamp(plaid_item_data.get('created_at'))
        item.last_sync = datetime.utcnow()

    # Existing Plaid API methods (unmodified)
    
    async def get_item(
        self,
        access_token: str,
        environment: str = 'production'
    ) -> Dict[str, Any]:
        """
        Get information about an Item.
        
        Returns metadata about the Item including available products,
        billed products, institution information, and error status.
        
        Args:
            access_token: Access token for the Item
            environment: Plaid environment ('production' or 'sandbox')
            
        Returns:
            Dict containing Item information
        """
        try:
            from plaid.model.item_get_request import ItemGetRequest
            
            client = self.client._get_client(environment)
            
            request = ItemGetRequest(access_token=access_token)
            response = client.item_get(request)
            
            # Convert response to dictionary format
            result = response.to_dict()
            item_data = result['item']
            
            return {
                'item': {
                    'item_id': item_data['item_id'],
                    'institution_id': item_data.get('institution_id'),
                    'institution_name': item_data.get('institution_name'),
                    'webhook': item_data.get('webhook'),
                    'error': item_data.get('error'),
                    'available_products': item_data.get('available_products', []),
                    'billed_products': item_data.get('billed_products', []),
                    'products': item_data.get('products', []),
                    'consented_products': item_data.get('consented_products', []),
                    'consent_expiration_time': item_data.get('consent_expiration_time'),
                    'update_type': item_data.get('update_type', 'background')
                },
                'status': result.get('status'),
                'request_id': result['request_id'],
                'environment': environment
            }
            
        except Exception as e:
            logger.error(f"Error getting Item in {environment}: {str(e)}")
            raise
    
    async def remove_item(
        self,
        access_token: str,
        environment: str = 'production'
    ) -> Dict[str, Any]:
        """
        Remove an Item.
        
        Once removed, the access_token associated with the Item
        is no longer valid and cannot be used to access any data
        that was associated with the Item.
        
        Args:
            access_token: Access token for the Item to remove
            environment: Plaid environment ('production' or 'sandbox')
            
        Returns:
            Dict containing removal confirmation
        """
        try:
            from plaid.model.item_remove_request import ItemRemoveRequest
            
            client = self.client._get_client(environment)
            
            request = ItemRemoveRequest(access_token=access_token)
            response = client.item_remove(request)
            
            return {
                'removed': True,
                'request_id': response['request_id'],
                'environment': environment,
                'message': 'Item successfully removed'
            }
            
        except Exception as e:
            logger.error(f"Error removing Item in {environment}: {str(e)}")
            raise
    
    async def update_webhook(
        self,
        access_token: str,
        webhook_url: Optional[str] = None,
        environment: str = 'production'
    ) -> Dict[str, Any]:
        """
        Update the webhook URL for an Item.
        
        The webhook URL is used to send notifications about Item events
        such as transaction updates, errors, and consent expirations.
        
        Args:
            access_token: Access token for the Item
            webhook_url: New webhook URL (None to remove webhook)
            environment: Plaid environment ('production' or 'sandbox')
            
        Returns:
            Dict containing updated Item information
        """
        try:
            from plaid.model.item_webhook_update_request import ItemWebhookUpdateRequest
            
            client = self.client._get_client(environment)
            
            request = ItemWebhookUpdateRequest(
                access_token=access_token,
                webhook=webhook_url
            )
            response = client.item_webhook_update(request)
            
            # Convert response to dictionary format  
            result = response.to_dict()
            item_data = result['item']
            
            return {
                'item': {
                    'item_id': item_data['item_id'],
                    'institution_id': item_data.get('institution_id'),
                    'institution_name': item_data.get('institution_name'),
                    'webhook': item_data.get('webhook'),
                    'error': item_data.get('error'),
                    'available_products': item_data.get('available_products', []),
                    'billed_products': item_data.get('billed_products', []),
                    'products': item_data.get('products', []),
                    'consented_products': item_data.get('consented_products', []),
                    'consent_expiration_time': item_data.get('consent_expiration_time'),
                    'update_type': item_data.get('update_type', 'background')
                },
                'request_id': result['request_id'],
                'environment': environment,
                'message': f'Webhook {"updated" if webhook_url else "removed"} successfully'
            }
            
        except Exception as e:
            logger.error(f"Error updating Item webhook in {environment}: {str(e)}")
            raise
