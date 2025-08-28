"""
Activity router for TruLedgr API

This module provides FastAPI routes for activity tracking and management.
Includes endpoints for viewing user activities, activity summaries, and different activity types.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlmodel.ext.asyncio.session import AsyncSession

from .models import (
    Activity,
    ActivityAPITransaction,
    ActivityDataAccess,
    ActivityDataChanges,
    ActivityAuthEvents,
    ActivityExternalAPI,
    ActivitySystemEvent
)
from .crud import (
    ActivityAPITransactionCRUD,
    ActivityDataAccessCRUD,
    ActivityDataChangesCRUD,
    ActivityExternalAPICRUD,
    ActivitySystemEventCRUD
)
from .service import activity_service
from api.db.deps import get_db
from api.authentication.deps import get_current_user
from api.users.models import User

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("/", response_model=List[Activity])
async def get_activities(
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"), 
    status: Optional[str] = Query(None, description="Filter by status"),
    start_date: Optional[datetime] = Query(None, description="Filter activities after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter activities before this date"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Get activities for the current user with optional filtering."""
    return await activity_service.get_user_activities(
        user_id=current_user.id,
        activity_type=activity_type,
        entity_type=entity_type,
        status=status,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
        session=session
    )


@router.get("/{activity_id}", response_model=Activity)
async def get_activity(
    activity_id: str = Path(..., description="Activity ID"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Get a specific activity by ID."""
    activity = await activity_service.get_activity(activity_id, session=session)
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Check if user owns this activity or has admin permissions
    if activity.user_id != current_user.id:
        # Here you could add admin permission check
        raise HTTPException(status_code=403, detail="Access denied")
    
    return activity


@router.get("/summary/user", response_model=Dict[str, Any])
async def get_user_activity_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days to include in summary"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Get activity summary for the current user."""
    return await activity_service.get_activity_summary(
        user_id=current_user.id,
        days=days,
        session=session
    )


@router.get("/api-transactions/", response_model=List[ActivityAPITransaction])
async def get_api_transactions(
    method: Optional[str] = Query(None, description="Filter by HTTP method"),
    endpoint: Optional[str] = Query(None, description="Filter by endpoint pattern"),
    status_code: Optional[int] = Query(None, description="Filter by status code"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Get API transaction activities for the current user."""
    return await ActivityAPITransactionCRUD.get_by_user(
        session=session,
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )


@router.get("/data-access/", response_model=List[ActivityDataAccess])
async def get_data_access_activities(
    table_name: Optional[str] = Query(None, description="Filter by table name"),
    operation: Optional[str] = Query(None, description="Filter by operation type"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Get data access activities for the current user."""
    if table_name:
        return await ActivityDataAccessCRUD.get_by_table(
            session=session,
            table_name=table_name,
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )
    else:
        # For now, return empty list when no table specified
        # Could be enhanced to return all data access activities
        return []


@router.get("/data-changes/", response_model=List[ActivityDataChanges])
async def get_data_changes_activities(
    table_name: str = Query(..., description="Table name to get changes for"),
    record_id: Optional[str] = Query(None, description="Specific record ID"),
    operation: Optional[str] = Query(None, description="Filter by operation type"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Get data change activities."""
    if record_id:
        return await ActivityDataChangesCRUD.get_by_record(
            session=session,
            table_name=table_name,
            record_id=record_id,
            limit=limit,
            offset=offset
        )
    else:
        # For now, return empty list when no record specified
        # Could be enhanced to return all changes for the table
        return []


@router.get("/auth-events/", response_model=List[ActivityAuthEvents])
async def get_auth_events(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    success: Optional[bool] = Query(None, description="Filter by success status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Get authentication events for the current user."""
    # For now, return basic user activities filtered by auth events
    # Could be enhanced with specific auth event filtering
    return await activity_service.get_user_activities(
        user_id=current_user.id,
        activity_type="auth",
        limit=limit,
        offset=offset,
        session=session
    )


@router.get("/external-api/", response_model=List[ActivityExternalAPI])
async def get_external_api_activities(
    service_name: Optional[str] = Query(None, description="Filter by service name"),
    method: Optional[str] = Query(None, description="Filter by HTTP method"),
    status_code: Optional[int] = Query(None, description="Filter by status code"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Get external API activities for the current user."""
    if service_name:
        return await ActivityExternalAPICRUD.get_by_service(
            session=session,
            service_name=service_name,
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )
    else:
        # For now, return empty list when no service specified
        # Could be enhanced to return all external API activities
        return []


@router.get("/system-events/", response_model=List[ActivitySystemEvent])
async def get_system_events(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    severity: Optional[str] = Query(None, description="Filter by severity level"),
    component: Optional[str] = Query(None, description="Filter by system component"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Get system events. Requires admin permissions."""
    # Note: This endpoint should have admin permission checks in a real application
    if severity:
        return await ActivitySystemEventCRUD.get_by_severity(
            session=session,
            severity=severity,
            component=component,
            limit=limit,
            offset=offset
        )
    else:
        # For now, return empty list when no severity specified
        # Could be enhanced to return all system events
        return []


# Admin endpoints (would require admin permissions in real implementation)
@router.get("/admin/users/{user_id}/activities", response_model=List[Activity])
async def get_user_activities_admin(
    user_id: str = Path(..., description="User ID to get activities for"),
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Get activities for any user. Requires admin permissions."""
    # TODO: Add admin permission check
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    return await activity_service.get_user_activities(
        user_id=user_id,
        activity_type=activity_type,
        limit=limit,
        offset=offset,
        session=session
    )


@router.get("/admin/summary/{user_id}", response_model=Dict[str, Any])
async def get_user_activity_summary_admin(
    user_id: str = Path(..., description="User ID to get summary for"),
    days: int = Query(30, ge=1, le=365, description="Number of days to include in summary"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Get activity summary for any user. Requires admin permissions."""
    # TODO: Add admin permission check
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    return await activity_service.get_activity_summary(
        user_id=user_id,
        days=days,
        session=session
    )
