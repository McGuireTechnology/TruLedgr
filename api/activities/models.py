"""
Activity and audit trail models for TruLedgr API

This module provides comprehensive activity tracking for audit trail functionality.
All user actions, system events, and data changes are logged for security and compliance.
"""

from sqlmodel import SQLModel, Field, Column, String, Text, DateTime, JSON
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy import func, Index
from api.common.models import TimestampMixin


class Activity(TimestampMixin, table=True):
    """Core activity record for tracking user and system actions"""
    __tablename__ = "activities" # type: ignore

    id: str = Field(primary_key=True, index=True)
    
    # Core activity information
    activity_type: Optional[str] = Field(default=None, max_length=100, description="Type of activity")
    description: Optional[str] = Field(default=None, max_length=500, description="Human-readable description")
    
    # Context information
    user_id: Optional[str] = Field(default=None, foreign_key="users.id", index=True, description="User who performed the action")
    session_id: Optional[str] = Field(default=None, foreign_key="user_sessions.id", index=True, description="Session context")
    client_ip: Optional[str] = Field(default=None, max_length=45, description="Client IP address")
    user_agent: Optional[str] = Field(default=None, max_length=500, description="User agent string")
    
    # Additional data (renamed from metadata to avoid conflict)
    extra_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON), description="Additional activity metadata")
    
    # Status
    status: str = Field(default="completed", max_length=50, index=True, description="Activity status")
    error_message: Optional[str] = Field(default=None, max_length=1000, description="Error message if failed")


class ActivityAPITransaction(TimestampMixin, table=True):
    """API request/response tracking for audit trails"""
    __tablename__ = "activity_api_transactions" # type: ignore

    id: str = Field(primary_key=True, index=True)
    activity_id: str = Field(foreign_key="activities.id", index=True, description="Related activity ID")

    # Request information
    method: str = Field(max_length=10, index=True, description="HTTP method (e.g., GET, POST)")
    path: str = Field(max_length=2000, index=True, description="Request path")
    query_params: Optional[str] = Field(default=None, max_length=2000, description="Query string parameters")
    
    # Headers (filtered for security)
    request_headers: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON), description="Filtered request headers")
    response_headers: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON), description="Response headers")
    
    # Body data (may be redacted)
    request_body: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON), description="Request body (sensitive data redacted)")
    response_body: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON), description="Response body (sensitive data redacted)")
    
    # Response information
    status_code: Optional[int] = Field(default=None, index=True, description="HTTP response status code")
    response_time_ms: Optional[int] = Field(default=None, description="Response time in milliseconds")
    
    # Size tracking
    request_size: Optional[int] = Field(default=None, description="Request size in bytes")
    response_size: Optional[int] = Field(default=None, description="Response size in bytes")


class ActivityDataAccess(TimestampMixin, table=True):
    """Track data access events for security auditing"""
    __tablename__ = "activity_data_access" # type: ignore

    id: str = Field(primary_key=True, index=True)
    activity_id: str = Field(foreign_key="activities.id", index=True, description="Related activity ID")

    # Entity being accessed
    entity_type: str = Field(max_length=100, index=True, description="Type of entity accessed (e.g., 'user', 'transaction')")
    entity_id: str = Field(max_length=50, index=True, description="ID of the accessed entity")
    entity_name: Optional[str] = Field(default=None, max_length=255, description="Human-readable entity name")
    
    # Access details
    access_type: str = Field(max_length=50, index=True, description="Type of access (read, list, search, etc.)")
    permission_level: Optional[str] = Field(default=None, max_length=50, description="Permission level used")
    
    # Context
    fields_accessed: Optional[List[str]] = Field(default=None, sa_column=Column(JSON), description="Specific fields accessed")
    filter_criteria: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON), description="Filter criteria used")
    record_count: Optional[int] = Field(default=None, description="Number of records accessed")


class ActivityDataChanges(TimestampMixin, table=True):
    """Track data modification events with before/after values"""
    __tablename__ = "activity_data_changes" # type: ignore

    id: str = Field(primary_key=True, index=True)
    activity_id: str = Field(foreign_key="activities.id", index=True, description="Related activity ID")

    # Entity being modified
    entity_type: str = Field(max_length=100, index=True, description="Type of entity modified")
    entity_id: str = Field(max_length=50, index=True, description="ID of the modified entity")
    entity_name: Optional[str] = Field(default=None, max_length=255, description="Human-readable entity name")
    
    # Change details
    change_type: str = Field(max_length=50, index=True, description="Type of change (create, update, delete, restore)")
    
    # Value tracking (sensitive data redacted)
    old_values: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON), description="Previous values (for updates)")
    new_values: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON), description="New values (for creates/updates)")
    changed_fields: Optional[List[str]] = Field(default=None, sa_column=Column(JSON), description="List of fields that changed")
    
    # Context
    change_reason: Optional[str] = Field(default=None, max_length=500, description="Reason for the change")
    bulk_operation: bool = Field(default=False, index=True, description="Whether this was part of a bulk operation")


