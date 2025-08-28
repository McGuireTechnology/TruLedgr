"""
Plaid Link Service

Service layer for handling Link token creation and public token exchange.
"""

from typing import Dict, Any, Optional, List
import logging
from .models import LinkTokenCreateRequest, LinkUser, PlaidProduct, CountryCode

logger = logging.getLogger(__name__)

class LinkService:
    """Service for handling Plaid Link operations"""
    
    def __init__(self, plaid_client):
        self.client = plaid_client
    
    async def create_link_token(
        self,
        user_id: str,
        client_name: str = "TruLedgr",
        products: Optional[List[str]] = None,
        webhook: Optional[str] = None,
        environment: str = 'production'
    ) -> Dict[str, Any]:
        """
        Create a Link token for initializing Plaid Link.
        
        Args:
            user_id: Unique identifier for the user
            client_name: Name of your application
            products: List of Plaid products to enable
            webhook: Webhook URL for notifications
            environment: Plaid environment ('production' or 'sandbox')
            
        Returns:
            Dict containing Link token and expiration
        """
        try:
            from plaid.model.link_token_create_request import LinkTokenCreateRequest
            from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
            from plaid.model.country_code import CountryCode
            from plaid.model.products import Products
            
            client = self.client._get_client(environment)
            
            # Default products if none provided
            if products is None:
                products = [Products('transactions'), Products('auth'), Products('identity')]
            else:
                products = [Products(product) for product in products]
            
            # Create user object
            user = LinkTokenCreateRequestUser(client_user_id=user_id)
            
            # Create request
            request = LinkTokenCreateRequest(
                products=products,
                client_name=client_name,
                country_codes=[CountryCode('US')],
                language='en',
                user=user,
                webhook=webhook
            )
            
            response = client.link_token_create(request)
            
            return {
                'link_token': response['link_token'],
                'expiration': response['expiration'],
                'request_id': response['request_id'],
                'environment': environment
            }
            
        except Exception as e:
            logger.error(f"Error creating Link token in {environment}: {str(e)}")
            raise
    
    async def exchange_public_token(
        self,
        public_token: str,
        environment: str = 'production'
    ) -> Dict[str, Any]:
        """
        Exchange a public token for an access token.
        
        Args:
            public_token: Public token received from Link onSuccess
            environment: Plaid environment ('production' or 'sandbox')
            
        Returns:
            Dict containing access token and item ID
        """
        try:
            from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
            
            client = self.client._get_client(environment)
            
            request = ItemPublicTokenExchangeRequest(public_token=public_token)
            response = client.item_public_token_exchange(request)
            
            return {
                'access_token': response['access_token'],
                'item_id': response['item_id'],
                'request_id': response['request_id'],
                'environment': environment
            }
            
        except Exception as e:
            logger.error(f"Error exchanging public token in {environment}: {str(e)}")
            raise
    
    async def create_update_mode_link_token(
        self,
        access_token: str,
        user_id: str,
        client_name: str = "TruLedgr",
        webhook: Optional[str] = None,
        environment: str = 'production'
    ) -> Dict[str, Any]:
        """
        Create a Link token for update mode to re-authenticate or reconnect an Item.
        
        Args:
            access_token: Access token for the Item to update
            user_id: Unique identifier for the user
            client_name: Name of your application
            webhook: Webhook URL for notifications
            environment: Plaid environment ('production' or 'sandbox')
            
        Returns:
            Dict containing Link token for update mode
        """
        try:
            from plaid.model.link_token_create_request import LinkTokenCreateRequest
            from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
            from plaid.model.link_token_create_request_update import LinkTokenCreateRequestUpdate
            from plaid.model.country_code import CountryCode
            
            client = self.client._get_client(environment)
            
            # Create user object
            user = LinkTokenCreateRequestUser(client_user_id=user_id)
            
            # Create update object
            update = LinkTokenCreateRequestUpdate(account_selection_enabled=True)
            
            # Create request
            request = LinkTokenCreateRequest(
                client_name=client_name,
                country_codes=[CountryCode('US')],
                language='en',
                user=user,
                webhook=webhook,
                access_token=access_token,
                update=update
            )
            
            response = client.link_token_create(request)
            
            return {
                'link_token': response['link_token'],
                'expiration': response['expiration'],
                'request_id': response['request_id'],
                'environment': environment,
                'mode': 'update'
            }
            
        except Exception as e:
            logger.error(f"Error creating update mode Link token in {environment}: {str(e)}")
            raise
