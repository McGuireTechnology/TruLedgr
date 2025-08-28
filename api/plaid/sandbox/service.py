"""
Plaid Sandbox Service

Service layer for handling Sandbox testing and simulation operations.
"""

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class SandboxService:
    """Service for handling Plaid Sandbox operations"""
    
    def __init__(self, plaid_client):
        self.client = plaid_client
    
    async def create_public_token(
        self,
        institution_id: str,
        initial_products: List[str],
        options: Optional[Dict[str, Any]] = None,
        environment: str = 'sandbox'
    ) -> Dict[str, Any]:
        """
        Create a public token for testing in sandbox.
        
        Args:
            institution_id: Institution ID (e.g., 'ins_3')
            initial_products: List of products to enable
            options: Additional configuration options
            environment: Must be 'sandbox'
            
        Returns:
            Dict containing public token for testing
        """
        try:
            from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
            from plaid.model.products import Products
            
            client = self.client._get_client(environment)
            
            products_enum = [Products(product) for product in initial_products]
            
            request = SandboxPublicTokenCreateRequest(
                institution_id=institution_id,
                initial_products=products_enum,
                options=options
            )
            
            response = client.sandbox_public_token_create(request)
            
            return {
                'public_token': response['public_token'],
                'request_id': response['request_id'],
                'environment': environment,
                'institution_id': institution_id,
                'products': initial_products
            }
            
        except Exception as e:
            logger.error(f"Error creating sandbox public token: {str(e)}")
            raise
    
    async def fire_webhook(
        self,
        access_token: str,
        webhook_code: str,
        environment: str = 'sandbox'
    ) -> Dict[str, Any]:
        """
        Trigger a webhook for testing in sandbox.
        
        Args:
            access_token: Access token for the Item
            webhook_code: Webhook code to fire (e.g., 'DEFAULT_UPDATE')
            environment: Must be 'sandbox'
            
        Returns:
            Dict containing webhook fire confirmation
        """
        try:
            from plaid.model.sandbox_item_fire_webhook_request import SandboxItemFireWebhookRequest
            from plaid.model.sandbox_item_fire_webhook_request_webhook_code import SandboxItemFireWebhookRequestWebhookCode
            
            client = self.client._get_client(environment)
            
            webhook_code_enum = SandboxItemFireWebhookRequestWebhookCode(webhook_code)
            
            request = SandboxItemFireWebhookRequest(
                access_token=access_token,
                webhook_code=webhook_code_enum
            )
            
            response = client.sandbox_item_fire_webhook(request)
            
            return {
                'webhook_fired': True,
                'webhook_code': webhook_code,
                'request_id': response['request_id'],
                'environment': environment
            }
            
        except Exception as e:
            logger.error(f"Error firing sandbox webhook: {str(e)}")
            raise
    
    async def set_verification_status(
        self,
        access_token: str,
        account_id: str,
        verification_status: str,
        environment: str = 'sandbox'
    ) -> Dict[str, Any]:
        """
        Set the verification status for an account in sandbox.
        
        Args:
            access_token: Access token for the Item
            account_id: Account ID
            verification_status: New verification status
            environment: Must be 'sandbox'
            
        Returns:
            Dict containing verification status update confirmation
        """
        try:
            from plaid.model.sandbox_item_set_verification_status_request import SandboxItemSetVerificationStatusRequest
            from plaid.model.sandbox_item_set_verification_status_request_verification_status import SandboxItemSetVerificationStatusRequestVerificationStatus
            
            client = self.client._get_client(environment)
            
            status_enum = SandboxItemSetVerificationStatusRequestVerificationStatus(verification_status)
            
            request = SandboxItemSetVerificationStatusRequest(
                access_token=access_token,
                account_id=account_id,
                verification_status=status_enum
            )
            
            response = client.sandbox_item_set_verification_status(request)
            
            return {
                'verification_status_updated': True,
                'account_id': account_id,
                'verification_status': verification_status,
                'request_id': response['request_id'],
                'environment': environment
            }
            
        except Exception as e:
            logger.error(f"Error setting verification status in sandbox: {str(e)}")
            raise
    
    async def reset_login(
        self,
        access_token: str,
        environment: str = 'sandbox'
    ) -> Dict[str, Any]:
        """
        Reset login for an Item to trigger an ITEM_LOGIN_REQUIRED error.
        
        Args:
            access_token: Access token for the Item
            environment: Must be 'sandbox'
            
        Returns:
            Dict containing login reset confirmation
        """
        try:
            from plaid.model.sandbox_item_reset_login_request import SandboxItemResetLoginRequest
            
            client = self.client._get_client(environment)
            
            request = SandboxItemResetLoginRequest(access_token=access_token)
            response = client.sandbox_item_reset_login(request)
            
            return {
                'reset_login': True,
                'request_id': response['request_id'],
                'environment': environment,
                'message': 'Item will now return ITEM_LOGIN_REQUIRED error'
            }
            
        except Exception as e:
            logger.error(f"Error resetting login in sandbox: {str(e)}")
            raise
    
    async def refresh_transactions(
        self,
        access_token: str,
        environment: str = 'sandbox'
    ) -> Dict[str, Any]:
        """
        Refresh transactions for an Item in sandbox.
        
        Args:
            access_token: Access token for the Item
            environment: Must be 'sandbox'
            
        Returns:
            Dict containing transaction refresh confirmation
        """
        try:
            from plaid.model.transactions_refresh_request import TransactionsRefreshRequest
            
            client = self.client._get_client(environment)
            
            request = TransactionsRefreshRequest(access_token=access_token)
            response = client.transactions_refresh(request)
            
            return {
                'transactions_refreshed': True,
                'request_id': response['request_id'],
                'environment': environment,
                'message': 'Transactions refresh triggered'
            }
            
        except Exception as e:
            logger.error(f"Error refreshing transactions in sandbox: {str(e)}")
            raise