class ActivityAuthEvents(TimestampMixin, table=True):
    """Track authentication and authorization events"""
    __tablename__ = "activity_auth_events" # type: ignore

    id: str = Field(primary_key=True, index=True)
    activity_id: str = Field(foreign_key="activities.id", index=True, description="Related activity ID")

    # Event details
    event_type: str = Field(max_length=50, index=True, description="Type of auth event")
    event_category: str = Field(max_length=50, index=True, description="Event category (authentication, authorization, session)")
    
    # User context
    user_id: Optional[str] = Field(default=None, foreign_key="users.id", index=True, description="User involved in the event")
    username: Optional[str] = Field(default=None, max_length=100, description="Username at time of event")
    
    # Result
    success: bool = Field(index=True, description="Whether the event was successful")
    failure_reason: Optional[str] = Field(default=None, max_length=255, description="Reason for failure if unsuccessful")
    
    # Context
    auth_method: Optional[str] = Field(default=None, max_length=50, description="Authentication method used")
    permission_checked: Optional[str] = Field(default=None, max_length=255, description="Permission that was checked")
    resource_accessed: Optional[str] = Field(default=None, max_length=255, description="Resource being accessed")
    
    # Risk assessment
    risk_score: Optional[int] = Field(default=None, description="Risk score for this event (0-100)")
    risk_factors: Optional[List[str]] = Field(default=None, sa_column=Column(JSON), description="Risk factors identified")


class ActivityExternalAPI(TimestampMixin, table=True):
    """Track external API calls and integrations"""
    __tablename__ = "activity_external_api" # type: ignore

    id: str = Field(primary_key=True, index=True)
    activity_id: str = Field(foreign_key="activities.id", index=True, description="Related activity ID")

    # Service details
    service_name: str = Field(max_length=100, index=True, description="Name of external service")
    service_endpoint: str = Field(max_length=500, description="API endpoint called")
    service_method: str = Field(max_length=10, description="HTTP method used")
    
    # Request/Response (redacted)
    request_summary: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON), description="Summary of request data")
    response_summary: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON), description="Summary of response data")
    
    # Timing and status
    status_code: Optional[int] = Field(default=None, index=True, description="HTTP status code")
    response_time_ms: Optional[int] = Field(default=None, description="Response time in milliseconds")
    
    # Context
    purpose: Optional[str] = Field(default=None, max_length=255, description="Purpose of the API call")
    user_context: Optional[str] = Field(default=None, foreign_key="users.id", description="User on whose behalf the call was made")
    
    # Error handling
    error_code: Optional[str] = Field(default=None, max_length=100, description="Error code if failed")
    error_message: Optional[str] = Field(default=None, max_length=500, description="Error message if failed")
    retry_count: int = Field(default=0, description="Number of retries attempted")


class ActivitySystemEvent(TimestampMixin, table=True):
    """Track system-level events and operations"""
    __tablename__ = "activity_system_events" # type: ignore

    id: str = Field(primary_key=True, index=True)
    activity_id: str = Field(foreign_key="activities.id", index=True, description="Related activity ID")

    # Event details
    event_type: str = Field(max_length=100, index=True, description="Type of system event")
    component: str = Field(max_length=100, index=True, description="System component involved")
    severity: str = Field(max_length=20, index=True, description="Event severity level")
    
    # Context
    message: str = Field(max_length=1000, description="Event message")
    details: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON), description="Additional event details")
    
    # Performance metrics
    duration_ms: Optional[int] = Field(default=None, description="Duration in milliseconds")
    memory_usage: Optional[int] = Field(default=None, description="Memory usage in bytes")
    cpu_usage: Optional[float] = Field(default=None, description="CPU usage percentage")
    
    # Related entities
    affected_entities: Optional[List[Dict[str, str]]] = Field(default=None, sa_column=Column(JSON), description="Entities affected by this event")


# Create indexes for better query performance
Activity.__table_args__ = (
    Index('idx_activities_user_created', 'user_id', 'created_at'),
    Index('idx_activities_type_created', 'activity_type', 'created_at'),
    Index('idx_activities_status_created', 'status', 'created_at'),
)

ActivityAPITransaction.__table_args__ = (
    Index('idx_api_transactions_activity_method', 'activity_id', 'method'),
    Index('idx_api_transactions_path_created', 'path', 'created_at'),
    Index('idx_api_transactions_status_created', 'status_code', 'created_at'),
)

ActivityDataAccess.__table_args__ = (
    Index('idx_data_access_entity', 'entity_type', 'entity_id'),
    Index('idx_data_access_type_created', 'access_type', 'created_at'),
)

ActivityDataChanges.__table_args__ = (
    Index('idx_data_changes_entity', 'entity_type', 'entity_id'),
    Index('idx_data_changes_type_created', 'change_type', 'created_at'),
)

ActivityAuthEvents.__table_args__ = (
    Index('idx_auth_events_user_type', 'user_id', 'event_type'),
    Index('idx_auth_events_success_created', 'success', 'created_at'),
    Index('idx_auth_events_category_created', 'event_category', 'created_at'),
)

ActivityExternalAPI.__table_args__ = (
    Index('idx_external_api_service_created', 'service_name', 'created_at'),
    Index('idx_external_api_status_created', 'status_code', 'created_at'),
)

ActivitySystemEvent.__table_args__ = (
    Index('idx_system_events_type_created', 'event_type', 'created_at'),
    Index('idx_system_events_component_severity', 'component', 'severity'),
)
