"""
Accounts Service

Business logic layer for account management operations.
Handles CRUD operations, balance updates, and account synchronization.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlmodel import select, and_, or_, func
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import Column
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
import logging

from api.common.utils import generate_id
from .models import Account, AccountSourceMapping, AccountBalanceHistory, AccountStatusHistory, AccountStatus
from .schemas import (
    AccountCreate,
    AccountUpdate,
    AccountSearchRequest,
    AccountResponse,
    AccountListResponse,
    AccountSummaryResponse,
    AccountBalanceUpdate,
    PlaidAccountSyncRequest,
    AccountBalanceHistoryResponse,
    AccountStatusHistoryResponse
)

logger = logging.getLogger(__name__)


class AccountService:
    """Service class for account operations"""

    def __init__(self):
        """Initialize the account service"""
        pass

    async def create_account(self, session: AsyncSession, request: AccountCreate) -> AccountResponse:
        """
        Create a new account

        Args:
            session: Database session
            request: Account creation request

        Returns:
            Created account response

        Raises:
            HTTPException: If account creation fails
        """
        try:
            # Generate unique ID
            account_id = generate_id()

            # Create account instance
            account = Account(
                id=account_id,
                institution_id=request.institution_id,
                user_id=request.user_id,
                name=request.name,
                official_name=request.official_name,
                nickname=request.nickname,
                account_type=request.account_type,
                account_subtype=request.account_subtype,
                primary_source=request.primary_source,
                plaid_account_id=request.plaid_account_id,
                account_number=request.account_number,
                routing_number=request.routing_number,
                holder_category=request.holder_category,
                available_balance=request.available_balance,
                current_balance=request.current_balance,
                limit_balance=request.limit_balance,
                iso_currency_code=request.iso_currency_code,
                unofficial_currency_code=request.unofficial_currency_code,
                status=request.status,
                is_closed=request.is_closed,
                invert_balance=request.invert_balance,
                invert_transactions=request.invert_transactions,
                plaid_enabled=request.plaid_enabled,
                manual_entry_allowed=request.manual_entry_allowed,
                notes=request.notes,
                tags=request.tags,
                balance_last_updated=datetime.utcnow() if request.current_balance is not None else None,
                verification_status=None,
                last_plaid_sync=None
            )

            # Add to database
            session.add(account)
            await session.commit()
            await session.refresh(account)

            logger.info(f"Created account {account_id} for user {request.user_id}")
            return self._account_to_response(account)

        except IntegrityError as e:
            await session.rollback()
            if "plaid_account_id" in str(e):
                raise HTTPException(
                    status_code=409,
                    detail=f"Account with Plaid ID {request.plaid_account_id} already exists"
                )
            raise HTTPException(
                status_code=400,
                detail="Account creation failed due to data constraint violation"
            )
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating account: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to create account"
            )

    async def get_account_by_id(self, session: AsyncSession, account_id: str) -> Optional[AccountResponse]:
        """
        Get account by ID

        Args:
            session: Database session
            account_id: Account ID

        Returns:
            Account response or None if not found
        """
        try:
            result = await session.exec(
                select(Account).where(Account.id == account_id)
            )
            account = result.first()

            if not account:
                return None

            return self._account_to_response(account)

        except Exception as e:
            logger.error(f"Error retrieving account {account_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve account"
            )

    async def update_account(self, session: AsyncSession, account_id: str, request: AccountUpdate) -> Optional[AccountResponse]:
        """
        Update an existing account

        Args:
            session: Database session
            account_id: Account ID
            request: Update request

        Returns:
            Updated account response or None if not found
        """
        try:
            # Get existing account
            query = select(Account).where(Account.id == account_id)
            result = await session.execute(query)
            account = result.scalar_one_or_none()

            if not account:
                return None

            # Track status changes
            if request.status and request.status != account.status:
                await self._record_status_change(
                    session, account_id, account.status, request.status,
                    account.is_closed, request.is_closed or account.is_closed
                )

            # Update fields
            update_data = request.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(account, field):
                    setattr(account, field, value)

            # Update balance timestamp if balance changed
            if any(field in update_data for field in ['available_balance', 'current_balance', 'limit_balance']):
                account.balance_last_updated = datetime.utcnow()

            account.updated_at = datetime.utcnow()

            await session.commit()
            await session.refresh(account)

            logger.info(f"Updated account {account_id}")
            return self._account_to_response(account)

        except Exception as e:
            await session.rollback()
            logger.error(f"Error updating account {account_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to update account"
            )

    async def delete_account(self, session: AsyncSession, account_id: str) -> bool:
        """
        Soft delete an account (mark as closed)

        Args:
            session: Database session
            account_id: Account ID

        Returns:
            True if account was deleted, False if not found
        """
        try:
            # Get existing account
            query = select(Account).where(Account.id == account_id)
            result = await session.execute(query)
            account = result.scalar_one_or_none()

            if not account:
                return False

            # Track status change
            await self._record_status_change(
                session, account_id, account.status, AccountStatus.CLOSED,
                account.is_closed, True
            )

            # Mark as closed
            account.status = AccountStatus.CLOSED
            account.is_closed = True
            account.updated_at = datetime.utcnow()

            await session.commit()

            logger.info(f"Closed account {account_id}")
            return True

        except Exception as e:
            await session.rollback()
            logger.error(f"Error deleting account {account_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to delete account"
            )

    async def list_accounts(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        search_request: Optional[AccountSearchRequest] = None
    ) -> tuple[List[AccountResponse], int]:
        """
        List accounts with optional filtering and pagination

        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            search_request: Optional search/filter criteria

        Returns:
            Tuple of (accounts list, total count)
        """
        try:
            # Base query
            query = select(Account)
            count_query = select(func.count(Account.id))

            # Apply filters
            filters = []

            if search_request:
                if search_request.name:
                    filters.append(Account.name.ilike(f"%{search_request.name}%"))

                if search_request.account_type:
                    filters.append(Account.account_type == search_request.account_type)

                if search_request.account_subtype:
                    filters.append(Account.account_subtype == search_request.account_subtype)

                if search_request.primary_source:
                    filters.append(Account.primary_source == search_request.primary_source)

                if search_request.institution_id:
                    filters.append(Account.institution_id == search_request.institution_id)

                if search_request.holder_category:
                    filters.append(Account.holder_category == search_request.holder_category)

                if search_request.status:
                    filters.append(Account.status == search_request.status)

                if search_request.is_closed is not None:
                    filters.append(Account.is_closed == search_request.is_closed)

                if search_request.plaid_enabled is not None:
                    filters.append(Account.plaid_enabled == search_request.plaid_enabled)

                if search_request.min_balance is not None and search_request.min_balance is not None:
                    filters.append(Account.current_balance >= search_request.min_balance)

                if search_request.max_balance is not None and search_request.max_balance is not None:
                    filters.append(Account.current_balance <= search_request.max_balance)

                if search_request.tags:
                    # Search for accounts with any of the specified tags
                    tag_filters = []
                    for tag in search_request.tags.split(","):
                        tag = tag.strip()
                        if tag and Account.tags is not None:
                            tag_filters.append(Account.tags.ilike(f"%{tag}%"))
                    if tag_filters:
                        filters.append(or_(*tag_filters))

            # Get total count
            count_result = await session.exec(query)
            total = len(count_result.all())

            # Apply pagination and get results
            paginated_query = query.offset(skip).limit(limit).order_by(Account.name)
            result = await session.exec(paginated_query)
            accounts = result.all()

            return [self._account_to_response(account) for account in accounts], total

        except Exception as e:
            logger.error(f"Error listing accounts: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve accounts"
            )

    async def get_accounts_by_institution(self, session: AsyncSession, institution_id: str) -> List[AccountResponse]:
        """
        Get all accounts for a specific institution

        Args:
            session: Database session
            institution_id: Institution ID

        Returns:
            List of account responses
        """
        try:
            result = await session.exec(
                select(Account).where(Account.institution_id == institution_id)
            )
            accounts = result.all()

            return [self._account_to_response(account) for account in accounts]

        except Exception as e:
            logger.error(f"Error retrieving accounts for institution {institution_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve accounts"
            )

    async def get_accounts_by_user(self, session: AsyncSession, user_id: str) -> List[AccountResponse]:
        """
        Get all accounts for a specific user

        Args:
            session: Database session
            user_id: User ID

        Returns:
            List of account responses
        """
        try:
            result = await session.exec(
                select(Account).where(Account.user_id == user_id)
            )
            accounts = result.all()

            return [self._account_to_response(account) for account in accounts]

        except Exception as e:
            logger.error(f"Error retrieving accounts for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve accounts"
            )

    async def update_account_balance(
        self,
        session: AsyncSession,
        account_id: str,
        balance_update: AccountBalanceUpdate
    ) -> Optional[AccountResponse]:
        """
        Update account balance and record history

        Args:
            session: Database session
            account_id: Account ID
            balance_update: Balance update data

        Returns:
            Updated account response or None if not found
        """
        try:
            # Get existing account
            result = await session.exec(
                select(Account).where(Account.id == account_id)
            )
            account = result.first()

            if not account:
                return None

            # Record balance history
            if account.current_balance is not None or account.available_balance is not None:
                history = AccountBalanceHistory(
                    account_id=account_id,
                    available_balance=account.available_balance,
                    current_balance=account.current_balance,
                    limit_balance=account.limit_balance,
                    iso_currency_code=account.iso_currency_code,
                    available_change=balance_update.available_balance - account.available_balance if balance_update.available_balance is not None and account.available_balance is not None else None,
                    current_change=balance_update.current_balance - account.current_balance if balance_update.current_balance is not None and account.current_balance is not None else None,
                    source=balance_update.source,
                    balance_updated_at=datetime.utcnow()
                )
                session.add(history)

            # Update balance
            if balance_update.available_balance is not None:
                account.available_balance = balance_update.available_balance
            if balance_update.current_balance is not None:
                account.current_balance = balance_update.current_balance
            if balance_update.limit_balance is not None:
                account.limit_balance = balance_update.limit_balance
            if balance_update.iso_currency_code:
                account.iso_currency_code = balance_update.iso_currency_code
            if balance_update.unofficial_currency_code:
                account.unofficial_currency_code = balance_update.unofficial_currency_code

            account.balance_last_updated = datetime.utcnow()
            account.updated_at = datetime.utcnow()

            await session.commit()
            await session.refresh(account)

            logger.info(f"Updated balance for account {account_id}")
            return self._account_to_response(account)

        except Exception as e:
            await session.rollback()
            logger.error(f"Error updating account balance {account_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to update account balance"
            )

    async def get_account_summary(self, session: AsyncSession, user_id: Optional[str] = None) -> AccountSummaryResponse:
        """
        Get account summary statistics

        Args:
            session: Database session
            user_id: Optional user ID to filter by

        Returns:
            Account summary response
        """
        try:
            # Base query
            query = select(Account)
            if user_id:
                query = query.where(Account.user_id == user_id)

            result = await session.exec(query)
            accounts = result.all()

            # Calculate statistics
            total_accounts = len(accounts)
            active_accounts = len([a for a in accounts if a.status == AccountStatus.ACTIVE and not a.is_closed])

            total_balance = sum(a.current_balance or 0 for a in accounts)
            total_available_balance = sum(a.available_balance or 0 for a in accounts)

            # Group by categories
            accounts_by_type = {}
            accounts_by_source = {}
            accounts_by_status = {}

            for account in accounts:
                # By type
                type_key = account.account_type.value
                accounts_by_type[type_key] = accounts_by_type.get(type_key, 0) + 1

                # By source
                source_key = account.primary_source.value
                accounts_by_source[source_key] = accounts_by_source.get(source_key, 0) + 1

                # By status
                status_key = account.status.value
                accounts_by_status[status_key] = accounts_by_status.get(status_key, 0) + 1

            return AccountSummaryResponse(
                total_accounts=total_accounts,
                active_accounts=active_accounts,
                total_balance=total_balance,
                total_available_balance=total_available_balance,
                accounts_by_type=accounts_by_type,
                accounts_by_source=accounts_by_source,
                accounts_by_status=accounts_by_status
            )

        except Exception as e:
            logger.error(f"Error getting account summary: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to get account summary"
            )

    async def sync_plaid_account(self, session: AsyncSession, request: PlaidAccountSyncRequest) -> AccountResponse:
        """
        Sync account data from Plaid

        Args:
            session: Database session
            request: Plaid sync request

        Returns:
            Synced account response
        """
        # This would integrate with the Plaid service to sync account data
        # For now, return a placeholder implementation
        logger.info(f"Syncing Plaid account {request.plaid_account_id}")

        # TODO: Implement actual Plaid sync logic
        raise HTTPException(
            status_code=501,
            detail="Plaid account sync not yet implemented"
        )

    def _account_to_response(self, account: Account) -> AccountResponse:
        """Convert Account model to AccountResponse schema"""
        return AccountResponse(
            id=account.id or "",
            institution_id=account.institution_id,
            user_id=account.user_id,
            name=account.name,
            official_name=account.official_name,
            nickname=account.nickname,
            account_type=account.account_type,
            account_subtype=account.account_subtype,
            primary_source=account.primary_source,
            plaid_account_id=account.plaid_account_id,
            account_number=account.account_number,
            routing_number=account.routing_number,
            holder_category=account.holder_category,
            available_balance=account.available_balance,
            current_balance=account.current_balance,
            limit_balance=account.limit_balance,
            iso_currency_code=account.iso_currency_code,
            unofficial_currency_code=account.unofficial_currency_code,
            status=account.status,
            is_closed=account.is_closed,
            invert_balance=account.invert_balance,
            invert_transactions=account.invert_transactions,
            plaid_enabled=account.plaid_enabled,
            manual_entry_allowed=account.manual_entry_allowed,
            notes=account.notes,
            tags=account.tags,
            balance_last_updated=account.balance_last_updated,
            verification_status=account.verification_status,
            health_status=account.health_status,
            last_health_check=account.last_health_check,
            plaid_sync_errors=account.plaid_sync_errors,
            last_plaid_sync=account.last_plaid_sync,
            created_at=account.created_at,
            updated_at=account.updated_at,
            tags_list=account.tags_list,
            balance_display=account.balance_display,
            is_positive_balance=account.is_positive_balance
        )

    async def _record_status_change(
        self,
        session: AsyncSession,
        account_id: str,
        old_status: AccountStatus,
        new_status: AccountStatus,
        old_closed: bool,
        new_closed: bool
    ):
        """Record account status change in history"""
        try:
            history = AccountStatusHistory(
                account_id=account_id,
                previous_status=old_status,
                new_status=new_status,
                previous_closed=old_closed,
                new_closed=new_closed,
                change_reason="api_update",
                source="system"
            )
            session.add(history)
        except Exception as e:
            logger.warning(f"Failed to record status change for account {account_id}: {str(e)}")


# Global service instance
account_service = AccountService()
