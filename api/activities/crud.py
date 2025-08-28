"""
Activity CRUD operations for TruLedgr API

This module provides Create, Read, Update, Delete operations for the activity tracking system.
Includes operations for activities, API transactions, data access/changes, auth events, and external APIs.
"""

from typing import Optional, List, Dict, Any
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, and_, desc, func, or_, col
from datetime import datetime, timedelta

from .models import (
    Activity,
    ActivityAPITransaction, 
    ActivityDataAccess,
    ActivityDataChanges,
    ActivityAuthEvents,
    ActivityExternalAPI,
    ActivitySystemEvent
)


class ActivityCRUD:
    """CRUD operations for Activity model"""

    @staticmethod
    async def create(session: AsyncSession, activity: Activity) -> Activity:
        """Create a new activity record"""
        try:
            session.add(activity)
            await session.commit()
            await session.refresh(activity)
            return activity
        except Exception:
            await session.rollback()
            raise

    @staticmethod
    async def get_by_id(session: AsyncSession, activity_id: str) -> Optional[Activity]:
        """Get activity by ID"""
        statement = select(Activity).where(Activity.id == activity_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_multiple(
        session: AsyncSession,
        filters: Optional[Dict[str, Any]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Activity]:
        """Get multiple activities with filtering"""
        statement = select(Activity)
        
        # Apply filters
        conditions = []
        if filters:
            for key, value in filters.items():
                if hasattr(Activity, key):
                    conditions.append(getattr(Activity, key) == value)
        
        if start_date:
            conditions.append(Activity.created_at >= start_date)
        if end_date:
            conditions.append(Activity.created_at <= end_date)
        
        if conditions:
            statement = statement.where(and_(*conditions))
        
        statement = statement.order_by(desc(Activity.created_at)).offset(offset).limit(limit)
        
        result = await session.execute(statement)
        return list(result.scalars().all())


class ActivityAPITransactionCRUD:
    """CRUD operations for ActivityAPITransaction model"""

    @staticmethod
    async def create(session: AsyncSession, api_transaction: ActivityAPITransaction) -> ActivityAPITransaction:
        """Create a new API transaction record"""
        try:
            session.add(api_transaction)
            await session.commit()
            await session.refresh(api_transaction)
            return api_transaction
        except Exception:
            await session.rollback()
            raise

    @staticmethod
    async def get_by_id(session: AsyncSession, transaction_id: str) -> Optional[ActivityAPITransaction]:
        """Get API transaction by ID"""
        statement = select(ActivityAPITransaction).where(ActivityAPITransaction.id == transaction_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_user(
        session: AsyncSession,
        user_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[ActivityAPITransaction]:
        """Get API transactions for a user"""
        statement = (
            select(ActivityAPITransaction)
            .where(ActivityAPITransaction.user_id == user_id)
            .order_by(desc(ActivityAPITransaction.created_at))
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(statement)
        return list(result.scalars().all())


class ActivityDataAccessCRUD:
    """CRUD operations for ActivityDataAccess model"""

    @staticmethod
    async def create(session: AsyncSession, data_access: ActivityDataAccess) -> ActivityDataAccess:
        """Create a new data access record"""
        try:
            session.add(data_access)
            await session.commit()
            await session.refresh(data_access)
            return data_access
        except Exception:
            await session.rollback()
            raise

    @staticmethod
    async def get_by_id(session: AsyncSession, access_id: str) -> Optional[ActivityDataAccess]:
        """Get data access by ID"""
        statement = select(ActivityDataAccess).where(ActivityDataAccess.id == access_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_table(
        session: AsyncSession,
        table_name: str,
        user_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ActivityDataAccess]:
        """Get data access records for a table"""
        conditions = [ActivityDataAccess.table_name == table_name]
        if user_id:
            conditions.append(ActivityDataAccess.user_id == user_id)
        
        statement = (
            select(ActivityDataAccess)
            .where(and_(*conditions))
            .order_by(desc(ActivityDataAccess.created_at))
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(statement)
        return list(result.scalars().all())


class ActivityDataChangesCRUD:
    """CRUD operations for ActivityDataChanges model"""

    @staticmethod
    async def create(session: AsyncSession, data_changes: ActivityDataChanges) -> ActivityDataChanges:
        """Create a new data changes record"""
        try:
            session.add(data_changes)
            await session.commit()
            await session.refresh(data_changes)
            return data_changes
        except Exception:
            await session.rollback()
            raise

    @staticmethod
    async def get_by_id(session: AsyncSession, changes_id: str) -> Optional[ActivityDataChanges]:
        """Get data changes by ID"""
        statement = select(ActivityDataChanges).where(ActivityDataChanges.id == changes_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_record(
        session: AsyncSession,
        table_name: str,
        record_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[ActivityDataChanges]:
        """Get data changes for a specific record"""
        statement = (
            select(ActivityDataChanges)
            .where(
                and_(
                    ActivityDataChanges.table_name == table_name,
                    ActivityDataChanges.record_id == record_id
                )
            )
            .order_by(desc(ActivityDataChanges.created_at))
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(statement)
        return list(result.scalars().all())


class ActivityAuthEventsCRUD:
    """CRUD operations for ActivityAuthEvents model"""

    @staticmethod
    async def create(session: AsyncSession, auth_event: ActivityAuthEvents) -> ActivityAuthEvents:
        """Create a new auth event record"""
        try:
            session.add(auth_event)
            await session.commit()
            await session.refresh(auth_event)
            return auth_event
        except Exception:
            await session.rollback()
            raise

    @staticmethod
    async def get_by_id(session: AsyncSession, event_id: str) -> Optional[ActivityAuthEvents]:
        """Get auth event by ID"""
        statement = select(ActivityAuthEvents).where(ActivityAuthEvents.id == event_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_failed_attempts(
        session: AsyncSession,
        ip_address: Optional[str] = None,
        user_id: Optional[str] = None,
        hours: int = 24
    ) -> List[ActivityAuthEvents]:
        """Get failed authentication attempts"""
        since = datetime.utcnow() - timedelta(hours=hours)
        conditions = [
            ActivityAuthEvents.success == False,
            ActivityAuthEvents.created_at >= since
        ]
        
        if ip_address:
            conditions.append(ActivityAuthEvents.ip_address == ip_address)
        if user_id:
            conditions.append(ActivityAuthEvents.user_id == user_id)
        
        statement = (
            select(ActivityAuthEvents)
            .where(and_(*conditions))
            .order_by(desc(ActivityAuthEvents.created_at))
        )
        result = await session.execute(statement)
        return list(result.scalars().all())


class ActivityExternalAPICRUD:
    """CRUD operations for ActivityExternalAPI model"""

    @staticmethod
    async def create(session: AsyncSession, external_api: ActivityExternalAPI) -> ActivityExternalAPI:
        """Create a new external API record"""
        try:
            session.add(external_api)
            await session.commit()
            await session.refresh(external_api)
            return external_api
        except Exception:
            await session.rollback()
            raise

    @staticmethod
    async def get_by_id(session: AsyncSession, api_id: str) -> Optional[ActivityExternalAPI]:
        """Get external API by ID"""
        statement = select(ActivityExternalAPI).where(ActivityExternalAPI.id == api_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_service(
        session: AsyncSession,
        service_name: str,
        user_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ActivityExternalAPI]:
        """Get external API calls for a service"""
        conditions = [ActivityExternalAPI.service_name == service_name]
        if user_id:
            conditions.append(ActivityExternalAPI.user_id == user_id)
        
        statement = (
            select(ActivityExternalAPI)
            .where(and_(*conditions))
            .order_by(desc(ActivityExternalAPI.created_at))
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(statement)
        return list(result.scalars().all())


class ActivitySystemEventCRUD:
    """CRUD operations for ActivitySystemEvent model"""

    @staticmethod
    async def create(session: AsyncSession, system_event: ActivitySystemEvent) -> ActivitySystemEvent:
        """Create a new system event record"""
        try:
            session.add(system_event)
            await session.commit()
            await session.refresh(system_event)
            return system_event
        except Exception:
            await session.rollback()
            raise

    @staticmethod
    async def get_by_id(session: AsyncSession, event_id: str) -> Optional[ActivitySystemEvent]:
        """Get system event by ID"""
        statement = select(ActivitySystemEvent).where(ActivitySystemEvent.id == event_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_severity(
        session: AsyncSession,
        severity: str,
        component: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ActivitySystemEvent]:
        """Get system events by severity"""
        conditions = [ActivitySystemEvent.severity == severity]
        if component:
            conditions.append(ActivitySystemEvent.component == component)
        
        statement = (
            select(ActivitySystemEvent)
            .where(and_(*conditions))
            .order_by(desc(ActivitySystemEvent.created_at))
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(statement)
        return list(result.scalars().all())


class ActivityCompositeCRUD:
    """Composite CRUD operations across multiple activity types"""

    @staticmethod
    async def get_user_activity_summary(
        session: AsyncSession,
        user_id: str,
        start_date: datetime
    ) -> Dict[str, Any]:
        """Get activity summary for a user"""
        # Count activities by type
        activity_counts = await session.execute(
            select(Activity.activity_type, func.count(Activity.id))
            .where(
                and_(
                    Activity.user_id == user_id,
                    Activity.created_at >= start_date
                )
            )
            .group_by(Activity.activity_type)
        )
        
        # Count API transactions
        api_count = await session.execute(
            select(func.count(ActivityAPITransaction.id))
            .where(
                and_(
                    ActivityAPITransaction.user_id == user_id,
                    ActivityAPITransaction.created_at >= start_date
                )
            )
        )
        
        # Count data access events
        data_access_count = await session.execute(
            select(func.count(ActivityDataAccess.id))
            .where(
                and_(
                    ActivityDataAccess.user_id == user_id,
                    ActivityDataAccess.created_at >= start_date
                )
            )
        )
        
        return {
            "user_id": user_id,
            "period_start": start_date,
            "activity_counts": dict(activity_counts.all()),
            "api_transaction_count": api_count.scalar(),
            "data_access_count": data_access_count.scalar(),
        }
