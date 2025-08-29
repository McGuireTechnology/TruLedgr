# Common Database Models Documentation

This document covers the common database models and mixins used throughout the TruLedgr application. These foundational components provide consistent functionality across all database entities.

## Overview

The common models module (`api/common/models.py`) provides reusable mixins that implement standard database patterns used across the application. These mixins follow SQLModel conventions and provide automatic functionality for timestamps and soft deletion.

## Base Mixins

### TimestampMixin

The `TimestampMixin` provides automatic timestamp tracking for database records, ensuring consistent created and updated time tracking across all models.

```python
class TimestampMixin(SQLModel):
    """Mixin for created_at and updated_at timestamps"""
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
```

#### Fields

| Field | Type | Description | Default | Constraints |
|-------|------|-------------|---------|-------------|
| `created_at` | `Optional[datetime]` | Timestamp when the record was first created | `datetime.utcnow()` | Auto-generated on creation |
| `updated_at` | `Optional[datetime]` | Timestamp when the record was last modified | `datetime.utcnow()` | Auto-updated on modification |

#### Usage

```python
from api.common.models import TimestampMixin

class User(TimestampMixin, table=True):
    id: str = Field(primary_key=True)
    email: str = Field(unique=True)
    # created_at and updated_at are automatically included
```

#### Features

- **Automatic Creation Timestamp**: `created_at` is automatically set when a record is first saved
- **Automatic Update Timestamp**: `updated_at` is automatically updated whenever the record is modified
- **UTC Timezone**: All timestamps use UTC to ensure consistency across different server timezones
- **Optional Type**: Fields are optional to handle edge cases during model initialization

#### Database Behavior

- **On INSERT**: Both `created_at` and `updated_at` are set to the current UTC timestamp
- **On UPDATE**: Only `updated_at` is modified to reflect the latest change
- **Indexing**: These fields are commonly indexed for efficient date-range queries

#### Best Practices

1. **Always use UTC**: The mixin uses `datetime.utcnow()` to ensure timezone consistency
2. **Query Optimization**: Index these fields when performing frequent date-range queries
3. **Audit Trails**: Use these timestamps for basic audit functionality
4. **Data Migration**: Preserve existing timestamps when migrating data

### SoftDeleteMixin

The `SoftDeleteMixin` implements soft deletion functionality, allowing records to be marked as deleted without physical removal from the database.

```python
class SoftDeleteMixin(SQLModel):
    """Mixin for soft delete functionality"""
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = Field(default=None)
```

#### SoftDeleteMixin Fields

| Field | Type | Description | Default | Constraints |
|-------|------|-------------|---------|-------------|
| `is_deleted` | `bool` | Boolean flag indicating if the record is deleted | `False` | Required field |
| `deleted_at` | `Optional[datetime]` | Timestamp when the record was soft-deleted | `None` | Set when deletion occurs |

#### SoftDeleteMixin Usage

```python
from api.common.models import SoftDeleteMixin, TimestampMixin

class Document(TimestampMixin, SoftDeleteMixin, table=True):
    id: str = Field(primary_key=True)
    title: str
    content: str
    # is_deleted and deleted_at are automatically included
```

#### SoftDeleteMixin Features

- **Non-Destructive Deletion**: Records remain in the database but are marked as deleted
- **Audit Trail Preservation**: Maintains data for compliance and audit purposes
- **Quick Status Check**: Boolean flag allows for efficient filtering of active records
- **Deletion Timestamp**: Tracks exactly when the deletion occurred

#### Implementation Patterns

##### Soft Delete Operation

```python
async def soft_delete_document(document_id: str, db: AsyncSession):
    document = await db.get(Document, document_id)
    if document and not document.is_deleted:
        document.is_deleted = True
        document.deleted_at = datetime.utcnow()
        await db.commit()
        return document
    return None
```

##### Query Active Records

```python
async def get_active_documents(db: AsyncSession):
    query = select(Document).where(Document.is_deleted == False)
    result = await db.execute(query)
    return result.scalars().all()
```

##### Restore Deleted Record

```python
async def restore_document(document_id: str, db: AsyncSession):
    document = await db.get(Document, document_id)
    if document and document.is_deleted:
        document.is_deleted = False
        document.deleted_at = None
        await db.commit()
        return document
    return None
```

