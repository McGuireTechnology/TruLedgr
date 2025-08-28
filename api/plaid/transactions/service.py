"""
Plaid Transactions Service

Service methods for transaction retrieval, management, and database operations.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlmodel import Session, select, desc
from fastapi import HTTPException, status
import logging

from api.db.deps import get_db
from .models import PlaidTransaction, PlaidTransactionResponse
from ..accounts.models import PlaidAccount
from ..items.models import PlaidItem, PlaidEnvironment

from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest as PlaidTransactionsGetRequest

logger = logging.getLogger(__name__)

class TransactionsService:
    """Service class for transaction-related operations"""
    
    def __init__(self, plaid_service):
        self.plaid_service = plaid_service
    
    # Database Operations
    async def get_user_transactions(
        self, 
        user_id: int, 
        account_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
        environment: Optional[PlaidEnvironment] = None
    ) -> Tuple[List[PlaidTransactionResponse], int]:
        """Get transactions for a user with pagination"""
        
        with get_db() as session:
            # Base query
            query = select(PlaidTransaction, PlaidAccount, PlaidItem).where(
                PlaidTransaction.account_id == PlaidAccount.id,
                PlaidAccount.item_id == PlaidItem.id,
                PlaidTransaction.user_id == str(user_id)
            )
            
            # Apply filters
            if account_id:
                query = query.where(PlaidTransaction.account_id == str(account_id))
                
            if start_date:
                query = query.where(PlaidTransaction.transaction_date >= start_date.date())
                
            if end_date:
                query = query.where(PlaidTransaction.transaction_date <= end_date.date())
                
            if environment:
                query = query.where(PlaidItem.environment == environment.value)
            
            # Count total
            count_results = session.exec(query).all()
            total = len(count_results)
            
            # Apply pagination and ordering
            results = session.exec(
                query.order_by(desc(PlaidTransaction.transaction_date))
                .offset(offset)
                .limit(limit)
            ).all()
            
            responses = []
            for transaction, account, item in results:
                response = self._transaction_to_response(transaction, account.name, account.account_id)
                responses.append(response)
            
            logger.info(f"Retrieved {len(responses)} transactions for user {user_id}")
            return responses, total

    async def sync_item_transactions(
        self, 
        user_id: int, 
        item_id: str, 
        days: int = 30
    ) -> int:
        """Sync transactions for a specific item"""
        with get_db() as session:
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
            
            count = await self._sync_transactions(item, session, days)
            logger.info(f"Synced {count} transactions for item {item_id}")
            return count

    # Private helper methods
    async def _sync_transactions(self, item: PlaidItem, session: Session, days: int = 30) -> int:
        """Sync transactions for an item"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            transactions_data = await self.plaid_service.get_transactions(
                access_token=item.access_token,
                start_date=start_date,
                end_date=end_date
            )
            
            count = 0
            for transaction_data in transactions_data['transactions']:
                # Find the account in our database
                account = session.exec(
                    select(PlaidAccount).where(
                        PlaidAccount.account_id == transaction_data['account_id'],
                        PlaidAccount.item_id == item.id
                    )
                ).first()
                
                if not account:
                    continue
                
                # Check if transaction exists
                existing_transaction = session.exec(
                    select(PlaidTransaction).where(
                        PlaidTransaction.transaction_id == transaction_data['transaction_id']
                    )
                ).first()
                
                if not existing_transaction:
                    # Create new transaction
                    transaction_date = transaction_data['date']
                    if isinstance(transaction_date, str):
                        from datetime import datetime as dt
                        transaction_date = dt.fromisoformat(transaction_date).date()
                    
                    new_transaction = PlaidTransaction(
                        account_id=account.id or "",
                        user_id=item.user_id,
                        item_id=item.id or "",
                        transaction_id=transaction_data['transaction_id'],
                        amount=transaction_data['amount'],
                        transaction_date=transaction_date,
                        name=transaction_data['name'],
                        merchant_name=transaction_data.get('merchant_name'),
                        transaction_type=transaction_data.get('type'),
                        pending=transaction_data.get('pending', False),
                        account_owner=transaction_data.get('account_owner'),
                        iso_currency_code=transaction_data.get('iso_currency_code', 'USD'),
                        environment=item.environment if isinstance(item.environment, str) else item.environment.value if item.environment else 'production'
                    )
                    
                    # Set JSON fields using property setters
                    if 'location' in transaction_data:
                        new_transaction.location_dict = transaction_data['location']
                    if 'payment_meta' in transaction_data:
                        # Convert PaymentMeta object to dict if necessary
                        payment_meta_value = transaction_data['payment_meta']
                        if hasattr(payment_meta_value, 'to_dict'):
                            payment_meta_value = payment_meta_value.to_dict()
                        elif hasattr(payment_meta_value, '__dict__'):
                            payment_meta_value = payment_meta_value.__dict__
                        new_transaction.payment_meta_dict = payment_meta_value
                    if 'category' in transaction_data:
                        new_transaction.category_list = transaction_data['category']
                    
                    session.add(new_transaction)
                    count += 1
            
            if count > 0:
                session.commit()
                
            # Update item last sync
            item.last_sync = datetime.utcnow()
            session.add(item)
            session.commit()
            
            return count
            
        except Exception as e:
            logger.error(f"Error syncing transactions for item {item.item_id}: {str(e)}")
            raise

    def _transaction_to_response(self, transaction: PlaidTransaction, account_name: str, account_id: str) -> PlaidTransactionResponse:
        """Convert PlaidTransaction to response model"""
        return PlaidTransactionResponse(
            id=transaction.id or "",
            transaction_id=transaction.transaction_id,
            amount=transaction.amount,
            date=transaction.transaction_date.isoformat() if transaction.transaction_date else "",
            authorized_date=transaction.authorized_date.isoformat() if transaction.authorized_date else None,
            name=transaction.name,
            merchant_name=transaction.merchant_name,
            category=transaction.category_list,  # Use property to get list
            transaction_type=transaction.transaction_type,
            pending=transaction.pending,
            account_name=account_name,
            account_id=account_id,
            institution_name="",  # Will be populated from item/institution data
            iso_currency_code=transaction.iso_currency_code or "USD",
            location=transaction.location_dict,  # Use property to get dict
            payment_meta=transaction.payment_meta_dict,  # Use property to get dict
            created_at=transaction.created_at,
            updated_at=transaction.updated_at
        )

    # Plaid API Operations (existing methods)
    
    async def get_transactions(
        self, 
        access_token: str, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        account_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get transactions for connected accounts"""
        try:
            # Use the plaid service to get transactions
            return await self.plaid_service.get_transactions(
                access_token=access_token,
                start_date=start_date,
                end_date=end_date,
                account_ids=account_ids
            )
            
        except Exception as e:
            logger.error(f"Error fetching transactions: {str(e)}")
            raise
    
    async def refresh_transactions(self, access_token: str, environment: str = 'production') -> Dict[str, Any]:
        """Refresh transactions for an item"""
        try:
            from plaid.model.transactions_refresh_request import TransactionsRefreshRequest
            
            client = self.plaid_service._get_client(environment)
            request = TransactionsRefreshRequest(access_token=access_token)
            response = client.transactions_refresh(request)
            
            return {
                'request_id': response['request_id'],
                'message': 'Transaction refresh initiated successfully'
            }
            
        except Exception as e:
            logger.error(f"Error refreshing transactions: {str(e)}")
            raise
