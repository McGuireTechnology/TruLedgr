# TruLedgr Activities Module

## Overview

The Activities module provides comprehensive activity tracking and audit trail functionality for TruLedgr, enabling monitoring of user actions, system events, and data changes for security and compliance purposes.

## Module Structure

```
api/activities/
├── __init__.py          # Module exports and initialization
├── models.py            # SQLModel database models
├── crud.py              # Async CRUD operations
├── service.py           # Business logic service layer
├── router.py            # FastAPI route definitions
└── schemas.py           # Pydantic request/response schemas
```

## Features

### 1. Core Activity Tracking
- **Activity**: Base activity tracking for all user actions
- Supports activity types, entities, descriptions, status tracking
- Flexible details and context storage using JSON fields
- Tagging system for categorization

### 2. Specialized Activity Types

#### API Transaction Tracking
- **ActivityAPITransaction**: Records all API calls
- Captures HTTP method, endpoint, status codes
- Tracks request/response data, headers, execution time
- Error details and performance metrics

#### Data Access Monitoring
- **ActivityDataAccess**: Monitors data read operations
- Tracks table access, query parameters, fields accessed
- Records permission levels and applied filters
- Useful for compliance and security auditing

#### Data Change Auditing
- **ActivityDataChanges**: Comprehensive change tracking
- Before/after values for data modifications
- Changed fields identification
- Validation errors and business rules tracking

#### Authentication Events
- **ActivityAuthEvents**: Security-focused auth tracking
- Login/logout events, success/failure tracking
- IP address, user agent, session information
- Two-factor authentication and login method tracking

#### External API Monitoring
- **ActivityExternalAPI**: Third-party API call tracking
- Service name, endpoint, method tracking
- Response codes, execution time, error details
- Rate limiting information

#### System Events
- **ActivitySystemEvent**: System-level event tracking
- Event types, severity levels, component identification
- Error codes, stack traces, affected entities
- System health and error monitoring

## Database Models

All models inherit from `TimestampMixin` providing:
- `id`: ULID-based primary keys
- `created_at`: Automatic creation timestamp
- `updated_at`: Automatic update timestamp

### Key Features:
- **Async Support**: All operations use AsyncSession for performance
- **Flexible JSON Storage**: Details, context, and metadata stored as JSON
- **Comprehensive Indexing**: Optimized queries for user, type, and date filtering
- **Type Safety**: Full SQLModel integration with Pydantic validation

## Service Layer

### ActivityService
Provides high-level business logic operations:

```python
# Create activities
activity = await activity_service.create_activity(
    activity_type="user_login",
    user_id="user_123",
    description="User logged in successfully"
)

# Track API transactions
api_transaction = await activity_service.log_api_transaction(
    user_id="user_123",
    method="POST",
    endpoint="/api/users",
    status_code=201
)

# Monitor data access
data_access = await activity_service.log_data_access(
    user_id="user_123",
    table_name="users",
    operation="read",
    fields_accessed=["id", "email", "name"]
)

# Track data changes
data_changes = await activity_service.log_data_changes(
    user_id="user_123",
    table_name="users",
    operation="update",
    record_id="user_456",
    old_values={"name": "John"},
    new_values={"name": "John Doe"}
)
```

## API Endpoints

### Core Endpoints
- `GET /activities/` - Get user activities with filtering
- `GET /activities/{activity_id}` - Get specific activity
- `GET /activities/summary/user` - Get user activity summary

### Specialized Endpoints
- `GET /activities/api-transactions/` - API transaction history
- `GET /activities/data-access/` - Data access logs
- `GET /activities/data-changes/` - Data change audit trail
- `GET /activities/auth-events/` - Authentication events
- `GET /activities/external-api/` - External API call logs
- `GET /activities/system-events/` - System events (admin)

### Admin Endpoints
- `GET /activities/admin/users/{user_id}/activities` - Admin view of user activities
- `GET /activities/admin/summary/{user_id}` - Admin activity summary

## CRUD Operations

All CRUD classes provide:
- **Async Operations**: Full async/await support
- **Filtering**: Flexible filtering by multiple criteria
- **Pagination**: Limit/offset pagination
- **Error Handling**: Proper rollback on failures
- **Performance**: Optimized queries with proper indexing

### Available CRUD Classes:
- `ActivityCRUD`
- `ActivityAPITransactionCRUD`
- `ActivityDataAccessCRUD`
- `ActivityDataChangesCRUD`
- `ActivityAuthEventsCRUD`
- `ActivityExternalAPICRUD`
- `ActivitySystemEventCRUD`
- `ActivityCompositeCRUD` (cross-table operations)

## Schemas

Comprehensive Pydantic schemas for:
- **Request Validation**: Create/update schemas
- **Response Serialization**: Response schemas with proper field types
- **Filtering**: Filter request schemas
- **Summaries**: Activity summary response schemas

## Integration

### Usage in Other Modules
```python
from api.activities import activity_service

# In your route handlers
@router.post("/users/")
async def create_user(user_data: UserCreate, session: AsyncSession = Depends(get_db)):
    # Create user
    user = await user_service.create_user(session, user_data)
    
    # Log the activity
    await activity_service.create_activity(
        activity_type="user_creation",
        user_id=current_user.id,
        entity_type="user",
        entity_id=user.id,
        description=f"Created new user: {user.email}",
        session=session
    )
    
    return user
```

### Middleware Integration
The module can be integrated with FastAPI middleware for automatic activity tracking:

```python
# Automatic API transaction logging
await activity_service.log_api_transaction(
    user_id=current_user.id,
    method=request.method,
    endpoint=str(request.url.path),
    status_code=response.status_code,
    execution_time_ms=execution_time,
    session=session
)
```

## Security Features

- **User Isolation**: Activities are scoped to users
- **Permission Checks**: Route-level access control
- **Data Redaction**: Sensitive data filtering utilities
- **Audit Compliance**: Comprehensive change tracking
- **Authentication Monitoring**: Failed login attempt tracking

## Performance Considerations

- **Async Operations**: Non-blocking database operations
- **Optimized Queries**: Proper indexing and query optimization
- **Pagination**: Prevents large data transfers
- **Selective Loading**: Load only required fields
- **Connection Pooling**: Efficient database connection management

## Extension Points

The module is designed for extensibility:
- **Custom Activity Types**: Easy to add new activity categories
- **Custom Fields**: JSON storage allows flexible data structures
- **Custom Filters**: CRUD operations support dynamic filtering
- **Custom Aggregations**: ActivityCompositeCRUD for complex queries
- **Webhook Integration**: Can trigger external notifications

## Future Enhancements

Potential improvements:
- **Real-time Notifications**: WebSocket integration for live activity feeds
- **Analytics Dashboard**: Activity visualization and reporting
- **Data Retention Policies**: Automatic cleanup of old activities
- **Export Functionality**: CSV/JSON export for compliance reporting
- **Advanced Filtering**: Full-text search capabilities

## Conclusion

The Activities module provides a robust foundation for activity tracking in TruLedgr, supporting security, compliance, and operational monitoring requirements while maintaining high performance and extensibility.
