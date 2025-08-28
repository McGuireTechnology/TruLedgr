"""
Activity schemas for TruLedgr API

This module provides Pydantic schemas for request/response validation
and serialization for the activity tracking system.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ActivityBase(BaseModel):
    """Base schema for Activity"""
    activity_type: str = Field(..., description="Type of activity")
    user_id: str = Field(..., description="User ID who performed the activity")
    entity_type: Optional[str] = Field(None, description="Type of entity involved")
    entity_id: Optional[str] = Field(None, description="ID of entity involved")
    description: Optional[str] = Field(None, description="Human-readable description")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional details")
    status: str = Field(default="completed", description="Activity status")
    tags: List[str] = Field(default_factory=list, description="Activity tags")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")


class ActivityCreate(ActivityBase):
    """Schema for creating an activity"""
    pass


class ActivityUpdate(BaseModel):
    """Schema for updating an activity"""
    status: Optional[str] = Field(None, description="Activity status")
    description: Optional[str] = Field(None, description="Updated description")
    details: Optional[Dict[str, Any]] = Field(None, description="Updated details")
    tags: Optional[List[str]] = Field(None, description="Updated tags")
    context: Optional[Dict[str, Any]] = Field(None, description="Updated context")


class ActivityResponse(ActivityBase):
    """Schema for activity response"""
    id: str = Field(..., description="Activity ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class ActivitySummaryResponse(BaseModel):
    """Schema for activity summary response"""
    user_id: str = Field(..., description="User ID")
    period_start: datetime = Field(..., description="Summary period start")
    activity_counts: Dict[str, int] = Field(..., description="Activity counts by type")
    api_transaction_count: int = Field(..., description="Total API transactions")
    data_access_count: int = Field(..., description="Total data access events")
    total_activities: int = Field(..., description="Total activity count")

    class Config:
        from_attributes = True


class ActivityFilterRequest(BaseModel):
    """Schema for activity filtering requests"""
    activity_type: Optional[str] = Field(None, description="Filter by activity type")
    entity_type: Optional[str] = Field(None, description="Filter by entity type")
    status: Optional[str] = Field(None, description="Filter by status")
    start_date: Optional[datetime] = Field(None, description="Filter activities after this date")
    end_date: Optional[datetime] = Field(None, description="Filter activities before this date")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum results")
    offset: int = Field(default=0, ge=0, description="Results offset")


class APITransactionBase(BaseModel):
    """Base schema for API Transaction"""
    user_id: str = Field(..., description="User ID")
    method: str = Field(..., description="HTTP method")
    endpoint: str = Field(..., description="API endpoint")
    status_code: int = Field(..., description="HTTP status code")
    request_data: Dict[str, Any] = Field(default_factory=dict, description="Request data")
    response_data: Dict[str, Any] = Field(default_factory=dict, description="Response data")
    execution_time_ms: Optional[int] = Field(None, description="Execution time in milliseconds")
    request_headers: Dict[str, str] = Field(default_factory=dict, description="Request headers")
    response_headers: Dict[str, str] = Field(default_factory=dict, description="Response headers")
    error_details: Dict[str, Any] = Field(default_factory=dict, description="Error details")


class APITransactionResponse(APITransactionBase):
    """Schema for API transaction response"""
    id: str = Field(..., description="Transaction ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class DataAccessBase(BaseModel):
    """Base schema for Data Access"""
    user_id: str = Field(..., description="User ID")
    table_name: str = Field(..., description="Table name")
    operation: str = Field(..., description="Operation type")
    record_id: Optional[str] = Field(None, description="Record ID")
    query_parameters: Dict[str, Any] = Field(default_factory=dict, description="Query parameters")
    fields_accessed: List[str] = Field(default_factory=list, description="Fields accessed")
    filters_applied: Dict[str, Any] = Field(default_factory=dict, description="Filters applied")
    permission_level: Optional[str] = Field(None, description="Permission level")


class DataAccessResponse(DataAccessBase):
    """Schema for data access response"""
    id: str = Field(..., description="Access ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class DataChangesBase(BaseModel):
    """Base schema for Data Changes"""
    user_id: str = Field(..., description="User ID")
    table_name: str = Field(..., description="Table name")
    operation: str = Field(..., description="Operation type")
    record_id: str = Field(..., description="Record ID")
    old_values: Dict[str, Any] = Field(default_factory=dict, description="Old values")
    new_values: Dict[str, Any] = Field(default_factory=dict, description="New values")
    changed_fields: List[str] = Field(default_factory=list, description="Changed fields")
    validation_errors: List[str] = Field(default_factory=list, description="Validation errors")
    business_rules_applied: List[str] = Field(default_factory=list, description="Business rules applied")


class DataChangesResponse(DataChangesBase):
    """Schema for data changes response"""
    id: str = Field(..., description="Changes ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class AuthEventBase(BaseModel):
    """Base schema for Auth Event"""
    user_id: Optional[str] = Field(None, description="User ID")
    event_type: str = Field(..., description="Event type")
    success: bool = Field(..., description="Success status")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent")
    session_id: Optional[str] = Field(None, description="Session ID")
    failure_reason: Optional[str] = Field(None, description="Failure reason")
    two_factor_used: bool = Field(default=False, description="Two-factor authentication used")
    login_method: Optional[str] = Field(None, description="Login method")


class AuthEventResponse(AuthEventBase):
    """Schema for auth event response"""
    id: str = Field(..., description="Event ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class ExternalAPIBase(BaseModel):
    """Base schema for External API"""
    user_id: str = Field(..., description="User ID")
    service_name: str = Field(..., description="Service name")
    endpoint: str = Field(..., description="Endpoint")
    method: str = Field(..., description="HTTP method")
    status_code: Optional[int] = Field(None, description="Status code")
    request_data: Dict[str, Any] = Field(default_factory=dict, description="Request data")
    response_data: Dict[str, Any] = Field(default_factory=dict, description="Response data")
    execution_time_ms: Optional[int] = Field(None, description="Execution time")
    error_details: Dict[str, Any] = Field(default_factory=dict, description="Error details")
    rate_limit_info: Dict[str, Any] = Field(default_factory=dict, description="Rate limit info")


class ExternalAPIResponse(ExternalAPIBase):
    """Schema for external API response"""
    id: str = Field(..., description="API ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class SystemEventBase(BaseModel):
    """Base schema for System Event"""
    event_type: str = Field(..., description="Event type")
    severity: str = Field(..., description="Severity level")
    component: str = Field(..., description="System component")
    message: str = Field(..., description="Event message")
    user_id: Optional[str] = Field(None, description="User ID")
    details: Dict[str, Any] = Field(default_factory=dict, description="Event details")
    error_code: Optional[str] = Field(None, description="Error code")
    stack_trace: Optional[str] = Field(None, description="Stack trace")
    affected_entities: List[str] = Field(default_factory=list, description="Affected entities")


class SystemEventResponse(SystemEventBase):
    """Schema for system event response"""
    id: str = Field(..., description="Event ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True
