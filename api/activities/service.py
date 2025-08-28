"""
Activity service for TruLedgr API

This module provides business logic for the activity tracking system.
Handles creation and management of activities, API transactions, data changes,
authentication events, and external API tracking.
"""

import logging
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Request, HTTPException

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
    ActivityCRUD,
    ActivityAPITransactionCRUD,
    ActivityDataAccessCRUD,
    ActivityDataChangesCRUD,
    ActivityAuthEventsCRUD,
    ActivityExternalAPICRUD,
    ActivitySystemEventCRUD,
    ActivityCompositeCRUD
)
from api.db.session import get_async_session
from api.common.utils import generate_id

logger = logging.getLogger(__name__)


class ActivityService:
    """Service class for activity tracking operations"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    # Core Activity Management

    async def create_activity(
        self,
        activity_type: str,
        user_id: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        description: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status: str = "completed",
        tags: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
        session: Optional[AsyncSession] = None,
    ) -> Activity:
        """Create a new activity record.
        
        Args:
            activity_type: Type of activity (e.g., 'login', 'data_access', 'api_call')
            user_id: ID of the user performing the activity
            entity_type: Optional type of entity being acted upon
            entity_id: Optional ID of specific entity
            description: Human-readable description
            details: Additional structured data
            status: Activity status ('pending', 'completed', 'failed', 'cancelled')
            tags: Optional list of tags for categorization
            context: Additional context data
            session: Database session
            
        Returns:
            Created Activity instance
        """
        activity_data = {
            "activity_type": activity_type,
            "user_id": user_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "description": description,
            "details": details or {},
            "status": status,
            "tags": tags or [],
            "context": context or {},
        }
        
        activity = Activity(**activity_data)
        
        if session:
            return await ActivityCRUD.create(session, activity)
        else:
            async for db_session in get_async_session():
                return await ActivityCRUD.create(db_session, activity)

    async def get_activity(self, activity_id: str, session: Optional[AsyncSession] = None) -> Optional[Activity]:
        """Get an activity by ID.
        
        Args:
            activity_id: The activity ID
            session: Database session
            
        Returns:
            Activity instance or None if not found
        """
        if session:
            return await ActivityCRUD.get_by_id(session, activity_id)
        else:
            async for db_session in get_async_session():
                return await ActivityCRUD.get_by_id(db_session, activity_id)

    async def get_user_activities(
        self,
        user_id: str,
        activity_type: Optional[str] = None,
        entity_type: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
        session: Optional[AsyncSession] = None
    ) -> List[Activity]:
        """Get activities for a specific user with filtering.
        
        Args:
            user_id: The user ID to filter by
            activity_type: Optional activity type filter
            entity_type: Optional entity type filter
            status: Optional status filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum number of results
            offset: Number of results to skip
            session: Database session
            
        Returns:
            List of Activity instances
        """
        filters = {"user_id": user_id}
        if activity_type:
            filters["activity_type"] = activity_type
        if entity_type:
            filters["entity_type"] = entity_type
        if status:
            filters["status"] = status
        
        if session:
            return await ActivityCRUD.get_multiple(
                session,
                filters=filters,
                start_date=start_date,
                end_date=end_date,
                limit=limit,
                offset=offset
            )
        else:
            async for db_session in get_async_session():
                return await ActivityCRUD.get_multiple(
                    db_session,
                    filters=filters,
                    start_date=start_date,
                    end_date=end_date,
                    limit=limit,
                    offset=offset
                )

    # API Transaction Tracking

    async def log_api_transaction(
        self,
        user_id: str,
        method: str,
        endpoint: str,
        status_code: int,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        execution_time_ms: Optional[int] = None,
        request_headers: Optional[Dict[str, str]] = None,
        response_headers: Optional[Dict[str, str]] = None,
        error_details: Optional[Dict[str, Any]] = None,
        session: Optional[AsyncSession] = None
    ) -> ActivityAPITransaction:
        """Log an API transaction activity.
        
        Args:
            user_id: ID of the user making the request
            method: HTTP method
            endpoint: API endpoint
            status_code: HTTP status code
            request_data: Request payload data
            response_data: Response data
            execution_time_ms: Request execution time in milliseconds
            request_headers: Request headers
            response_headers: Response headers
            error_details: Error information if applicable
            session: Database session
            
        Returns:
            Created ActivityAPITransaction instance
        """
        api_transaction_data = {
            "user_id": user_id,
            "method": method,
            "endpoint": endpoint,
            "status_code": status_code,
            "request_data": request_data or {},
            "response_data": response_data or {},
            "execution_time_ms": execution_time_ms,
            "request_headers": request_headers or {},
            "response_headers": response_headers or {},
            "error_details": error_details or {},
        }
        
        api_transaction = ActivityAPITransaction(**api_transaction_data)
        
        if session:
            return await ActivityAPITransactionCRUD.create(session, api_transaction)
        else:
            async for db_session in get_async_session():
                return await ActivityAPITransactionCRUD.create(db_session, api_transaction)

    # Data Access Tracking

    async def log_data_access(
        self,
        user_id: str,
        table_name: str,
        operation: str,
        record_id: Optional[str] = None,
        query_parameters: Optional[Dict[str, Any]] = None,
        fields_accessed: Optional[List[str]] = None,
        filters_applied: Optional[Dict[str, Any]] = None,
        permission_level: Optional[str] = None,
        session: Optional[AsyncSession] = None
    ) -> ActivityDataAccess:
        """Log a data access activity.
        
        Args:
            user_id: ID of the user accessing data
            table_name: Name of the table/collection accessed
            operation: Type of operation (read, list, search, etc.)
            record_id: Optional specific record ID
            query_parameters: Query parameters used
            fields_accessed: List of fields that were accessed
            filters_applied: Filters applied to the query
            permission_level: Permission level used for access
            session: Database session
            
        Returns:
            Created ActivityDataAccess instance
        """
        data_access_data = {
            "user_id": user_id,
            "table_name": table_name,
            "operation": operation,
            "record_id": record_id,
            "query_parameters": query_parameters or {},
            "fields_accessed": fields_accessed or [],
            "filters_applied": filters_applied or {},
            "permission_level": permission_level,
        }
        
        data_access = ActivityDataAccess(**data_access_data)
        
        if session:
            return await ActivityDataAccessCRUD.create(session, data_access)
        else:
            async for db_session in get_async_session():
                return await ActivityDataAccessCRUD.create(db_session, data_access)

    # Data Changes Tracking

    async def log_data_changes(
        self,
        user_id: str,
        table_name: str,
        operation: str,
        record_id: str,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        changed_fields: Optional[List[str]] = None,
        validation_errors: Optional[List[str]] = None,
        business_rules_applied: Optional[List[str]] = None,
        session: Optional[AsyncSession] = None
    ) -> ActivityDataChanges:
        """Log a data change activity.
        
        Args:
            user_id: ID of the user making changes
            table_name: Name of the table/collection changed
            operation: Type of operation (create, update, delete)
            record_id: ID of the record that was changed
            old_values: Previous values before change
            new_values: New values after change
            changed_fields: List of fields that were changed
            validation_errors: Any validation errors encountered
            business_rules_applied: Business rules that were applied
            session: Database session
            
        Returns:
            Created ActivityDataChanges instance
        """
        data_changes_data = {
            "user_id": user_id,
            "table_name": table_name,
            "operation": operation,
            "record_id": record_id,
            "old_values": old_values or {},
            "new_values": new_values or {},
            "changed_fields": changed_fields or [],
            "validation_errors": validation_errors or [],
            "business_rules_applied": business_rules_applied or [],
        }
        
        data_changes = ActivityDataChanges(**data_changes_data)
        
        if session:
            return await ActivityDataChangesCRUD.create(session, data_changes)
        else:
            async for db_session in get_async_session():
                return await ActivityDataChangesCRUD.create(db_session, data_changes)

    # Authentication Events Tracking

    async def log_auth_event(
        self,
        user_id: Optional[str],
        event_type: str,
        success: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        failure_reason: Optional[str] = None,
        two_factor_used: bool = False,
        login_method: Optional[str] = None,
        session: Optional[AsyncSession] = None
    ) -> ActivityAuthEvents:
        """Log an authentication event.
        
        Args:
            user_id: ID of the user (may be None for failed login attempts)
            event_type: Type of auth event (login, logout, token_refresh, etc.)
            success: Whether the authentication was successful
            ip_address: IP address of the request
            user_agent: User agent string
            session_id: Session ID if applicable
            failure_reason: Reason for failure if applicable
            two_factor_used: Whether two-factor authentication was used
            login_method: Method used for login (password, oauth, etc.)
            session: Database session
            
        Returns:
            Created ActivityAuthEvents instance
        """
        auth_event_data = {
            "user_id": user_id,
            "event_type": event_type,
            "success": success,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "session_id": session_id,
            "failure_reason": failure_reason,
            "two_factor_used": two_factor_used,
            "login_method": login_method,
        }
        
        auth_event = ActivityAuthEvents(**auth_event_data)
        
        if session:
            return await ActivityAuthEventsCRUD.create(session, auth_event)
        else:
            async for db_session in get_async_session():
                return await ActivityAuthEventsCRUD.create(db_session, auth_event)

    # External API Tracking

    async def log_external_api_call(
        self,
        user_id: str,
        service_name: str,
        endpoint: str,
        method: str,
        status_code: Optional[int] = None,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        execution_time_ms: Optional[int] = None,
        error_details: Optional[Dict[str, Any]] = None,
        rate_limit_info: Optional[Dict[str, Any]] = None,
        session: Optional[AsyncSession] = None
    ) -> ActivityExternalAPI:
        """Log an external API call activity.
        
        Args:
            user_id: ID of the user initiating the call
            service_name: Name of the external service
            endpoint: External API endpoint
            method: HTTP method used
            status_code: HTTP status code received
            request_data: Data sent to external API
            response_data: Data received from external API
            execution_time_ms: Execution time in milliseconds
            error_details: Error information if applicable
            rate_limit_info: Rate limiting information
            session: Database session
            
        Returns:
            Created ActivityExternalAPI instance
        """
        external_api_data = {
            "user_id": user_id,
            "service_name": service_name,
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "request_data": request_data or {},
            "response_data": response_data or {},
            "execution_time_ms": execution_time_ms,
            "error_details": error_details or {},
            "rate_limit_info": rate_limit_info or {},
        }
        
        external_api = ActivityExternalAPI(**external_api_data)
        
        if session:
            return await ActivityExternalAPICRUD.create(session, external_api)
        else:
            async for db_session in get_async_session():
                return await ActivityExternalAPICRUD.create(db_session, external_api)

    # System Events Tracking

    async def log_system_event(
        self,
        event_type: str,
        severity: str,
        component: str,
        message: str,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
        stack_trace: Optional[str] = None,
        affected_entities: Optional[List[str]] = None,
        session: Optional[AsyncSession] = None
    ) -> ActivitySystemEvent:
        """Log a system event activity.
        
        Args:
            event_type: Type of system event (error, warning, info, etc.)
            severity: Event severity level (low, medium, high, critical)
            component: System component that generated the event
            message: Event message
            user_id: Optional user ID if event is user-related
            details: Additional event details
            error_code: Optional error code
            stack_trace: Optional stack trace for errors
            affected_entities: List of affected entity IDs
            session: Database session
            
        Returns:
            Created ActivitySystemEvent instance
        """
        system_event_data = {
            "event_type": event_type,
            "severity": severity,
            "component": component,
            "message": message,
            "user_id": user_id,
            "details": details or {},
            "error_code": error_code,
            "stack_trace": stack_trace,
            "affected_entities": affected_entities or [],
        }
        
        system_event = ActivitySystemEvent(**system_event_data)
        
        if session:
            return await ActivitySystemEventCRUD.create(session, system_event)
        else:
            async for db_session in get_async_session():
                return await ActivitySystemEventCRUD.create(db_session, system_event)

    # Utility Methods

    def _redact_sensitive_data(self, data: Dict[str, Any], sensitive_keys: List[str]) -> Dict[str, Any]:
        """Redact sensitive information from activity data.
        
        Args:
            data: Data dictionary to redact
            sensitive_keys: List of keys to redact
            
        Returns:
            Data dictionary with sensitive values replaced with [REDACTED]
        """
        if not data:
            return data
        
        redacted_data = data.copy()
        for key in sensitive_keys:
            if key in redacted_data:
                redacted_data[key] = "[REDACTED]"
        
        return redacted_data

    def _extract_request_info(self, request: Request) -> Dict[str, Any]:
        """Extract useful information from a FastAPI request.
        
        Args:
            request: FastAPI Request object
            
        Returns:
            Dictionary containing extracted request information
        """
        return {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "client_host": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }

    async def get_activity_summary(
        self,
        user_id: str,
        days: int = 30,
        session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """Get activity summary for a user over a time period.
        
        Args:
            user_id: User ID to get summary for
            days: Number of days to look back
            session: Database session
            
        Returns:
            Dictionary with activity summary statistics
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        if session:
            return await ActivityCompositeCRUD.get_user_activity_summary(
                session, user_id, start_date
            )
        else:
            async for db_session in get_async_session():
                return await ActivityCompositeCRUD.get_user_activity_summary(
                    db_session, user_id, start_date
                )


# Service instance
activity_service = ActivityService()
