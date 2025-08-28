"""
Plaid Accounts Service

Service layer for handling Account information, balance operations, and database operations.
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from sqlmodel import Session, select, desc
from fastapi import HTTPException, status
import logging
import json

from api.db.deps import get_db
from .models import (
    PlaidAccount, PlaidAccountResponse, AccountType, AccountSubtype,
    PlaidAccountBalanceHistory, PlaidAccountStatusHistory, PlaidAccountWebhookEvent
)
from ..items.models import PlaidItem, PlaidEnvironment

logger = logging.getLogger(__name__)

class AccountsService:
    """Service for handling Plaid Account operations"""
    
    def __init__(self, plaid_client):
        self.client = plaid_client
    
    # Database Operations
    async def get_user_accounts(self, user_id: int, environment: Optional[PlaidEnvironment] = None) -> List[PlaidAccountResponse]:
        """Get all accounts for a user"""
        with get_db() as session:
            query = select(PlaidAccount, PlaidItem).where(
                PlaidAccount.item_id == PlaidItem.id,
                PlaidAccount.user_id == str(user_id),
                PlaidAccount.is_active == True
            )
            
            if environment:
                query = query.where(PlaidItem.environment == environment.value)
            
            results = session.exec(query.order_by(desc(PlaidAccount.created_at))).all()
            
            responses = []
            for account, item in results:
                response = self._account_to_response(account, item.institution_name)
                responses.append(response)
            
            logger.info(f"Retrieved {len(responses)} accounts for user {user_id}")
            return responses

    async def sync_item_accounts(self, item_id: str, session: Session) -> None:
        """Sync accounts for an item"""
        try:
            # Get the item
            item = session.exec(
                select(PlaidItem).where(PlaidItem.id == item_id)
            ).first()
            
            if not item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Item not found"
                )
            
            # Get accounts from Plaid API
            accounts_data = await self.get_accounts(item.access_token, environment=item.environment)
            
            for account_data in accounts_data['accounts']:
                # Check if account exists
                existing_account = session.exec(
                    select(PlaidAccount).where(PlaidAccount.account_id == account_data['account_id'])
                ).first()
                
                if existing_account:
                    # Update existing account
                    self._update_account_from_api_data(existing_account, account_data)
                    existing_account.last_sync = datetime.utcnow()
                    existing_account.updated_at = datetime.utcnow()
                    session.add(existing_account)
                else:
                    # Create new account
                    new_account = self._create_account_from_api_data(item, account_data)
                    session.add(new_account)
            
            session.commit()
            
        except Exception as e:
            logger.error(f"Error syncing accounts for item {item_id}: {str(e)}")
            raise

    async def sync_user_item_accounts(self, user_id: int, item_id: str) -> List[PlaidAccountResponse]:
        """Sync accounts for a specific item and return updated accounts"""
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
            
            await self.sync_item_accounts(item_id, session)
            
            # Get updated accounts
            accounts = session.exec(
                select(PlaidAccount).where(
                    PlaidAccount.item_id == item_id,
                    PlaidAccount.is_active == True
                )
            ).all()
            
            responses = [self._account_to_response(acc, item.institution_name) for acc in accounts]
            logger.info(f"Synced {len(responses)} accounts for item {item_id}")
            return responses

    # Private helper methods
    def _create_account_from_api_data(self, item: PlaidItem, account_data: Dict[str, Any]) -> PlaidAccount:
        """Create new account from Plaid API data with enhanced fields"""
        balances = account_data['balances']
        
        # Parse balance last updated datetime if available
        balance_updated = None
        if balances.get('last_updated_datetime'):
            try:
                balance_updated = datetime.fromisoformat(balances['last_updated_datetime'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass
        
        # Prepare additional metadata for JSON storage
        metadata = {}
        for key in ['verification_status', 'class_type', 'persistent_account_id']:
            if key in account_data and account_data[key] is not None:
                metadata[key] = account_data[key]
        
        return PlaidAccount(
            item_id=item.id or "",
            user_id=item.user_id,
            account_id=account_data['account_id'],
            persistent_account_id=account_data.get('persistent_account_id'),
            name=account_data['name'],
            official_name=account_data.get('official_name'),
            type=account_data['type'],
            subtype=account_data.get('subtype'),
            mask=account_data.get('mask'),
            holder_category=account_data.get('holder_category', 'personal'),
            available_balance=float(balances.get('available')) if balances.get('available') is not None else None,
            current_balance=float(balances.get('current')) if balances.get('current') is not None else None,
            limit_balance=float(balances.get('limit')) if balances.get('limit') is not None else None,
            iso_currency_code=balances.get('iso_currency_code', 'USD'),
            unofficial_currency_code=balances.get('unofficial_currency_code'),
            balance_last_updated_datetime=balance_updated,
            verification_status=account_data.get('verification_status'),
            is_active=True,
            is_closed=False,
            plaid_metadata=json.dumps(metadata) if metadata else None,
            last_sync=datetime.utcnow()
        )

    def _update_account_from_api_data(self, account: PlaidAccount, account_data: Dict[str, Any]) -> None:
        """Update existing account with Plaid API data including enhanced fields"""
        balances = account_data['balances']
        
        # Store previous balances for change tracking
        prev_available = account.available_balance
        prev_current = account.current_balance
        
        # Update basic account information
        account.name = account_data['name']
        account.official_name = account_data.get('official_name')
        account.type = account_data['type']
        account.subtype = account_data.get('subtype')
        account.mask = account_data.get('mask')
        account.holder_category = account_data.get('holder_category', 'personal')
        
        # Update balance information
        account.available_balance = float(balances.get('available')) if balances.get('available') is not None else None
        account.current_balance = float(balances.get('current')) if balances.get('current') is not None else None
        account.limit_balance = float(balances.get('limit')) if balances.get('limit') is not None else None
        account.iso_currency_code = balances.get('iso_currency_code', 'USD')
        account.unofficial_currency_code = balances.get('unofficial_currency_code')
        
        # Update balance timestamp if available
        if balances.get('last_updated_datetime'):
            try:
                account.balance_last_updated_datetime = datetime.fromisoformat(
                    balances['last_updated_datetime'].replace('Z', '+00:00')
                )
            except (ValueError, AttributeError):
                pass
        
        # Update verification and persistent ID
        account.verification_status = account_data.get('verification_status')
        if account_data.get('persistent_account_id'):
            account.persistent_account_id = account_data.get('persistent_account_id')
        
        # Update metadata
        metadata = account.plaid_metadata_dict if hasattr(account, 'plaid_metadata_dict') else {}
        for key in ['verification_status', 'class_type', 'persistent_account_id']:
            if key in account_data and account_data[key] is not None:
                metadata[key] = account_data[key]
        
        account.plaid_metadata = json.dumps(metadata) if metadata else None

    def _account_to_response(self, account: PlaidAccount, institution_name: str) -> PlaidAccountResponse:
        """Convert PlaidAccount to response model with enhanced data"""
        return PlaidAccountResponse(
            id=account.id or "",
            account_id=account.account_id,
            persistent_account_id=account.persistent_account_id,
            name=account.name,
            official_name=account.official_name,
            type=AccountType(account.type) if account.type else AccountType.OTHER,
            subtype=AccountSubtype(account.subtype) if account.subtype else None,
            mask=account.mask,
            holder_category=account.holder_category,
            available_balance=account.available_balance,
            current_balance=account.current_balance,
            limit_balance=account.limit_balance,
            iso_currency_code=account.iso_currency_code,
            unofficial_currency_code=account.unofficial_currency_code,
            balance_last_updated_datetime=account.balance_last_updated_datetime,
            verification_status=account.verification_status,
            is_active=account.is_active,
            is_closed=account.is_closed,
            invert_balance=account.invert_balance,
            invert_transactions=account.invert_transactions,
            institution_name=institution_name,
            created_at=account.created_at,
            updated_at=account.updated_at,
            last_sync=account.last_sync,
            plaid_metadata=account.plaid_metadata_dict if hasattr(account, 'plaid_metadata_dict') else None
        )

    # Enhanced Database Operations
    async def track_balance_history(
        self, 
        account_id: str, 
        balance_data: Dict[str, Any], 
        source: str = "api_sync",
        session: Session = None
    ) -> None:
        """Track balance changes in history table"""
        close_session = session is None
        if session is None:
            session = get_db()
        
        try:
            # Get current account for comparison
            current_account = session.exec(
                select(PlaidAccount).where(PlaidAccount.id == account_id)
            ).first()
            
            if not current_account:
                logger.warning(f"Account {account_id} not found for balance tracking")
                return
            
            # Calculate changes
            available_change = None
            current_change = None
            
            if balance_data.get('available') is not None and current_account.available_balance is not None:
                available_change = float(balance_data['available']) - current_account.available_balance
            
            if balance_data.get('current') is not None and current_account.current_balance is not None:
                current_change = float(balance_data['current']) - current_account.current_balance
            
            # Parse balance updated datetime
            balance_updated = None
            if balance_data.get('last_updated_datetime'):
                try:
                    balance_updated = datetime.fromisoformat(
                        balance_data['last_updated_datetime'].replace('Z', '+00:00')
                    )
                except (ValueError, AttributeError):
                    pass
            
            # Get environment from associated item
            item = session.exec(
                select(PlaidItem).where(PlaidItem.id == current_account.item_id)
            ).first()
            environment = item.environment if item else "production"
            
            # Create balance history record
            from api.common.utils import generate_id
            
            balance_history = PlaidAccountBalanceHistory(
                id=generate_id(),
                account_id=account_id,
                available_balance=float(balance_data.get('available')) if balance_data.get('available') is not None else None,
                current_balance=float(balance_data.get('current')) if balance_data.get('current') is not None else None,
                limit_balance=float(balance_data.get('limit')) if balance_data.get('limit') is not None else None,
                iso_currency_code=balance_data.get('iso_currency_code', 'USD'),
                unofficial_currency_code=balance_data.get('unofficial_currency_code'),
                source=source,
                balance_updated_datetime=balance_updated,
                available_change=available_change,
                current_change=current_change,
                environment=environment
            )
            
            session.add(balance_history)
            session.commit()
            
            logger.info(f"Balance history tracked for account {account_id}")
            
        except Exception as e:
            logger.error(f"Error tracking balance history for account {account_id}: {str(e)}")
            session.rollback()
            raise
        finally:
            if close_session:
                session.close()

    async def track_status_change(
        self,
        account_id: str,
        new_status: Dict[str, Any],
        change_reason: str = "api_sync",
        session: Session = None
    ) -> None:
        """Track account status and verification changes"""
        close_session = session is None
        if session is None:
            session = get_db()
        
        try:
            # Get current account for comparison
            current_account = session.exec(
                select(PlaidAccount).where(PlaidAccount.id == account_id)
            ).first()
            
            if not current_account:
                logger.warning(f"Account {account_id} not found for status tracking")
                return
            
            # Check if status actually changed
            status_changed = (
                current_account.is_active != new_status.get('is_active', current_account.is_active) or
                current_account.is_closed != new_status.get('is_closed', current_account.is_closed) or
                current_account.verification_status != new_status.get('verification_status', current_account.verification_status)
            )
            
            if not status_changed:
                return
            
            # Get environment from associated item
            item = session.exec(
                select(PlaidItem).where(PlaidItem.id == current_account.item_id)
            ).first()
            environment = item.environment if item else "production"
            
            # Create status history record
            from api.common.utils import generate_id
            
            status_history = PlaidAccountStatusHistory(
                id=generate_id(),
                account_id=account_id,
                is_active=new_status.get('is_active', current_account.is_active),
                is_closed=new_status.get('is_closed', current_account.is_closed),
                previous_active=current_account.is_active,
                previous_closed=current_account.is_closed,
                verification_status=new_status.get('verification_status'),
                previous_verification_status=current_account.verification_status,
                change_reason=change_reason,
                environment=environment
            )
            
            session.add(status_history)
            session.commit()
            
            logger.info(f"Status change tracked for account {account_id}: {change_reason}")
            
        except Exception as e:
            logger.error(f"Error tracking status change for account {account_id}: {str(e)}")
            session.rollback()
            raise
        finally:
            if close_session:
                session.close()

    async def handle_webhook_event(
        self,
        account_id: str,
        item_id: str,
        webhook_data: Dict[str, Any],
        session: Session = None
    ) -> None:
        """Handle and store webhook events for accounts"""
        close_session = session is None
        if session is None:
            session = get_db()
        
        try:
            # Get environment from associated item
            item = session.exec(
                select(PlaidItem).where(PlaidItem.id == item_id)
            ).first()
            environment = item.environment if item else "production"
            
            # Create webhook event record
            from api.common.utils import generate_id
            
            webhook_event = PlaidAccountWebhookEvent(
                id=generate_id(),
                account_id=account_id,
                item_id=item_id,
                webhook_type=webhook_data.get('webhook_type', 'UNKNOWN'),
                webhook_code=webhook_data.get('webhook_code', 'UNKNOWN'),
                webhook_payload=json.dumps(webhook_data),
                processed=False,
                environment=environment
            )
            
            session.add(webhook_event)
            session.commit()
            
            logger.info(f"Webhook event stored for account {account_id}: {webhook_data.get('webhook_code')}")
            
        except Exception as e:
            logger.error(f"Error handling webhook event for account {account_id}: {str(e)}")
            session.rollback()
            raise
        finally:
            if close_session:
                session.close()

    async def sync_account_from_plaid(
        self,
        account_id: str,
        force_refresh: bool = False
    ) -> PlaidAccountResponse:
        """Sync a specific account from Plaid API with enhanced tracking"""
        with get_db() as session:
            # Get the account and associated item
            account = session.exec(
                select(PlaidAccount).where(PlaidAccount.account_id == account_id)
            ).first()
            
            if not account:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Account {account_id} not found"
                )
            
            item = session.exec(
                select(PlaidItem).where(PlaidItem.id == account.item_id)
            ).first()
            
            if not item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Associated item not found"
                )
            
            # Get fresh data from Plaid
            accounts_data = await self.get_accounts(
                item.access_token, 
                account_ids=[account_id],
                environment=item.environment
            )
            
            if not accounts_data['accounts']:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Account not found in Plaid"
                )
            
            account_data = accounts_data['accounts'][0]
            
            # Track balance history before updating
            await self.track_balance_history(
                account.id, 
                account_data['balances'], 
                source="manual_sync",
                session=session
            )
            
            # Track status changes
            status_data = {
                'verification_status': account_data.get('verification_status'),
                'is_active': not account_data.get('is_closed', False),
                'is_closed': account_data.get('is_closed', False)
            }
            
            await self.track_status_change(
                account.id,
                status_data,
                change_reason="manual_sync",
                session=session
            )
            
            # Update account with fresh data
            self._update_account_from_api_data(account, account_data)
            account.last_sync = datetime.utcnow()
            
            session.add(account)
            session.commit()
            
            logger.info(f"Account {account_id} synced successfully")
            
            return self._account_to_response(account, item.institution_name)

    # Plaid API Operations (existing methods)
    
    async def get_accounts(
        self,
        access_token: str,
        account_ids: Optional[List[str]] = None,
        environment: str = 'production'
    ) -> Dict[str, Any]:
        """
        Get account information for an Item.
        
        Returns detailed account information including balances,
        account types, names, and verification status.
        
        Args:
            access_token: Access token for the Item
            account_ids: Optional list of specific account IDs to retrieve
            environment: Plaid environment ('production' or 'sandbox')
            
        Returns:
            Dict containing account information
        """
        try:
            from plaid.model.accounts_get_request import AccountsGetRequest
            
            client = self.client._get_client(environment)
            
            request = AccountsGetRequest(
                access_token=access_token,
                account_ids=account_ids
            )
            response = client.accounts_get(request)
            
            # Convert response to dictionary format
            result = response.to_dict()
            
            # Transform accounts data
            accounts = []
            for acc in result['accounts']:
                balances = acc['balances']
                
                account_data = {
                    'account_id': acc['account_id'],
                    'balances': {
                        'available': balances.get('available'),
                        'current': balances.get('current'),
                        'limit': balances.get('limit'),
                        'iso_currency_code': balances.get('iso_currency_code'),
                        'unofficial_currency_code': balances.get('unofficial_currency_code'),
                        'last_updated_datetime': balances.get('last_updated_datetime')
                    },
                    'mask': acc.get('mask'),
                    'name': acc['name'],
                    'official_name': acc.get('official_name'),
                    'type': acc['type'],
                    'subtype': acc.get('subtype'),
                    'verification_status': acc.get('verification_status'),
                    'persistent_account_id': acc.get('persistent_account_id')
                }
                accounts.append(account_data)
            
            return {
                'accounts': accounts,
                'item': result.get('item', {}),
                'total_accounts': len(accounts),
                'request_id': result['request_id'],
                'environment': environment
            }
            
        except Exception as e:
            logger.error(f"Error getting accounts in {environment}: {str(e)}")
            raise
    
    async def get_balances(
        self,
        access_token: str,
        account_ids: Optional[List[str]] = None,
        environment: str = 'production'
    ) -> Dict[str, Any]:
        """
        Get real-time balance information for accounts.
        
        This endpoint returns the same account information as get_accounts
        but may return more up-to-date balance information on some institutions.
        
        Args:
            access_token: Access token for the Item
            account_ids: Optional list of specific account IDs to retrieve
            environment: Plaid environment ('production' or 'sandbox')
            
        Returns:
            Dict containing account balance information
        """
        try:
            from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
            
            client = self.client._get_client(environment)
            
            request = AccountsBalanceGetRequest(
                access_token=access_token,
                account_ids=account_ids
            )
            response = client.accounts_balance_get(request)
            
            # Convert response to dictionary format
            result = response.to_dict()
            
            # Transform accounts data
            accounts = []
            for acc in result['accounts']:
                balances = acc['balances']
                
                account_data = {
                    'account_id': acc['account_id'],
                    'balances': {
                        'available': balances.get('available'),
                        'current': balances.get('current'),
                        'limit': balances.get('limit'),
                        'iso_currency_code': balances.get('iso_currency_code'),
                        'unofficial_currency_code': balances.get('unofficial_currency_code'),
                        'last_updated_datetime': balances.get('last_updated_datetime')
                    },
                    'mask': acc.get('mask'),
                    'name': acc['name'],
                    'official_name': acc.get('official_name'),
                    'type': acc['type'],
                    'subtype': acc.get('subtype'),
                    'verification_status': acc.get('verification_status'),
                    'persistent_account_id': acc.get('persistent_account_id')
                }
                accounts.append(account_data)
            
            return {
                'accounts': accounts,
                'item': result.get('item', {}),
                'total_accounts': len(accounts),
                'request_id': result['request_id'],
                'environment': environment,
                'balance_update': True
            }
            
        except Exception as e:
            logger.error(f"Error getting account balances in {environment}: {str(e)}")
            raise
    
    async def get_account_by_id(
        self,
        access_token: str,
        account_id: str,
        environment: str = 'production'
    ) -> Dict[str, Any]:
        """
        Get information for a specific account by ID.
        
        Args:
            access_token: Access token for the Item
            account_id: Specific account ID to retrieve
            environment: Plaid environment ('production' or 'sandbox')
            
        Returns:
            Dict containing single account information
        """
        try:
            result = await self.get_accounts(
                access_token=access_token,
                account_ids=[account_id],
                environment=environment
            )
            
            if not result['accounts']:
                raise ValueError(f"Account {account_id} not found")
            
            return {
                'account': result['accounts'][0],
                'item': result['item'],
                'request_id': result['request_id'],
                'environment': environment
            }
            
        except Exception as e:
            logger.error(f"Error getting account {account_id} in {environment}: {str(e)}")
            raise
    
    async def update_account_inversion_settings(
        self,
        account_id: str,
        user_id: str,
        invert_balance: Optional[bool] = None,
        invert_transactions: Optional[bool] = None,
        session: Optional[Session] = None
    ) -> PlaidAccountResponse:
        """Update account inversion display settings"""
        if session:
            return await self._update_account_inversion_with_session(
                session, account_id, user_id, invert_balance, invert_transactions
            )
        
        with get_db() as db:
            return await self._update_account_inversion_with_session(
                db, account_id, user_id, invert_balance, invert_transactions
            )
    
    async def _update_account_inversion_with_session(
        self,
        db: Session,
        account_id: str,
        user_id: str,
        invert_balance: Optional[bool] = None,
        invert_transactions: Optional[bool] = None,
    ) -> PlaidAccountResponse:
        """Internal method to update account inversion settings with a database session"""
        try:
            # Find the account for this user
            account = db.exec(
                select(PlaidAccount)
                .where(PlaidAccount.id == account_id)
                .where(PlaidAccount.user_id == user_id)
            ).first()
            
            if not account:
                raise HTTPException(
                    status_code=404,
                    detail="Account not found"
                )
            
            # Get the associated item for institution name
            item = db.exec(
                select(PlaidItem)
                .where(PlaidItem.id == account.item_id)
            ).first()
            
            if not item:
                raise HTTPException(
                    status_code=404,
                    detail="Associated item not found"
                )
            
            # Update only the fields that were provided
            update_data = {}
            if invert_balance is not None:
                update_data["invert_balance"] = invert_balance
            if invert_transactions is not None:
                update_data["invert_transactions"] = invert_transactions
            
            if not update_data:
                # No changes requested, return current account
                return self._account_to_response(account, item.institution_name)
            
            # Apply updates
            for field, value in update_data.items():
                setattr(account, field, value)
            
            # Update timestamp
            account.updated_at = datetime.utcnow()
            
            # Save changes
            db.add(account)
            db.commit()
            db.refresh(account)
            
            # Return updated account
            return self._account_to_response(account, item.institution_name)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating account inversion settings for {account_id}: {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Failed to update account settings"
            )
