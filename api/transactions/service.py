"""
Transactions Service

Business logic layer for transaction management operations.
Handles CRUD operations, categorization, reconciliation, and transaction synchronization.
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, timedelta
from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
import logging
import json
from collections import defaultdict

from api.common.utils import generate_id
from .models import (
    Transaction,
    TransactionSourceMapping,
    TransactionModificationHistory,
    RecurringTransaction,
    TransactionReconciliation,
    UserCategory,
    CategoryRule,
    TransactionType,
    TransactionStatus,
    TransactionSource,
    TransactionCategory,
    TransactionSubcategory
)
from .schemas import (
    TransactionCreate,
    TransactionUpdate,
    TransactionSearchRequest,
    TransactionResponse,
    TransactionListResponse,
    TransactionSummaryResponse,
    TransactionReconciliationRequest,
    TransactionReconciliationResponse,
    RecurringTransactionCreate,
    RecurringTransactionResponse,
    PlaidTransactionSyncRequest,
    BulkTransactionUpdateRequest,
    TransactionDuplicateCheckRequest,
    TransactionDuplicateResponse,
    TransactionCategoryCreate,
    TransactionCategoryUpdate,
    TransactionCategoryResponse,
    TransactionCategoryTreeResponse,
    TransactionCategoryMoveRequest,
    CategoryRuleCreate,
    CategoryRuleUpdate,
    CategoryRuleResponse,
    CategoryRuleTestRequest,
    CategoryRuleTestResponse
)

logger = logging.getLogger(__name__)


class TransactionService:
    """Service class for transaction operations"""

    def __init__(self):
        """Initialize the transaction service"""
        pass

    async def create_transaction(self, session: AsyncSession, request: TransactionCreate) -> TransactionResponse:
        """
        Create a new transaction

        Args:
            session: Database session
            request: Transaction creation request

        Returns:
            Created transaction response

        Raises:
            HTTPException: If transaction creation fails
        """
        try:
            # Generate unique ID
            transaction_id = generate_id()

            # Check for potential duplicates
            duplicate_check = await self._check_for_duplicates(
                session, request.account_id, request.amount,
                request.transaction_date, request.name, request.merchant_name
            )

            if duplicate_check.is_duplicate:
                logger.warning(f"Potential duplicate transaction detected: {duplicate_check}")

            # Create transaction instance
            transaction = Transaction(
                id=transaction_id,
                account_id=request.account_id,
                institution_id=request.institution_id,
                user_id=request.user_id,
                plaid_transaction_id=request.plaid_transaction_id,
                external_transaction_id=request.external_transaction_id,
                amount=request.amount,
                transaction_type=request.transaction_type,
                transaction_date=request.transaction_date,
                transaction_datetime=request.transaction_datetime,
                name=request.name,
                description=request.description,
                merchant_name=request.merchant_name,
                merchant_entity_id=request.merchant_entity_id,
                category=request.category,
                subcategory=request.subcategory,
                custom_category=request.custom_category,
                user_category_id=None,  # Will be set by categorization rules
                status=request.status,
                source=request.source,
                is_pending=request.is_pending,
                iso_currency_code=request.iso_currency_code,
                unofficial_currency_code=request.unofficial_currency_code,
                exchange_rate=request.exchange_rate,
                check_number=request.check_number,
                payment_method=request.payment_method,
                location_json=None,  # Will be set from location dict if provided
                counterparty_name=request.counterparty_name,
                counterparty_type=request.counterparty_type,
                logo_url=request.logo_url,
                website=request.website,
                is_recurring=request.is_recurring,
                recurrence_pattern=request.recurrence_pattern,
                recurrence_id=request.recurrence_id,
                tags=",".join(request.tags) if request.tags else None,
                notes=request.notes,
                is_reconciled=request.is_reconciled,
                reconciled_at=None,
                reconciled_by=None,
                created_by=request.user_id,
                updated_by=None,
                confidence_score=duplicate_check.confidence_score if duplicate_check.is_duplicate else None,
                duplicate_of=duplicate_check.duplicate_of if duplicate_check.is_duplicate else None,
                last_verified=None
            )

            # Set location data if provided
            if request.location:
                transaction.location_dict = request.location

            # Add to database
            session.add(transaction)
            await session.commit()
            await session.refresh(transaction)

            # Record creation in modification history
            await self._record_modification(
                session, transaction_id, "create", None, None,
                "Transaction created", request.user_id
            )

            logger.info(f"Created transaction {transaction_id} for user {request.user_id}")
            return self._transaction_to_response(transaction)

        except IntegrityError as e:
            await session.rollback()
            logger.error(f"Integrity error creating transaction: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail="Transaction creation failed due to data constraint violation"
            )
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating transaction: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to create transaction"
            )

    async def get_transaction_by_id(self, session: AsyncSession, transaction_id: str) -> Optional[TransactionResponse]:
        """
        Get transaction by ID

        Args:
            session: Database session
            transaction_id: Transaction ID

        Returns:
            Transaction response or None if not found
        """
        try:
            result = await session.execute(
                select(Transaction).where(Transaction.id == transaction_id)
            )
            transaction = result.scalar_one_or_none()

            if not transaction:
                return None

            return self._transaction_to_response(transaction)

        except Exception as e:
            logger.error(f"Error retrieving transaction {transaction_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve transaction"
            )

    async def update_transaction(
        self,
        session: AsyncSession,
        transaction_id: str,
        request: TransactionUpdate,
        updated_by: Optional[str] = None
    ) -> Optional[TransactionResponse]:
        """
        Update an existing transaction

        Args:
            session: Database session
            transaction_id: Transaction ID
            request: Update request
            updated_by: User who made the update

        Returns:
            Updated transaction response or None if not found
        """
        try:
            # Get existing transaction
            result = await session.execute(
                select(Transaction).where(Transaction.id == transaction_id)
            )
            transaction = result.scalar_one_or_none()

            if not transaction:
                return None

            # Track changes for history
            changes = {}

            # Update fields and track changes
            update_data = request.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(transaction, field):
                    old_value = getattr(transaction, field)
                    if old_value != value:
                        changes[field] = (old_value, value)
                        setattr(transaction, field, value)

            # Handle special cases
            if "tags" in update_data and update_data["tags"] is not None:
                transaction.tags = ",".join(update_data["tags"])
            if "location" in update_data and update_data["location"] is not None:
                transaction.location_dict = update_data["location"]

            # Update metadata
            transaction.updated_at = datetime.utcnow()
            transaction.updated_by = updated_by

            # Record changes in modification history
            for field, (old_value, new_value) in changes.items():
                await self._record_modification(
                    session, transaction_id, "update", field,
                    str(old_value), str(new_value), updated_by
                )

            await session.commit()
            await session.refresh(transaction)

            logger.info(f"Updated transaction {transaction_id}")
            return self._transaction_to_response(transaction)

        except Exception as e:
            await session.rollback()
            logger.error(f"Error updating transaction {transaction_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to update transaction"
            )

    async def delete_transaction(self, session: AsyncSession, transaction_id: str, deleted_by: Optional[str] = None) -> bool:
        """
        Soft delete a transaction (mark as cancelled)

        Args:
            session: Database session
            transaction_id: Transaction ID
            deleted_by: User who deleted the transaction

        Returns:
            True if transaction was deleted, False if not found
        """
        try:
            # Get existing transaction
            result = await session.execute(
                select(Transaction).where(Transaction.id == transaction_id)
            )
            transaction = result.scalar_one_or_none()

            if not transaction:
                return False

            # Record deletion in modification history
            await self._record_modification(
                session, transaction_id, "delete", None, None,
                "Transaction deleted", deleted_by
            )

            # Mark as cancelled
            transaction.status = TransactionStatus.CANCELLED
            transaction.updated_at = datetime.utcnow()
            transaction.updated_by = deleted_by

            await session.commit()

            logger.info(f"Deleted transaction {transaction_id}")
            return True

        except Exception as e:
            await session.rollback()
            logger.error(f"Error deleting transaction {transaction_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to delete transaction"
            )

    async def list_transactions(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        search_request: Optional[TransactionSearchRequest] = None
    ) -> Tuple[List[TransactionResponse], int]:
        """
        List transactions with optional filtering and pagination

        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            search_request: Optional search/filter criteria

        Returns:
            Tuple of (transactions list, total count)
        """
        try:
            # Base query
            query = select(Transaction)
            count_query = select(func.count()).select_from(Transaction)

            # Apply filters
            filters = []

            if search_request:
                # Date filtering
                if search_request.start_date:
                    filters.append(Transaction.transaction_date >= search_request.start_date)
                if search_request.end_date:
                    filters.append(Transaction.transaction_date <= search_request.end_date)

                # Amount filtering
                if search_request.min_amount is not None:
                    filters.append(Transaction.amount >= search_request.min_amount)
                if search_request.max_amount is not None:
                    filters.append(Transaction.amount <= search_request.max_amount)

                # Categorization filtering
                if search_request.category:
                    filters.append(Transaction.category == search_request.category)
                if search_request.subcategory:
                    filters.append(Transaction.subcategory == search_request.subcategory)
                if search_request.custom_category:
                    filters.append(Transaction.custom_category.ilike(f"%{search_request.custom_category}%"))

                # Status filtering
                if search_request.status:
                    filters.append(Transaction.status == search_request.status)
                if search_request.is_pending is not None:
                    filters.append(Transaction.is_pending == search_request.is_pending)
                if search_request.is_reconciled is not None:
                    filters.append(Transaction.is_reconciled == search_request.is_reconciled)

                # Source filtering
                if search_request.source:
                    filters.append(Transaction.source == search_request.source)
                if search_request.plaid_transaction_id:
                    filters.append(Transaction.plaid_transaction_id == search_request.plaid_transaction_id)

                # Relationship filtering
                if search_request.account_id:
                    filters.append(Transaction.account_id == search_request.account_id)
                if search_request.institution_id:
                    filters.append(Transaction.institution_id == search_request.institution_id)
                if search_request.user_id:
                    filters.append(Transaction.user_id == search_request.user_id)

                # Text search
                if search_request.search_text:
                    search_filters = [
                        Transaction.name.ilike(f"%{search_request.search_text}%"),
                        Transaction.description.ilike(f"%{search_request.search_text}%"),
                        Transaction.merchant_name.ilike(f"%{search_request.search_text}%")
                    ]
                    filters.append(or_(*search_filters))

                # Merchant filtering
                if search_request.merchant_name:
                    filters.append(Transaction.merchant_name.ilike(f"%{search_request.merchant_name}%"))
                if search_request.merchant_entity_id:
                    filters.append(Transaction.merchant_entity_id == search_request.merchant_entity_id)

                # Recurring filtering
                if search_request.is_recurring is not None:
                    filters.append(Transaction.is_recurring == search_request.is_recurring)
                if search_request.recurrence_id:
                    filters.append(Transaction.recurrence_id == search_request.recurrence_id)

                # Tag filtering
                if search_request.tags:
                    for tag in search_request.tags.split(","):
                        tag = tag.strip()
                        if tag:
                            filters.append(Transaction.tags.ilike(f"%{tag}%"))

            # Apply filters to both queries
            if filters:
                query = query.where(and_(*filters))
                count_query = count_query.where(and_(*filters))

            # Apply sorting
            if search_request and search_request.sort_by:
                sort_column = getattr(Transaction, search_request.sort_by, Transaction.transaction_date)
                if search_request.sort_order == "asc":
                    query = query.order_by(asc(sort_column))
                else:
                    query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(desc(Transaction.transaction_date))

            # Get total count
            count_result = await session.execute(count_query)
            total = count_result.scalar() or 0

            # Apply pagination and get results
            paginated_query = query.offset(skip).limit(limit)
            result = await session.execute(paginated_query)
            transactions = result.scalars().all()

            return [self._transaction_to_response(transaction) for transaction in transactions], total

        except Exception as e:
            logger.error(f"Error listing transactions: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve transactions"
            )

    async def get_transaction_summary(
        self,
        session: AsyncSession,
        user_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> TransactionSummaryResponse:
        """
        Get transaction summary statistics

        Args:
            session: Database session
            user_id: Optional user ID to filter by
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering

        Returns:
            Transaction summary response
        """
        try:
            # Base query
            query = select(Transaction)
            if user_id:
                query = query.where(Transaction.user_id == user_id)
            if start_date:
                query = query.where(Transaction.transaction_date >= start_date)
            if end_date:
                query = query.where(Transaction.transaction_date <= end_date)

            result = await session.execute(query)
            transactions = result.scalars().all()

            # Calculate statistics
            total_transactions = len(transactions)
            pending_transactions = len([t for t in transactions if t.is_pending])
            reconciled_transactions = len([t for t in transactions if t.is_reconciled])
            recurring_transactions = len([t for t in transactions if t.is_recurring])

            # Amount statistics
            total_debits = sum(abs(t.amount) for t in transactions if t.amount < 0)
            total_credits = sum(t.amount for t in transactions if t.amount > 0)
            net_amount = total_credits - total_debits

            # Category breakdown
            transactions_by_category = defaultdict(int)
            amount_by_category = defaultdict(float)

            for transaction in transactions:
                category_key = transaction.category.value if transaction.category else "uncategorized"
                transactions_by_category[category_key] += 1
                amount_by_category[category_key] += transaction.amount

            # Source breakdown
            transactions_by_source = defaultdict(int)
            amount_by_source = defaultdict(float)

            for transaction in transactions:
                source_key = transaction.source.value
                transactions_by_source[source_key] += 1
                amount_by_source[source_key] += transaction.amount

            return TransactionSummaryResponse(
                total_transactions=total_transactions,
                pending_transactions=pending_transactions,
                reconciled_transactions=reconciled_transactions,
                recurring_transactions=recurring_transactions,
                total_debits=total_debits,
                total_credits=total_credits,
                net_amount=net_amount,
                transactions_by_category=dict(transactions_by_category),
                amount_by_category=dict(amount_by_category),
                transactions_by_source=dict(transactions_by_source),
                amount_by_source=dict(amount_by_source),
                date_range_start=start_date,
                date_range_end=end_date
            )

        except Exception as e:
            logger.error(f"Error getting transaction summary: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to get transaction summary"
            )

    async def reconcile_transactions(
        self,
        session: AsyncSession,
        request: TransactionReconciliationRequest,
        reconciled_by: str
    ) -> TransactionReconciliationResponse:
        """
        Perform transaction reconciliation

        Args:
            session: Database session
            request: Reconciliation request
            reconciled_by: User performing reconciliation

        Returns:
            Reconciliation response
        """
        try:
            # Get all transactions for the account up to the reconciliation date
            result = await session.execute(
                select(Transaction).where(
                    and_(
                        Transaction.account_id == request.account_id,
                        Transaction.transaction_date <= request.reconciliation_date,
                        Transaction.status != TransactionStatus.CANCELLED
                    )
                )
            )
            transactions = result.scalars().all()

            # Calculate balance from transactions
            calculated_balance = sum(t.amount for t in transactions)
            difference = request.statement_balance - calculated_balance
            is_balanced = abs(difference) < 0.01  # Allow for small rounding differences

            # Mark transactions as reconciled
            reconciled_count = 0
            for transaction in transactions:
                if not transaction.is_reconciled:
                    transaction.is_reconciled = True
                    transaction.reconciled_at = datetime.utcnow()
                    transaction.reconciled_by = reconciled_by
                    reconciled_count += 1

            # Create reconciliation record
            reconciliation = TransactionReconciliation(
                id=generate_id(),
                account_id=request.account_id,
                reconciliation_date=request.reconciliation_date,
                statement_balance=request.statement_balance,
                calculated_balance=calculated_balance,
                difference=difference,
                is_balanced=is_balanced,
                reconciled_transactions=reconciled_count,
                outstanding_transactions=0,  # Could be calculated differently
                reconciled_by=reconciled_by,
                notes=request.notes
            )

            session.add(reconciliation)
            await session.commit()

            logger.info(f"Reconciliation completed for account {request.account_id}")
            return TransactionReconciliationResponse(
                reconciliation_id=reconciliation.id,
                account_id=reconciliation.account_id,
                reconciliation_date=reconciliation.reconciliation_date,
                statement_balance=reconciliation.statement_balance,
                calculated_balance=reconciliation.calculated_balance,
                difference=reconciliation.difference,
                is_balanced=reconciliation.is_balanced,
                reconciled_transactions=reconciliation.reconciled_transactions,
                outstanding_transactions=reconciliation.outstanding_transactions,
                reconciled_by=reconciliation.reconciled_by,
                notes=reconciliation.notes,
                created_at=reconciliation.created_at
            )

        except Exception as e:
            await session.rollback()
            logger.error(f"Error performing reconciliation: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to perform reconciliation"
            )

    async def bulk_update_transactions(
        self,
        session: AsyncSession,
        request: BulkTransactionUpdateRequest,
        updated_by: str
    ) -> List[TransactionResponse]:
        """
        Bulk update multiple transactions

        Args:
            session: Database session
            request: Bulk update request
            updated_by: User performing the update

        Returns:
            List of updated transaction responses
        """
        try:
            updated_transactions = []

            for transaction_id in request.transaction_ids:
                updated = await self.update_transaction(
                    session, transaction_id, request.updates, updated_by
                )
                if updated:
                    updated_transactions.append(updated)

            logger.info(f"Bulk updated {len(updated_transactions)} transactions")
            return updated_transactions

        except Exception as e:
            await session.rollback()
            logger.error(f"Error performing bulk update: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to perform bulk update"
            )

    async def check_duplicates(
        self,
        session: AsyncSession,
        request: TransactionDuplicateCheckRequest
    ) -> TransactionDuplicateResponse:
        """
        Check for duplicate transactions

        Args:
            session: Database session
            request: Duplicate check request

        Returns:
            Duplicate check response
        """
        return await self._check_for_duplicates(
            session, request.account_id, request.amount,
            request.transaction_date, request.name, request.merchant_name
        )

    async def _check_for_duplicates(
        self,
        session: AsyncSession,
        account_id: str,
        amount: float,
        transaction_date: date,
        name: str,
        merchant_name: Optional[str] = None
    ) -> TransactionDuplicateResponse:
        """
        Internal method to check for duplicate transactions

        Args:
            session: Database session
            account_id: Account ID
            amount: Transaction amount
            transaction_date: Transaction date
            name: Transaction name
            merchant_name: Optional merchant name

        Returns:
            Duplicate check response
        """
        try:
            # Look for transactions with same amount, date, and similar name
            date_range_start = transaction_date - timedelta(days=3)
            date_range_end = transaction_date + timedelta(days=3)

            # Find similar transactions
            result = await session.execute(
                select(Transaction).where(
                    and_(
                        Transaction.account_id == account_id,
                        Transaction.amount == amount,
                        Transaction.transaction_date >= date_range_start,
                        Transaction.transaction_date <= date_range_end,
                        Transaction.status != TransactionStatus.CANCELLED
                    )
                )
            )
            similar_transactions = result.scalars().all()

            # Filter by name similarity
            exact_matches = []
            similar_matches = []

            for transaction in similar_transactions:
                name_similarity = self._calculate_name_similarity(name, transaction.name)
                if name_similarity > 0.9:  # Very similar names
                    exact_matches.append(transaction)
                elif name_similarity > 0.6:  # Somewhat similar names
                    similar_matches.append(transaction)

            # Determine if this is a duplicate
            is_duplicate = len(exact_matches) > 0
            duplicate_of = exact_matches[0].id if exact_matches else None

            # Calculate confidence score
            confidence_score = 0.0
            if exact_matches:
                confidence_score = 0.95
            elif similar_matches:
                confidence_score = 0.7

            return TransactionDuplicateResponse(
                is_duplicate=is_duplicate,
                duplicate_of=duplicate_of,
                confidence_score=confidence_score,
                similar_transactions=[
                    self._transaction_to_response(t) for t in exact_matches + similar_matches[:5]
                ]
            )

        except Exception as e:
            logger.error(f"Error checking for duplicates: {str(e)}")
            return TransactionDuplicateResponse(
                is_duplicate=False,
                confidence_score=0.0,
                similar_transactions=[]
            )

    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two transaction names"""
        if not name1 or not name2:
            return 0.0

        # Simple similarity based on common words
        words1 = set(name1.lower().split())
        words2 = set(name2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    async def _record_modification(
        self,
        session: AsyncSession,
        transaction_id: str,
        modification_type: str,
        field_changed: Optional[str],
        previous_value: Optional[str],
        new_value: Optional[str],
        changed_by: Optional[str]
    ):
        """Record transaction modification in history"""
        try:
            history = TransactionModificationHistory(
                id=generate_id(),
                transaction_id=transaction_id,
                modification_type=modification_type,
                field_changed=field_changed,
                previous_value=previous_value,
                new_value=new_value,
                change_reason="api_update",
                changed_by=changed_by
            )
            session.add(history)
        except Exception as e:
            logger.warning(f"Failed to record modification for transaction {transaction_id}: {str(e)}")

    def _transaction_to_response(self, transaction: Transaction) -> TransactionResponse:
        """Convert Transaction model to TransactionResponse schema"""
        return TransactionResponse(
            id=transaction.id or "",
            account_id=transaction.account_id,
            institution_id=transaction.institution_id,
            user_id=transaction.user_id,
            plaid_transaction_id=transaction.plaid_transaction_id,
            external_transaction_id=transaction.external_transaction_id,
            amount=transaction.amount,
            transaction_type=transaction.transaction_type,
            transaction_date=transaction.transaction_date,
            transaction_datetime=transaction.transaction_datetime,
            name=transaction.name,
            description=transaction.description,
            merchant_name=transaction.merchant_name,
            merchant_entity_id=transaction.merchant_entity_id,
            category=transaction.category,
            subcategory=transaction.subcategory,
            custom_category=transaction.custom_category,
            status=transaction.status,
            source=transaction.source,
            is_pending=transaction.is_pending,
            iso_currency_code=transaction.iso_currency_code,
            unofficial_currency_code=transaction.unofficial_currency_code,
            exchange_rate=transaction.exchange_rate,
            check_number=transaction.check_number,
            payment_method=transaction.payment_method,
            location=transaction.location_dict,
            counterparty_name=transaction.counterparty_name,
            counterparty_type=transaction.counterparty_type,
            logo_url=transaction.logo_url,
            website=transaction.website,
            is_recurring=transaction.is_recurring,
            recurrence_pattern=transaction.recurrence_pattern,
            recurrence_id=transaction.recurrence_id,
            tags=transaction.tags_list,
            notes=transaction.notes,
            is_reconciled=transaction.is_reconciled,
            reconciled_at=transaction.reconciled_at,
            reconciled_by=transaction.reconciled_by,
            created_by=transaction.created_by,
            updated_by=transaction.updated_by,
            confidence_score=transaction.confidence_score,
            duplicate_of=transaction.duplicate_of,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at,
            last_verified=transaction.last_verified,
            tags_list=transaction.tags_list,
            absolute_amount=transaction.absolute_amount,
            is_debit=transaction.is_debit,
            is_credit=transaction.is_credit
        )


# Global service instance
transaction_service = TransactionService()


class TransactionCategoryService:
    """Service class for transaction category operations"""

    def __init__(self):
        """Initialize the transaction category service"""
        pass

    async def create_category(self, session: AsyncSession, request: TransactionCategoryCreate) -> TransactionCategoryResponse:
        """
        Create a new user category

        Args:
            session: Database session
            request: Category creation request

        Returns:
            Created category response

        Raises:
            HTTPException: If category creation fails
        """
        try:
            # Generate unique ID
            category_id = generate_id()

            # Determine level and path
            level = 1
            path = request.name

            if request.parent_id:
                # Get parent category to determine level and path
                parent_result = await session.execute(
                    select(TransactionCategory).where(TransactionCategory.id == request.parent_id)
                )
                parent = parent_result.scalar_one_or_none()

                if not parent:
                    raise HTTPException(
                        status_code=400,
                        detail="Parent category not found"
                    )

                level = parent.level + 1
                path = f"{parent.path}/{request.name}"

            # Create category instance
            category = TransactionCategory(
                id=category_id,
                user_id=request.user_id,
                group_id=request.group_id,
                name=request.name,
                description=request.description,
                color=request.color,
                icon=request.icon,
                parent_id=request.parent_id,
                level=level,
                path=path,
                is_income=request.is_income,
                is_expense=request.is_expense,
                budget_amount=request.budget_amount,
                budget_period=request.budget_period,
                is_active=request.is_active,
                sort_order=request.sort_order
            )

            # Add to database
            session.add(category)
            await session.commit()
            await session.refresh(category)

            logger.info(f"Created category {category_id} for user {request.user_id}")
            return self._category_to_response(category)

        except IntegrityError as e:
            await session.rollback()
            logger.error(f"Integrity error creating category: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail="Category creation failed due to data constraint violation"
            )
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating category: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to create category"
            )

    async def get_category_by_id(self, session: AsyncSession, category_id: str) -> Optional[TransactionCategoryResponse]:
        """
        Get category by ID

        Args:
            session: Database session
            category_id: Category ID

        Returns:
            Category response or None if not found
        """
        try:
            result = await session.execute(
                select(UserCategory).where(UserCategory.id == category_id)
            )
            category = result.scalar_one_or_none()

            if not category:
                return None

            return self._category_to_response(category)

        except Exception as e:
            logger.error(f"Error retrieving category {category_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve category"
            )

    async def update_category(
        self,
        session: AsyncSession,
        category_id: str,
        request: TransactionCategoryUpdate
    ) -> Optional[TransactionCategoryResponse]:
        """
        Update an existing category

        Args:
            session: Database session
            category_id: Category ID
            request: Update request

        Returns:
            Updated category response or None if not found
        """
        try:
            # Get existing category
            result = await session.execute(
                select(UserCategory).where(UserCategory.id == category_id)
            )
            category = result.scalar_one_or_none()

            if not category:
                return None

            # Update fields
            update_data = request.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(category, field):
                    setattr(category, field, value)

            # Update path if name changed and has parent
            if "name" in update_data and category.parent_id:
                parent_result = await session.execute(
                    select(UserCategory).where(UserCategory.id == category.parent_id)
                )
                parent = parent_result.scalar_one_or_none()
                if parent:
                    category.path = f"{parent.path}/{category.name}"

            # Update child paths if name changed
            if "name" in update_data:
                await self._update_child_paths(session, category_id, category.path)

            # Update metadata
            category.updated_at = datetime.utcnow()

            await session.commit()
            await session.refresh(category)

            logger.info(f"Updated category {category_id}")
            return self._category_to_response(category)

        except Exception as e:
            await session.rollback()
            logger.error(f"Error updating category {category_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to update category"
            )

    async def delete_category(self, session: AsyncSession, category_id: str, reassign_to: Optional[str] = None) -> bool:
        """
        Delete a category and optionally reassign transactions

        Args:
            session: Database session
            category_id: Category ID
            reassign_to: Category ID to reassign transactions to

        Returns:
            True if category was deleted, False if not found
        """
        try:
            # Get existing category
            result = await session.execute(
                select(UserCategory).where(UserCategory.id == category_id)
            )
            category = result.scalar_one_or_none()

            if not category:
                return False

            # Reassign transactions if requested
            if reassign_to:
                await session.execute(
                    Transaction.__table__.update().where(
                        Transaction.user_category_id == category_id
                    ).values(user_category_id=reassign_to)
                )

            # Delete category (cascade will handle children)
            await session.delete(category)
            await session.commit()

            logger.info(f"Deleted category {category_id}")
            return True

        except Exception as e:
            await session.rollback()
            logger.error(f"Error deleting category {category_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to delete category"
            )

    async def list_categories(
        self,
        session: AsyncSession,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = False
    ) -> Tuple[List[TransactionCategoryResponse], int]:
        """
        List categories for a user

        Args:
            session: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_inactive: Whether to include inactive categories

        Returns:
            Tuple of (categories list, total count)
        """
        try:
            # Base query
            query = select(UserCategory).where(UserCategory.user_id == user_id)
            count_query = select(func.count()).select_from(UserCategory).where(UserCategory.user_id == user_id)

            # Filter active categories
            if not include_inactive:
                query = query.where(UserCategory.is_active == True)
                count_query = count_query.where(UserCategory.is_active == True)

            # Order by sort_order, then by name
            query = query.order_by(UserCategory.sort_order, UserCategory.name)

            # Get total count
            count_result = await session.execute(count_query)
            total = count_result.scalar() or 0

            # Apply pagination and get results
            paginated_query = query.offset(skip).limit(limit)
            result = await session.execute(paginated_query)
            categories = result.scalars().all()

            return [self._category_to_response(category) for category in categories], total

        except Exception as e:
            logger.error(f"Error listing categories for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve categories"
            )

    async def get_category_tree(self, session: AsyncSession, user_id: str) -> List[TransactionCategoryTreeResponse]:
        """
        Get hierarchical category tree for a user

        Args:
            session: Database session
            user_id: User ID

        Returns:
            List of root categories with their children
        """
        try:
            # Get all categories for user
            result = await session.execute(
                select(UserCategory).where(
                    UserCategory.user_id == user_id,
                    UserCategory.is_active == True
                ).order_by(UserCategory.sort_order, UserCategory.name)
            )
            categories = result.scalars().all()

            # Build tree structure
            category_map = {cat.id: cat for cat in categories}
            root_categories = []

            for category in categories:
                if category.parent_id is None:
                    # Root category
                    root_categories.append(self._build_category_tree(category, category_map))
                # Non-root categories will be added as children of their parents

            return root_categories

        except Exception as e:
            logger.error(f"Error getting category tree for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to get category tree"
            )

    async def move_category(
        self,
        session: AsyncSession,
        category_id: str,
        new_parent_id: Optional[str],
        sort_order: Optional[int] = None
    ) -> Optional[TransactionCategoryResponse]:
        """
        Move a category to a new parent

        Args:
            session: Database session
            category_id: Category ID to move
            new_parent_id: New parent category ID (None for root)
            sort_order: New sort order

        Returns:
            Updated category response or None if not found
        """
        try:
            # Get category to move
            result = await session.execute(
                select(UserCategory).where(UserCategory.id == category_id)
            )
            category = result.scalar_one_or_none()

            if not category:
                return None

            # Validate new parent
            if new_parent_id:
                parent_result = await session.execute(
                    select(UserCategory).where(UserCategory.id == new_parent_id)
                )
                parent = parent_result.scalar_one_or_none()

                if not parent:
                    raise HTTPException(
                        status_code=400,
                        detail="Parent category not found"
                    )

                # Prevent circular references
                if parent.parent_id == category_id:
                    raise HTTPException(
                        status_code=400,
                        detail="Cannot move category to its own child"
                    )

                # Update level and path
                category.parent_id = new_parent_id
                category.level = parent.level + 1
                category.path = f"{parent.path}/{category.name}"
            else:
                # Move to root
                category.parent_id = None
                category.level = 1
                category.path = category.name

            # Update sort order
            if sort_order is not None:
                category.sort_order = sort_order

            # Update child paths
            await self._update_child_paths(session, category_id, category.path)

            # Update metadata
            category.updated_at = datetime.utcnow()

            await session.commit()
            await session.refresh(category)

            logger.info(f"Moved category {category_id} to parent {new_parent_id}")
            return self._category_to_response(category)

        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            logger.error(f"Error moving category {category_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to move category"
            )

    async def _update_child_paths(self, session: AsyncSession, parent_id: str, parent_path: str):
        """Update paths of all child categories"""
        try:
            # Get all child categories
            result = await session.execute(
                select(UserCategory).where(UserCategory.parent_id == parent_id)
            )
            children = result.scalars().all()

            for child in children:
                child.path = f"{parent_path}/{child.name}"
                child.level = len(child.path.split("/"))
                # Recursively update grandchildren
                await self._update_child_paths(session, child.id, child.path)

        except Exception as e:
            logger.warning(f"Error updating child paths for {parent_id}: {str(e)}")

    def _build_category_tree(self, category: TransactionCategory, category_map: Dict[str, TransactionCategory]) -> TransactionCategoryTreeResponse:
        """Build tree structure for a category"""
        children = []
        for cat_id, cat in category_map.items():
            if cat.parent_id == category.id:
                children.append(self._build_category_tree(cat, category_map))

        return TransactionCategoryTreeResponse(
            category=self._category_to_response(category),
            children=children
        )

    def _category_to_response(self, category: TransactionCategory) -> TransactionCategoryResponse:
        """Convert UserCategory model to UserCategoryResponse schema"""
        return TransactionCategoryResponse(
            id=category.id or "",
            user_id=category.user_id,
            group_id=category.group_id,
            name=category.name,
            description=category.description,
            color=category.color,
            icon=category.icon,
            parent_id=category.parent_id,
            level=category.level,
            path=category.path,
            is_income=category.is_income,
            is_expense=category.is_expense,
            budget_amount=category.budget_amount,
            budget_period=category.budget_period,
            is_active=category.is_active,
            sort_order=category.sort_order,
            transaction_count=category.transaction_count,
            total_amount=category.total_amount,
            created_at=category.created_at,
            updated_at=category.updated_at,
            is_root=category.is_root,
            is_leaf=category.is_leaf,
            full_path_list=category.full_path_list,
            depth=category.depth
        )


