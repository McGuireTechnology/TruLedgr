"""
Plaid Enrich Service

Service methods for transaction enrichment.
"""

from typing import List, Dict, Any, Optional
import logging

from plaid.api import plaid_api

logger = logging.getLogger(__name__)

class EnrichService:
    """Service class for transaction enrichment operations"""
    
    def __init__(self, plaid_client: plaid_api.PlaidApi):
        self.client = plaid_client
    
    async def enrich_transactions(
        self,
        account_type: str,
        transactions: List[Dict[str, Any]],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Enrich locally-held transaction data using Plaid's enrichment service.
        
        This endpoint enriches raw transaction data that you have generated
        or retrieved from non-Plaid sources with merchant information,
        categorization, location data, and other insights.
        
        Args:
            account_type: Account type ('depository' or 'credit')
            transactions: List of transactions to enrich (max 100)
            options: Optional enrichment settings
            
        Returns:
            Dict containing enriched transactions
        """
        try:
            # Import the required model here to avoid import order issues
            from plaid.model.transactions_enrich_request import TransactionsEnrichRequest
            from plaid.model.transactions_enrich_request_options import TransactionsEnrichRequestOptions
            
            # Validate transaction limit
            if len(transactions) > 100:
                raise ValueError("Maximum of 100 transactions can be enriched per request")
            
            # Build request
            request_data = {
                'account_type': account_type,
                'transactions': transactions
            }
            
            if options:
                enrich_options = TransactionsEnrichRequestOptions(**options)
                request_data['options'] = enrich_options
            
            request = TransactionsEnrichRequest(**request_data)
            response = self.client.transactions_enrich(request)
            
            # Convert response to dictionary format for consistent API
            result = response.to_dict()
            
            return {
                'enriched_transactions': [
                    {
                        'id': txn['id'],
                        'description': txn['description'],
                        'amount': txn['amount'],
                        'direction': txn['direction'],
                        'iso_currency_code': txn['iso_currency_code'],
                        'enrichments': {
                            'counterparties': [
                                {
                                    'name': cp['name'],
                                    'entity_id': cp.get('entity_id'),
                                    'type': cp['type'],
                                    'website': cp.get('website'),
                                    'logo_url': cp.get('logo_url'),
                                    'confidence_level': cp.get('confidence_level'),
                                    'phone_number': cp.get('phone_number'),
                                    'account_numbers': cp.get('account_numbers')
                                }
                                for cp in txn['enrichments'].get('counterparties', [])
                            ],
                            'entity_id': txn['enrichments'].get('entity_id'),
                            'legacy_category_id': txn['enrichments'].get('legacy_category_id'),
                            'legacy_category': txn['enrichments'].get('legacy_category'),
                            'location': {
                                'address': txn['enrichments'].get('location', {}).get('address'),
                                'city': txn['enrichments'].get('location', {}).get('city'),
                                'region': txn['enrichments'].get('location', {}).get('region'),
                                'postal_code': txn['enrichments'].get('location', {}).get('postal_code'),
                                'country': txn['enrichments'].get('location', {}).get('country'),
                                'lat': txn['enrichments'].get('location', {}).get('lat'),
                                'lon': txn['enrichments'].get('location', {}).get('lon'),
                                'store_number': txn['enrichments'].get('location', {}).get('store_number')
                            } if txn['enrichments'].get('location') else None,
                            'logo_url': txn['enrichments'].get('logo_url'),
                            'merchant_name': txn['enrichments'].get('merchant_name'),
                            'payment_channel': txn['enrichments'].get('payment_channel'),
                            'phone_number': txn['enrichments'].get('phone_number'),
                            'personal_finance_category': {
                                'primary': txn['enrichments'].get('personal_finance_category', {}).get('primary'),
                                'detailed': txn['enrichments'].get('personal_finance_category', {}).get('detailed'),
                                'confidence_level': txn['enrichments'].get('personal_finance_category', {}).get('confidence_level')
                            } if txn['enrichments'].get('personal_finance_category') else None,
                            'personal_finance_category_icon_url': txn['enrichments'].get('personal_finance_category_icon_url'),
                            'recurrence': {
                                'is_recurring': txn['enrichments'].get('recurrence', {}).get('is_recurring')
                            } if txn['enrichments'].get('recurrence') else None,
                            'website': txn['enrichments'].get('website')
                        }
                    }
                    for txn in result['enriched_transactions']
                ],
                'request_id': result['request_id']
            }
            
        except Exception as e:
            logger.error(f"Error enriching transactions: {str(e)}")
            raise