#### Database Considerations

- **Indexing Strategy**: Index `is_deleted` for efficient filtering of active records
- **Composite Indexes**: Consider composite indexes like `(user_id, is_deleted)` for user-specific queries
- **Storage Impact**: Soft-deleted records consume storage space indefinitely
- **Performance**: Large numbers of soft-deleted records can impact query performance

#### SoftDeleteMixin Best Practices

1. **Default Queries**: Always filter by `is_deleted = False` unless specifically querying deleted records
2. **Archival Strategy**: Implement periodic archival of old soft-deleted records
3. **Permissions**: Ensure proper authorization for viewing and restoring deleted records
4. **Cascade Considerations**: Plan how soft deletion affects related records
5. **Data Retention**: Comply with data retention policies and regulations

## Combined Usage

Most models in TruLedgr inherit from both mixins to provide comprehensive record tracking:

```python
class BaseModel(TimestampMixin, SoftDeleteMixin, SQLModel):
    """Base model with timestamps and soft delete functionality"""
    pass

class User(BaseModel, table=True):
    id: str = Field(primary_key=True)
    email: str = Field(unique=True)
    username: str = Field(unique=True)
    # Automatically includes: created_at, updated_at, is_deleted, deleted_at
```

## Database Schema Impact

When using these mixins, the following columns are added to each table:

```sql
-- TimestampMixin columns
created_at TIMESTAMP WITH TIME ZONE,
updated_at TIMESTAMP WITH TIME ZONE,

-- SoftDeleteMixin columns  
is_deleted BOOLEAN DEFAULT FALSE,
deleted_at TIMESTAMP WITH TIME ZONE
```

## Migration Considerations

When adding these mixins to existing models:

1. **Add Columns**: Migration will add the new columns with appropriate defaults
2. **Populate Timestamps**: Existing records will get current timestamp for both fields
3. **Index Creation**: Consider adding indexes for performance
4. **Application Logic**: Update queries to handle soft deletion appropriately

## Testing Patterns

### Testing Timestamps

```python
def test_timestamp_creation():
    user = User(email="test@example.com")
    assert user.created_at is not None
    assert user.updated_at is not None
    assert user.created_at == user.updated_at

def test_timestamp_updates():
    user = User(email="test@example.com")
    original_created = user.created_at
    
    # Simulate update
    user.updated_at = datetime.utcnow()
    
    assert user.created_at == original_created
    assert user.updated_at > user.created_at
```

### Testing Soft Delete

```python
def test_soft_delete():
    user = User(email="test@example.com")
    assert not user.is_deleted
    assert user.deleted_at is None
    
    # Soft delete
    user.is_deleted = True
    user.deleted_at = datetime.utcnow()
    
    assert user.is_deleted
    assert user.deleted_at is not None
```

## Performance Considerations

### Indexing Strategy

```sql
-- Recommended indexes for performance
CREATE INDEX idx_tablename_is_deleted ON tablename(is_deleted);
CREATE INDEX idx_tablename_created_at ON tablename(created_at);
CREATE INDEX idx_tablename_updated_at ON tablename(updated_at);

-- Composite indexes for common query patterns
CREATE INDEX idx_tablename_user_active ON tablename(user_id, is_deleted);
CREATE INDEX idx_tablename_date_range ON tablename(created_at, updated_at);
```

### Query Optimization

1. **Always Filter**: Include `is_deleted = False` in WHERE clauses
2. **Use Indexes**: Ensure timestamp columns are indexed for date-range queries
3. **Limit Results**: Use pagination for large result sets
4. **Composite Queries**: Design indexes that support your most common query patterns

## Security Considerations

1. **Access Control**: Implement proper permissions for viewing deleted records
2. **Audit Logging**: Log all soft delete and restore operations
3. **Data Privacy**: Consider GDPR and other privacy regulations for deleted data
4. **Retention Policies**: Implement automatic cleanup of old soft-deleted records

## Related Documentation

- [Database Models Overview](../database-models.md)
- [User Models](./users.md)
- [Migration Guide](../migrations.md)
- [API Security](../security.md)
