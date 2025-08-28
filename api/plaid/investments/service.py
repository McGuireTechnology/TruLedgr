"""
Plaid Investments Service

Service methods for investment holdings and transactions.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from plaid.api import plaid_api

logger = logging.getLogger(__name__)

class InvestmentsService:
    """Service class for investment-related operations"""
    
    def __init__(self, plaid_client: plaid_api.PlaidApi):
        self.client = plaid_client
    
    async def get_investments_holdings(
        self,
        access_token: str,
        account_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get investment holdings for connected accounts.
        
        Args:
            access_token: Access token for the connected account
            account_ids: Optional list of specific account IDs to retrieve
            
        Returns:
            Dict containing holdings, securities, and account information
        """
        try:
            # Import the required model here to avoid import order issues
            from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest
            
            # Create request with minimal parameters - Plaid handles options internally
            request = InvestmentsHoldingsGetRequest(access_token=access_token)
            
            response = self.client.investments_holdings_get(request)
            
            # Convert response to dict format
            return {
                'accounts': [
                    {
                        'account_id': acc['account_id'],
                        'name': acc['name'],
                        'official_name': acc.get('official_name'),
                        'type': acc['type'],
                        'subtype': acc.get('subtype'),
                        'balances': {
                            'available': acc['balances'].get('available'),
                            'current': acc['balances'].get('current'),
                            'limit': acc['balances'].get('limit'),
                            'iso_currency_code': acc['balances'].get('iso_currency_code')
                        },
                        'mask': acc.get('mask')
                    }
                    for acc in response['accounts']
                ],
                'holdings': [
                    {
                        'account_id': holding['account_id'],
                        'security_id': holding['security_id'],
                        'institution_price': holding['institution_price'],
                        'institution_price_as_of': holding.get('institution_price_as_of'),
                        'institution_price_datetime': holding.get('institution_price_datetime'),
                        'institution_value': holding['institution_value'],
                        'cost_basis': holding.get('cost_basis'),
                        'quantity': holding['quantity'],
                        'iso_currency_code': holding.get('iso_currency_code'),
                        'unofficial_currency_code': holding.get('unofficial_currency_code'),
                        'vested_quantity': holding.get('vested_quantity'),
                        'vested_value': holding.get('vested_value')
                    }
                    for holding in response['holdings']
                ],
                'securities': [
                    {
                        'security_id': security['security_id'],
                        'isin': security.get('isin'),
                        'cusip': security.get('cusip'),
                        'sedol': security.get('sedol'),
                        'institution_security_id': security.get('institution_security_id'),
                        'institution_id': security.get('institution_id'),
                        'proxy_security_id': security.get('proxy_security_id'),
                        'name': security.get('name'),
                        'ticker_symbol': security.get('ticker_symbol'),
                        'is_cash_equivalent': security.get('is_cash_equivalent'),
                        'type': security.get('type'),
                        'close_price': security.get('close_price'),
                        'close_price_as_of': security.get('close_price_as_of'),
                        'update_datetime': security.get('update_datetime'),
                        'iso_currency_code': security.get('iso_currency_code'),
                        'unofficial_currency_code': security.get('unofficial_currency_code'),
                        'market_identifier_code': security.get('market_identifier_code'),
                        'sector': security.get('sector'),
                        'industry': security.get('industry'),
                        'option_contract': security.get('option_contract'),
                        'fixed_income': security.get('fixed_income')
                    }
                    for security in response['securities']
                ],
                'request_id': response['request_id'],
                'is_investments_fallback_item': response.get('is_investments_fallback_item', False)
            }
            
        except Exception as e:
            logger.error(f"Error fetching investment holdings: {str(e)}")
            raise
    
    async def get_investments_transactions(
        self,
        access_token: str,
        start_date: datetime,
        end_date: datetime,
        account_ids: Optional[List[str]] = None,
        count: int = 100,
        offset: int = 0,
        async_update: bool = False
    ) -> Dict[str, Any]:
        """
        Get investment transactions for connected accounts.
        
        Args:
            access_token: Access token for the connected account
            start_date: Start date for transaction query
            end_date: End date for transaction query  
            account_ids: Optional list of specific account IDs to retrieve
            count: Number of transactions to fetch (1-500)
            offset: Number of transactions to skip for pagination
            async_update: Whether to use asynchronous extraction for initial data
            
        Returns:
            Dict containing investment transactions, securities, and account information
        """
        try:
            # Import the required models here to avoid import order issues
            from plaid.model.investments_transactions_get_request import InvestmentsTransactionsGetRequest
            
            # Convert dates to proper format for Plaid
            start_date_str = start_date.date().strftime('%Y-%m-%d') if hasattr(start_date, 'date') else start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.date().strftime('%Y-%m-%d') if hasattr(end_date, 'date') else end_date.strftime('%Y-%m-%d')
            
            request = InvestmentsTransactionsGetRequest(
                access_token=access_token,
                start_date=start_date_str,
                end_date=end_date_str
            )
            
            response = self.client.investments_transactions_get(request)
            
            # Convert response to dict format
            return {
                'accounts': [
                    {
                        'account_id': acc['account_id'],
                        'name': acc['name'],
                        'official_name': acc.get('official_name'),
                        'type': acc['type'],
                        'subtype': acc.get('subtype'),
                        'balances': {
                            'available': acc['balances'].get('available'),
                            'current': acc['balances'].get('current'),
                            'limit': acc['balances'].get('limit'),
                            'iso_currency_code': acc['balances'].get('iso_currency_code')
                        },
                        'mask': acc.get('mask')
                    }
                    for acc in response['accounts']
                ],
                'investment_transactions': [
                    {
                        'investment_transaction_id': txn['investment_transaction_id'],
                        'account_id': txn['account_id'],
                        'security_id': txn.get('security_id'),
                        'date': str(txn['date']),
                        'name': txn['name'],
                        'quantity': txn['quantity'],
                        'amount': txn['amount'],
                        'price': txn['price'],
                        'fees': txn.get('fees'),
                        'type': txn['type'],
                        'subtype': txn['subtype'],
                        'iso_currency_code': txn.get('iso_currency_code'),
                        'unofficial_currency_code': txn.get('unofficial_currency_code')
                    }
                    for txn in response['investment_transactions']
                ],
                'securities': [
                    {
                        'security_id': security['security_id'],
                        'isin': security.get('isin'),
                        'cusip': security.get('cusip'),
                        'sedol': security.get('sedol'),
                        'institution_security_id': security.get('institution_security_id'),
                        'institution_id': security.get('institution_id'),
                        'proxy_security_id': security.get('proxy_security_id'),
                        'name': security.get('name'),
                        'ticker_symbol': security.get('ticker_symbol'),
                        'is_cash_equivalent': security.get('is_cash_equivalent'),
                        'type': security.get('type'),
                        'close_price': security.get('close_price'),
                        'close_price_as_of': security.get('close_price_as_of'),
                        'update_datetime': security.get('update_datetime'),
                        'iso_currency_code': security.get('iso_currency_code'),
                        'unofficial_currency_code': security.get('unofficial_currency_code'),
                        'market_identifier_code': security.get('market_identifier_code'),
                        'sector': security.get('sector'),
                        'industry': security.get('industry'),
                        'option_contract': security.get('option_contract'),
                        'fixed_income': security.get('fixed_income')
                    }
                    for security in response['securities']
                ],
                'total_investment_transactions': response['total_investment_transactions'],
                'request_id': response['request_id'],
                'is_investments_fallback_item': response.get('is_investments_fallback_item', False)
            }
            
        except Exception as e:
            logger.error(f"Error fetching investment transactions: {str(e)}")
            raise
    
    async def refresh_investments(
        self,
        access_token: str
    ) -> Dict[str, Any]:
        """
        Refresh investment data for an item.
        
        This endpoint triggers an on-demand extraction to fetch the newest investment
        holdings and transactions. Updated data can then be retrieved with the
        get_investments_holdings and get_investments_transactions methods.
        
        Args:
            access_token: Access token for the connected account
            
        Returns:
            Dict containing request_id
        """
        try:
            # Import the required model here to avoid import order issues
            from plaid.model.investments_refresh_request import InvestmentsRefreshRequest
            
            request = InvestmentsRefreshRequest(access_token=access_token)
            response = self.client.investments_refresh(request)
            
            return {
                'request_id': response['request_id'],
                'message': 'Investment data refresh initiated'
            }
            
        except Exception as e:
            logger.error(f"Error refreshing investments: {str(e)}")
            raise
