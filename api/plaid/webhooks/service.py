"""
Plaid Webhooks Service

Service methods for webhook verification and processing.
"""

from typing import List, Dict, Any, Optional
import json
import hmac
import hashlib
import os
import logging

logger = logging.getLogger(__name__)

class WebhooksService:
    """Service class for webhook-related operations"""
    
    def __init__(self):
        pass
    
    def verify_webhook(self, request_body: bytes, plaid_signature: str, webhook_secret: Optional[str] = None) -> bool:
        """
        Verify that a webhook request is from Plaid by validating the signature.
        
        Args:
            request_body: Raw request body as bytes
            plaid_signature: The Plaid-Signature header value
            webhook_secret: Optional webhook secret (uses env var if not provided)
        
        Returns:
            bool: True if signature is valid, False otherwise
        """
        if not webhook_secret:
            webhook_secret = os.getenv('PLAID_WEBHOOK_SECRET')
        
        if not webhook_secret:
            logger.warning("PLAID_WEBHOOK_SECRET not configured - webhook verification disabled")
            return True  # Allow webhooks through in development if secret not set
        
        try:
            # Calculate expected signature
            expected_signature = hmac.new(
                webhook_secret.encode('utf-8'),
                request_body,
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(plaid_signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {str(e)}")
            return False
    
    def parse_webhook_payload(self, request_body: bytes) -> Dict[str, Any]:
        """
        Parse webhook payload from Plaid.
        
        Args:
            request_body: Raw request body as bytes
            
        Returns:
            Dict containing parsed webhook data
        """
        try:
            payload = json.loads(request_body.decode('utf-8'))
            return payload
        except Exception as e:
            logger.error(f"Error parsing webhook payload: {str(e)}")
            raise ValueError(f"Invalid webhook payload: {str(e)}")
    
    async def handle_webhook_event(self, webhook_type: str, webhook_code: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process different types of webhook events from Plaid.
        
        Args:
            webhook_type: Type of webhook (TRANSACTIONS, ITEM, etc.)
            webhook_code: Specific webhook code
            payload: Full webhook payload
            
        Returns:
            Dict with processing results
        """
        try:
            logger.info(f"Processing webhook: {webhook_type}.{webhook_code}")
            
            if webhook_type == "TRANSACTIONS":
                return await self._handle_transactions_webhook(webhook_code, payload)
            elif webhook_type == "ITEM":
                return await self._handle_item_webhook(webhook_code, payload)
            elif webhook_type == "AUTH":
                return await self._handle_auth_webhook(webhook_code, payload)
            elif webhook_type == "ASSETS":
                return await self._handle_assets_webhook(webhook_code, payload)
            elif webhook_type == "HOLDINGS":
                return await self._handle_holdings_webhook(webhook_code, payload)
            elif webhook_type == "INVESTMENTS_TRANSACTIONS":
                return await self._handle_investments_transactions_webhook(webhook_code, payload)
            elif webhook_type == "LIABILITIES":
                return await self._handle_liabilities_webhook(webhook_code, payload)
            else:
                logger.warning(f"Unhandled webhook type: {webhook_type}")
                return {"status": "unhandled", "webhook_type": webhook_type}
                
        except Exception as e:
            logger.error(f"Error handling webhook {webhook_type}.{webhook_code}: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _handle_transactions_webhook(self, webhook_code: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle TRANSACTIONS webhook events"""
        item_id = payload.get('item_id')
        
        if webhook_code == "INITIAL_UPDATE":
            # Historical transactions are ready to be fetched
            logger.info(f"Initial transactions available for item {item_id}")
            return {
                "status": "processed",
                "action": "initial_transactions_ready",
                "item_id": item_id,
                "message": "Historical transactions are now available for fetching"
            }
            
        elif webhook_code == "HISTORICAL_UPDATE":
            # Historical transactions update completed
            logger.info(f"Historical transactions updated for item {item_id}")
            return {
                "status": "processed",
                "action": "historical_transactions_updated",
                "item_id": item_id,
                "message": "Historical transactions have been updated"
            }
            
        elif webhook_code == "DEFAULT_UPDATE":
            # New transactions are available
            new_transactions = payload.get('new_transactions', 0)
            removed_transactions = payload.get('removed_transactions', [])
            
            logger.info(f"Transaction update for item {item_id}: {new_transactions} new, {len(removed_transactions)} removed")
            
            # TODO: Implement actual transaction sync logic here
            # This would typically:
            # 1. Fetch new transactions using the access token
            # 2. Update your database
            # 3. Notify your application about the changes
            
            return {
                "status": "processed", 
                "action": "transactions_updated",
                "item_id": item_id,
                "new_transactions": new_transactions,
                "removed_transactions": removed_transactions,
                "message": f"Processed {new_transactions} new transactions"
            }
            
        else:
            logger.warning(f"Unhandled TRANSACTIONS webhook code: {webhook_code}")
            return {"status": "unhandled", "webhook_code": webhook_code}
    
    async def _handle_item_webhook(self, webhook_code: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ITEM webhook events"""
        item_id = payload.get('item_id')
        
        if webhook_code == "ERROR":
            error = payload.get('error', {})
            logger.error(f"Item error for {item_id}: {error}")
            
            # TODO: Handle item errors (e.g., expired tokens, connection issues)
            # This might involve:
            # 1. Notifying the user
            # 2. Requesting re-authentication
            # 3. Updating item status in database
            
            return {
                "status": "processed",
                "action": "item_error",
                "item_id": item_id,
                "error": error,
                "message": "Item encountered an error - user may need to reconnect"
            }
            
        elif webhook_code == "PENDING_EXPIRATION":
            consent_expiration_time = payload.get('consent_expiration_time')
            logger.warning(f"Item {item_id} consent expiring at {consent_expiration_time}")
            
            return {
                "status": "processed",
                "action": "pending_expiration",
                "item_id": item_id,
                "consent_expiration_time": consent_expiration_time,
                "message": "Item consent is pending expiration"
            }
            
        elif webhook_code == "USER_PERMISSION_REVOKED":
            logger.info(f"User revoked permissions for item {item_id}")
            
            return {
                "status": "processed",
                "action": "permission_revoked",
                "item_id": item_id,
                "message": "User has revoked permissions for this item"
            }
            
        elif webhook_code == "WEBHOOK_UPDATE_ACKNOWLEDGED":
            new_webhook_url = payload.get('new_webhook_url')
            logger.info(f"Webhook URL updated for item {item_id}: {new_webhook_url}")
            
            return {
                "status": "processed",
                "action": "webhook_updated",
                "item_id": item_id,
                "new_webhook_url": new_webhook_url
            }
            
        else:
            logger.warning(f"Unhandled ITEM webhook code: {webhook_code}")
            return {"status": "unhandled", "webhook_code": webhook_code}
    
    async def _handle_auth_webhook(self, webhook_code: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle AUTH (Account) webhook events"""
        item_id = payload.get('item_id')
        
        if webhook_code == "AUTOMATICALLY_VERIFIED":
            account_id = payload.get('account_id')
            logger.info(f"Account {account_id} automatically verified for item {item_id}")
            
            return {
                "status": "processed",
                "action": "account_verified",
                "item_id": item_id,
                "account_id": account_id
            }
            
        elif webhook_code == "VERIFICATION_EXPIRED":
            account_id = payload.get('account_id')
            logger.warning(f"Account verification expired for {account_id} in item {item_id}")
            
            return {
                "status": "processed", 
                "action": "verification_expired",
                "item_id": item_id,
                "account_id": account_id
            }
            
        else:
            logger.warning(f"Unhandled AUTH webhook code: {webhook_code}")
            return {"status": "unhandled", "webhook_code": webhook_code}
    
    async def _handle_assets_webhook(self, webhook_code: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ASSETS webhook events"""
        # Assets webhooks are for Plaid's Assets product
        logger.info(f"Assets webhook received: {webhook_code}")
        return {"status": "processed", "action": "assets_event", "webhook_code": webhook_code}
    
    async def _handle_holdings_webhook(self, webhook_code: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle HOLDINGS webhook events"""
        item_id = payload.get('item_id')
        new_holdings = payload.get('new_holdings', 0)
        updated_holdings = payload.get('updated_holdings', 0)
        
        if webhook_code == "DEFAULT_UPDATE":
            logger.info(f"Holdings updated for item {item_id}: {new_holdings} new, {updated_holdings} updated")
            
            # TODO: In production, you might want to:
            # 1. Fetch updated holdings using get_investments_holdings()
            # 2. Update your database
            # 3. Notify users of portfolio changes
            # 4. Trigger any portfolio analysis or rebalancing logic
            
            return {
                "status": "processed",
                "action": "holdings_updated",
                "item_id": item_id,
                "new_holdings": new_holdings,
                "updated_holdings": updated_holdings,
                "message": f"Holdings updated: {new_holdings} new, {updated_holdings} updated"
            }
        else:
            logger.warning(f"Unhandled HOLDINGS webhook code: {webhook_code}")
            return {"status": "unhandled", "webhook_code": webhook_code}
    
    async def _handle_investments_transactions_webhook(self, webhook_code: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle INVESTMENTS_TRANSACTIONS webhook events"""
        item_id = payload.get('item_id')
        new_transactions = payload.get('new_investments_transactions', 0)
        canceled_transactions = payload.get('canceled_investments_transactions', 0)
        
        if webhook_code == "DEFAULT_UPDATE":
            logger.info(f"Investment transactions updated for item {item_id}: {new_transactions} new, {canceled_transactions} canceled")
            
            # TODO: In production, you might want to:
            # 1. Fetch new transactions using get_investments_transactions()
            # 2. Update your database with new investment transactions
            # 3. Update portfolio performance calculations
            # 4. Notify users of new investment activity
            
            return {
                "status": "processed",
                "action": "investment_transactions_updated",
                "item_id": item_id,
                "new_transactions": new_transactions,
                "canceled_transactions": canceled_transactions,
                "message": f"Investment transactions updated: {new_transactions} new, {canceled_transactions} canceled"
            }
            
        elif webhook_code == "HISTORICAL_UPDATE":
            logger.info(f"Historical investment data ready for item {item_id}: {new_transactions} transactions available")
            
            # This webhook fires after asynchronous investments extraction completes
            # when async_update was set to true in the original request
            
            return {
                "status": "processed",
                "action": "historical_investment_data_ready",
                "item_id": item_id,
                "new_transactions": new_transactions,
                "canceled_transactions": canceled_transactions,
                "message": "Historical investment data extraction completed and ready for retrieval"
            }
            
        else:
            logger.warning(f"Unhandled INVESTMENTS_TRANSACTIONS webhook code: {webhook_code}")
            return {"status": "unhandled", "webhook_code": webhook_code}

    async def _handle_liabilities_webhook(self, webhook_code: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle LIABILITIES webhook events"""
        item_id = payload.get('item_id')
        
        if webhook_code == "DEFAULT_UPDATE":
            account_ids_with_new_liabilities = payload.get('account_ids_with_new_liabilities', [])
            account_ids_with_updated_liabilities = payload.get('account_ids_with_updated_liabilities', {})
            
            total_new_accounts = len(account_ids_with_new_liabilities)
            total_updated_accounts = len(account_ids_with_updated_liabilities)
            
            logger.info(f"Liabilities updated for item {item_id}: {total_new_accounts} accounts with new liabilities, {total_updated_accounts} accounts with updated liabilities")
            
            # TODO: In production, you might want to:
            # 1. Fetch updated liabilities data using get_liabilities()
            # 2. Update your database with new liability information  
            # 3. Recalculate debt-to-income ratios or other financial metrics
            # 4. Notify users of changes in their loan/credit status
            # 5. Update payment reminders based on new due dates
            
            return {
                "status": "processed",
                "action": "liabilities_updated", 
                "item_id": item_id,
                "accounts_with_new_liabilities": account_ids_with_new_liabilities,
                "accounts_with_updated_liabilities": account_ids_with_updated_liabilities,
                "message": f"Liabilities updated: {total_new_accounts} accounts with new liabilities, {total_updated_accounts} accounts with updates",
                "details": {
                    "new_liability_accounts": account_ids_with_new_liabilities,
                    "updated_liability_accounts": account_ids_with_updated_liabilities
                }
            }
            
        else:
            logger.warning(f"Unhandled LIABILITIES webhook code: {webhook_code}")
            return {"status": "unhandled", "webhook_code": webhook_code}
    
    def get_webhook_types(self) -> List[str]:
        """Get list of supported webhook types"""
        return ["TRANSACTIONS", "ITEM", "AUTH", "ASSETS", "HOLDINGS", "INVESTMENTS_TRANSACTIONS", "LIABILITIES"]
    
    def get_webhook_codes_for_type(self, webhook_type: str) -> List[str]:
        """Get supported webhook codes for a given type"""
        webhook_codes = {
            "TRANSACTIONS": ["INITIAL_UPDATE", "HISTORICAL_UPDATE", "DEFAULT_UPDATE"],
            "ITEM": ["ERROR", "PENDING_EXPIRATION", "USER_PERMISSION_REVOKED", "WEBHOOK_UPDATE_ACKNOWLEDGED"],
            "AUTH": ["AUTOMATICALLY_VERIFIED", "VERIFICATION_EXPIRED"],
            "ASSETS": ["PRODUCT_READY", "ERROR"],
            "HOLDINGS": ["DEFAULT_UPDATE"],
            "INVESTMENTS_TRANSACTIONS": ["DEFAULT_UPDATE", "HISTORICAL_UPDATE"],
            "LIABILITIES": ["DEFAULT_UPDATE"]
        }
        return webhook_codes.get(webhook_type, [])