class CategoryRuleService:
    """Service class for category rule operations"""

    def __init__(self):
        """Initialize the category rule service"""
        pass

    async def create_rule(self, session: AsyncSession, request: CategoryRuleCreate) -> CategoryRuleResponse:
        """
        Create a new category rule

        Args:
            session: Database session
            request: Rule creation request

        Returns:
            Created rule response

        Raises:
            HTTPException: If rule creation fails
        """
        try:
            # Generate unique ID
            rule_id = generate_id()

            # Validate category exists
            category_result = await session.execute(
                select(UserCategory).where(UserCategory.id == request.category_id)
            )
            category = category_result.scalar_one_or_none()

            if not category:
                raise HTTPException(
                    status_code=400,
                    detail="Target category not found"
                )

            # Create rule instance
            rule = CategoryRule(
                id=rule_id,
                user_id=request.user_id,
                category_id=request.category_id,
                name=request.name,
                description=request.description,
                merchant_name_pattern=request.merchant_name_pattern,
                transaction_name_pattern=request.transaction_name_pattern,
                description_pattern=request.description_pattern,
                amount_min=request.amount_min,
                amount_max=request.amount_max,
                transaction_type=request.transaction_type,
                is_active=request.is_active,
                priority=request.priority,
                confidence_threshold=request.confidence_threshold
            )

            # Add to database
            session.add(rule)
            await session.commit()
            await session.refresh(rule)

            logger.info(f"Created rule {rule_id} for user {request.user_id}")
            return self._rule_to_response(rule)

        except IntegrityError as e:
            await session.rollback()
            logger.error(f"Integrity error creating rule: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail="Rule creation failed due to data constraint violation"
            )
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating rule: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to create rule"
            )

    async def get_rule_by_id(self, session: AsyncSession, rule_id: str) -> Optional[CategoryRuleResponse]:
        """
        Get rule by ID

        Args:
            session: Database session
            rule_id: Rule ID

        Returns:
            Rule response or None if not found
        """
        try:
            result = await session.execute(
                select(CategoryRule).where(CategoryRule.id == rule_id)
            )
            rule = result.scalar_one_or_none()

            if not rule:
                return None

            return self._rule_to_response(rule)

        except Exception as e:
            logger.error(f"Error retrieving rule {rule_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve rule"
            )

    async def update_rule(
        self,
        session: AsyncSession,
        rule_id: str,
        request: CategoryRuleUpdate
    ) -> Optional[CategoryRuleResponse]:
        """
        Update an existing rule

        Args:
            session: Database session
            rule_id: Rule ID
            request: Update request

        Returns:
            Updated rule response or None if not found
        """
        try:
            # Get existing rule
            result = await session.execute(
                select(CategoryRule).where(CategoryRule.id == rule_id)
            )
            rule = result.scalar_one_or_none()

            if not rule:
                return None

            # Validate category if being updated
            if "category_id" in request.model_dump(exclude_unset=True):
                category_result = await session.execute(
                    select(UserCategory).where(UserCategory.id == request.category_id)
                )
                category = category_result.scalar_one_or_none()

                if not category:
                    raise HTTPException(
                        status_code=400,
                        detail="Target category not found"
                    )

            # Update fields
            update_data = request.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(rule, field):
                    setattr(rule, field, value)

            # Update metadata
            rule.updated_at = datetime.utcnow()

            await session.commit()
            await session.refresh(rule)

            logger.info(f"Updated rule {rule_id}")
            return self._rule_to_response(rule)

        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            logger.error(f"Error updating rule {rule_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to update rule"
            )

    async def delete_rule(self, session: AsyncSession, rule_id: str) -> bool:
        """
        Delete a rule

        Args:
            session: Database session
            rule_id: Rule ID

        Returns:
            True if rule was deleted, False if not found
        """
        try:
            # Get existing rule
            result = await session.execute(
                select(CategoryRule).where(CategoryRule.id == rule_id)
            )
            rule = result.scalar_one_or_none()

            if not rule:
                return False

            # Delete rule
            await session.delete(rule)
            await session.commit()

            logger.info(f"Deleted rule {rule_id}")
            return True

        except Exception as e:
            await session.rollback()
            logger.error(f"Error deleting rule {rule_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to delete rule"
            )

    async def list_rules(
        self,
        session: AsyncSession,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = False
    ) -> Tuple[List[CategoryRuleResponse], int]:
        """
        List rules for a user

        Args:
            session: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_inactive: Whether to include inactive rules

        Returns:
            Tuple of (rules list, total count)
        """
        try:
            # Base query
            query = select(CategoryRule).where(CategoryRule.user_id == user_id)
            count_query = select(func.count()).select_from(CategoryRule).where(CategoryRule.user_id == user_id)

            # Filter active rules
            if not include_inactive:
                query = query.where(CategoryRule.is_active == True)
                count_query = count_query.where(CategoryRule.is_active == True)

            # Order by priority, then by name
            query = query.order_by(CategoryRule.priority.desc(), CategoryRule.name)

            # Get total count
            count_result = await session.execute(count_query)
            total = count_result.scalar() or 0

            # Apply pagination and get results
            paginated_query = query.offset(skip).limit(limit)
            result = await session.execute(paginated_query)
            rules = result.scalars().all()

            return [self._rule_to_response(rule) for rule in rules], total

        except Exception as e:
            logger.error(f"Error listing rules for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve rules"
            )

    async def test_rule(
        self,
        session: AsyncSession,
        rule_id: str,
        transaction_ids: List[str]
    ) -> CategoryRuleTestResponse:
        """
        Test a rule against specific transactions

        Args:
            session: Database session
            rule_id: Rule ID
            transaction_ids: List of transaction IDs to test

        Returns:
            Test response with matches
        """
        try:
            # Get rule
            rule_result = await session.execute(
                select(CategoryRule).where(CategoryRule.id == rule_id)
            )
            rule = rule_result.scalar_one_or_none()

            if not rule:
                raise HTTPException(
                    status_code=404,
                    detail="Rule not found"
                )

            # Get transactions
            transaction_result = await session.execute(
                select(Transaction).where(Transaction.id.in_(transaction_ids))
            )
            transactions = transaction_result.scalars().all()

            # Test rule against transactions
            matches = []
            for transaction in transactions:
                if self._rule_matches_transaction(rule, transaction):
                    matches.append(transaction.id)

            return CategoryRuleTestResponse(
                rule_id=rule_id,
                rule_name=rule.name,
                matches=matches,
                match_count=len(matches),
                would_apply=len(matches) > 0 and rule.is_active
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error testing rule {rule_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to test rule"
            )

    async def apply_rules_to_transaction(
        self,
        session: AsyncSession,
        transaction_id: str,
        user_id: str
    ) -> Optional[str]:
        """
        Apply active rules to a transaction

        Args:
            session: Database session
            transaction_id: Transaction ID
            user_id: User ID

        Returns:
            Category ID if rule was applied, None otherwise
        """
        try:
            # Get transaction
            transaction_result = await session.execute(
                select(Transaction).where(Transaction.id == transaction_id)
            )
            transaction = transaction_result.scalar_one_or_none()

            if not transaction:
                return None

            # Get active rules for user, ordered by priority
            rules_result = await session.execute(
                select(CategoryRule).where(
                    CategoryRule.user_id == user_id,
                    CategoryRule.is_active == True
                ).order_by(CategoryRule.priority.desc())
            )
            rules = rules_result.scalars().all()

            # Test each rule
            for rule in rules:
                if self._rule_matches_transaction(rule, transaction):
                    # Apply rule
                    transaction.user_category_id = rule.category_id
                    transaction.updated_at = datetime.utcnow()

                    # Update rule usage stats
                    rule.match_count += 1
                    rule.last_matched = datetime.utcnow()

                    await session.commit()

                    logger.info(f"Applied rule {rule.id} to transaction {transaction_id}")
                    return rule.category_id

            return None

        except Exception as e:
            await session.rollback()
            logger.error(f"Error applying rules to transaction {transaction_id}: {str(e)}")
            return None

    def _rule_matches_transaction(self, rule: CategoryRule, transaction: Transaction) -> bool:
        """Check if a rule matches a transaction"""
        try:
            import re

            # Check merchant name pattern
            if rule.merchant_name_pattern:
                if not transaction.merchant_name:
                    return False
                if not re.search(rule.merchant_name_pattern, transaction.merchant_name, re.IGNORECASE):
                    return False

            # Check transaction name pattern
            if rule.transaction_name_pattern:
                if not re.search(rule.transaction_name_pattern, transaction.name, re.IGNORECASE):
                    return False

            # Check description pattern
            if rule.description_pattern:
                if not transaction.description:
                    return False
                if not re.search(rule.description_pattern, transaction.description, re.IGNORECASE):
                    return False

            # Check amount range
            if rule.amount_min is not None and transaction.amount < rule.amount_min:
                return False
            if rule.amount_max is not None and transaction.amount > rule.amount_max:
                return False

            # Check transaction type
            if rule.transaction_type and transaction.transaction_type != rule.transaction_type:
                return False

            return True

        except Exception as e:
            logger.warning(f"Error matching rule {rule.id} against transaction {transaction.id}: {str(e)}")
            return False

    def _rule_to_response(self, rule: CategoryRule) -> CategoryRuleResponse:
        """Convert CategoryRule model to CategoryRuleResponse schema"""
        return CategoryRuleResponse(
            id=rule.id or "",
            user_id=rule.user_id,
            category_id=rule.category_id,
            name=rule.name,
            description=rule.description,
            merchant_name_pattern=rule.merchant_name_pattern,
            transaction_name_pattern=rule.transaction_name_pattern,
            description_pattern=rule.description_pattern,
            amount_min=rule.amount_min,
            amount_max=rule.amount_max,
            transaction_type=rule.transaction_type,
            is_active=rule.is_active,
            priority=rule.priority,
            confidence_threshold=rule.confidence_threshold,
            match_count=rule.match_count,
            last_matched=rule.last_matched,
            created_at=rule.created_at,
            updated_at=rule.updated_at
        )


# Global service instances
transaction_category_service = TransactionCategoryService()
category_rule_service = CategoryRuleService()
