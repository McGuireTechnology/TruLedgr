"""
Plaid service integration for TruLedgr API
Core banking integration functionality with database operations

This service handles the fundamental Plaid APIs and coordinates database operations:
- Link token creation and public token exchange  
- Account information retrieval
- Basic transaction retrieval
- Institution information lookup
- Single environment support (sandbox for development)

Database operations coordination with modular services

Specialized services are located in submodules:
- transactions/: Advanced transaction management
- investments/: Investment holdings and transactions
- liabilities/: Credit cards, mortgages, student loans
- webhooks/: Webhook verification and processing
- enrich/: Transaction enrichment services
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging

from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.item_get_request import ItemGetRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
from plaid.model.institutions_get_by_id_request import InstitutionsGetByIdRequest
from plaid.configuration import Configuration
from plaid.api_client import ApiClient

logger = logging.getLogger(__name__)

class PlaidService:
    """Core Plaid service for fundamental banking integration"""
    
    def __init__(self):
        # Plaid configuration - single environment
        self.client_id = os.getenv('PLAID_CLIENT_ID')
        self.secret = os.getenv('PLAID_SECRET')
        self.client: Optional[plaid_api.PlaidApi] = None
        
        # Check if we have valid credentials (not placeholder values)
        if (not self.client_id or not self.secret or 
            self.client_id == 'your-plaid-client-id' or 
            self.secret == 'your-plaid-secret-key'):
            logger.warning("Plaid credentials not configured - Plaid service will be limited")
            self.client = None
            return
        
        # Create single client
        self._setup_client()
        
        logger.info("Plaid service initialized successfully")
    
    def _setup_client(self):
        """Setup Plaid client"""
        from plaid.configuration import Environment
        
        try:
            configuration = Configuration(
                host=Environment.Sandbox,  # Always use sandbox
                api_key={
                    'clientId': self.client_id,
                    'secret': self.secret
                }
            )
            api_client = ApiClient(configuration)
            self.client = plaid_api.PlaidApi(api_client)
            logger.info("Plaid client configured successfully")
        except Exception as e:
            logger.error(f"Failed to configure Plaid client: {str(e)}")
            self.client = None
    
    def get_client(self) -> plaid_api.PlaidApi:
        """Get the Plaid client"""
        if not self.client:
            raise ValueError("Plaid client not configured. Check your credentials.")
        return self.client
    
    async def create_link_token(self, user_id: str, user_name: Optional[str] = None) -> Dict[str, Any]:
        """Create a link token for Plaid Link initialization
        
        Args:
            user_id: Unique identifier for the user
            user_name: Optional user name for display
        """
        if not self.client:
            raise ValueError("Plaid client not configured - check credentials")
            
        try:
            request = LinkTokenCreateRequest(
                products=[Products('transactions')],
                client_name="TruLedgr",
                country_codes=[CountryCode('US')],
                language='en',
                user=LinkTokenCreateRequestUser(client_user_id=user_id)
            )
            
            response = self.client.link_token_create(request)
            
            return {
                'link_token': response['link_token'],
                'expiration': response['expiration'],
                'request_id': response['request_id']
            }
            
        except Exception as e:
            logger.error(f"Error creating link token: {str(e)}")
            raise
    
    async def exchange_public_token(self, public_token: str) -> Dict[str, Any]:
        """Exchange public token for access token
        
        Args:
            public_token: The public token from Plaid Link
        """
        if not self.client:
            raise ValueError("Plaid client not configured - check credentials")
            
        try:
            request = ItemPublicTokenExchangeRequest(public_token=public_token)
            response = self.client.item_public_token_exchange(request)
            
            return {
                'access_token': response['access_token'],
                'item_id': response['item_id'],
                'request_id': response['request_id']
            }
            
        except Exception as e:
            logger.error(f"Error exchanging public token: {str(e)}")
            raise
    
    async def get_item_details(self, access_token: str) -> Dict[str, Any]:
        """Get item details including institution information
        
        Args:
            access_token: The access token for the connected account
        """
        if not self.client:
            raise ValueError("Plaid client not configured - check credentials")
            
        try:
            request = ItemGetRequest(access_token=access_token)
            response = self.client.item_get(request)
            
            return {
                'item_id': response['item']['item_id'],
                'institution_id': response['item']['institution_id'],
                'webhook': response['item']['webhook'],
                'error': response['item']['error'],
                'available_products': response['item']['available_products'],
                'billed_products': response['item']['billed_products'],
                'consent_expiration_time': response['item']['consent_expiration_time'],
                'update_type': response['item']['update_type']
            }
            
        except Exception as e:
            logger.error(f"Error getting item details: {str(e)}")
            raise
    
    async def get_accounts(self, access_token: str) -> List[Dict[str, Any]]:
        """Get account information for a connected item
        
        Args:
            access_token: The access token for the connected account
        """
        if not self.client:
            raise ValueError("Plaid client not configured - check credentials")
            
        try:
            request = AccountsGetRequest(access_token=access_token)
            response = self.client.accounts_get(request)
            
            accounts = []
            for account in response['accounts']:
                accounts.append({
                    'account_id': account['account_id'],
                    'name': account['name'],
                    'official_name': account.get('official_name'),
                    'type': account['type'],
                    'subtype': account['subtype'],
                    'balances': {
                        'available': account['balances'].get('available'),
                        'current': account['balances'].get('current'),
                        'limit': account['balances'].get('limit'),
                        'iso_currency_code': account['balances'].get('iso_currency_code')
                    },
                    'mask': account.get('mask')
                })
            
            return accounts
            
        except Exception as e:
            logger.error(f"Error fetching accounts: {str(e)}")
            raise
    
    async def get_transactions(
        self, 
        access_token: str, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        account_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get transactions for connected accounts (basic implementation)
        
        For advanced transaction management, use the transactions submodule.
        
        Args:
            access_token: The access token for the connected account
            start_date: Start date for transactions (defaults to 30 days ago)
            end_date: End date for transactions (defaults to today)
            account_ids: Optional list of specific account IDs to fetch
        """
        if not self.client:
            raise ValueError("Plaid client not configured - check credentials")
            
        try:
            # Default to last 30 days if no dates provided
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()
            
            request = TransactionsGetRequest(
                access_token=access_token,
                start_date=start_date.date(),
                end_date=end_date.date()
            )
            
            if account_ids:
                request = TransactionsGetRequest(
                    access_token=access_token,
                    start_date=start_date.date(),
                    end_date=end_date.date(),
                    account_ids=account_ids
                )
            
            response = self.client.transactions_get(request)
            
            transactions = []
            for transaction in response['transactions']:
                transactions.append({
                    'transaction_id': transaction['transaction_id'],
                    'account_id': transaction['account_id'],
                    'amount': transaction['amount'],
                    'date': transaction['date'].isoformat(),
                    'name': transaction['name'],
                    'merchant_name': transaction.get('merchant_name'),
                    'category': transaction.get('category', []),
                    'category_id': transaction.get('category_id'),
                    'type': transaction.get('transaction_type'),
                    'pending': transaction.get('pending', False),
                    'account_owner': transaction.get('account_owner'),
                    'location': {
                        'address': transaction.get('location', {}).get('address'),
                        'city': transaction.get('location', {}).get('city'),
                        'region': transaction.get('location', {}).get('region'),
                        'postal_code': transaction.get('location', {}).get('postal_code'),
                        'country': transaction.get('location', {}).get('country')
                    } if transaction.get('location') else None,
                    'payment_meta': self._convert_payment_meta(transaction.get('payment_meta'))
                })
            
            return {
                'transactions': transactions,
                'total_transactions': response['total_transactions'],
                'accounts': [
                    {
                        'account_id': acc['account_id'],
                        'name': acc['name'],
                        'type': acc['type'],
                        'subtype': acc['subtype']
                    }
                    for acc in response['accounts']
                ],
                'request_id': response['request_id']
            }
            
        except Exception as e:
            logger.error(f"Error fetching transactions: {str(e)}")
            raise
    
    def _convert_payment_meta(self, payment_meta):
        """Convert PaymentMeta object to dictionary if necessary"""
        if payment_meta is None:
            return {}
        
        # If it's already a dict, return it
        if isinstance(payment_meta, dict):
            return payment_meta
        
        # If it has a to_dict method, use it
        if hasattr(payment_meta, 'to_dict'):
            return payment_meta.to_dict()
        
        # If it has attributes, convert to dict
        if hasattr(payment_meta, '__dict__'):
            return {k: v for k, v in payment_meta.__dict__.items() if not k.startswith('_')}
        
        # If it's some other object, try to convert to dict or return empty
        try:
            return dict(payment_meta)
        except (TypeError, ValueError):
            return {}
    
    async def get_institution_info(self, institution_id: str) -> Dict[str, Any]:
        """Get information about a financial institution
        
        Args:
            institution_id: The institution ID to look up
        """
        if not self.client:
            raise ValueError("Plaid client not configured - check credentials")
            
        try:
            request = InstitutionsGetByIdRequest(
                institution_id=institution_id,
                country_codes=[CountryCode('US')]
            )
            
            response = self.client.institutions_get_by_id(request)
            institution = response['institution']
            
            return {
                'institution_id': institution['institution_id'],
                'name': institution['name'],
                'products': institution['products'],
                'country_codes': institution['country_codes'],
                'url': institution.get('url'),
                'primary_color': institution.get('primary_color'),
                'logo': institution.get('logo')
            }
            
        except Exception as e:
            logger.error(f"Error fetching institution info: {str(e)}")
            raise
    
    # Database Operations Coordination
    def _ensure_modular_services(self):
        """Lazy initialize modular services"""
        if not hasattr(self, '_modular_services_initialized'):
            # Import here to avoid circular imports
            from .items.service import ItemsService
            from .accounts.service import AccountsService
            from .transactions.service import TransactionsService
            from .institutions.service import InstitutionsService
            
            self.items_service = ItemsService(self)
            self.accounts_service = AccountsService(self)
            self.transactions_service = TransactionsService(self)
            self.institutions_service = InstitutionsService(self)
            self._modular_services_initialized = True

    async def create_link_token_db(self, user_id: int) -> Dict[str, Any]:
        """Create a link token for Plaid Link initialization"""
        self._ensure_modular_services()
        from .items.models import PlaidEnvironment
        return await self.items_service.create_link_token(user_id, PlaidEnvironment.SANDBOX)

    async def create_item_db(self, user_id: int, public_token: str):
        """Create a new Plaid item from a public token"""
        self._ensure_modular_services()
        from .items.models import PlaidEnvironment
        return await self.items_service.create_item(user_id, public_token, PlaidEnvironment.SANDBOX)

    async def get_user_items_db(self, user_id: int):
        """Get all Plaid items for a user"""
        self._ensure_modular_services()
        return await self.items_service.get_user_items(user_id)

    async def delete_item_db(self, user_id: int, item_id: str) -> bool:
        """Delete a Plaid item and its associated data"""
        self._ensure_modular_services()
        return await self.items_service.delete_item(user_id, item_id)

    async def get_user_accounts_db(self, user_id: int):
        """Get all accounts for a user"""
        self._ensure_modular_services()
        return await self.accounts_service.get_user_accounts(user_id, None)

    async def sync_item_accounts_db(self, user_id: int, item_id: str):
        """Sync accounts for a specific item"""
        self._ensure_modular_services()
        return await self.accounts_service.sync_user_item_accounts(user_id, item_id)

    async def sync_item_transactions_db(self, user_id: int, item_id: str, days: int = 30) -> int:
        """Sync transactions for a specific item"""
        self._ensure_modular_services()
        return await self.transactions_service.sync_item_transactions(user_id, item_id, days)

    async def get_institutions_db(self, limit: int = 100, offset: int = 0):
        """Get institutions from database with pagination"""
        self._ensure_modular_services()
        return self.institutions_service.get_institutions_db(limit, offset)

    async def get_institution_by_id_db(self, institution_id: str):
        """Get institution from database by ID"""
        self._ensure_modular_services()
        return self.institutions_service.get_institution_by_id_db(institution_id)

    async def sync_institution_db(self, institution_id: str):
        """Sync institution data from Plaid and store in database"""
        self._ensure_modular_services()
        return self.institutions_service.sync_institution_db(institution_id)

    async def get_user_transactions_db(
        self, 
        user_id: int, 
        account_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ):
        """Get transactions for a user with pagination"""
        self._ensure_modular_services()
        return await self.transactions_service.get_user_transactions(
            user_id, account_id, start_date, end_date, limit, offset
        )

# Global instance
plaid_service: Optional[PlaidService] = None

def get_plaid_service() -> PlaidService:
    """Get or create the global PlaidService instance"""
    global plaid_service
    if plaid_service is None:
        plaid_service = PlaidService()
    return plaid_service
