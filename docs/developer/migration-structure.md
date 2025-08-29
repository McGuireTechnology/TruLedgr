# TruLedgr Database Migration Structure

## Overview

The TruLedgr database has been restructured into **7 logical, incremental migrations** that are easier to understand, maintain, and deploy. Each migration focuses on a specific functional area and properly handles foreign key dependencies.

## Migration Sequence

### 001: Base Tables (`001_create_base_tables.py`)
**Purpose**: Create foundational tables with no foreign key dependencies

**Tables Created**:
- `item` - General items and entities
- `permissions` - Authorization permissions (actions on resources)
- `roles` - User roles for RBAC

**Dependencies**: None
**Key Features**:
- Clean foundation for the authorization system
- No foreign keys, so can be created first
- Includes proper indexes for performance

### 002: Role-Permission Relationships (`002_create_role_permissions.py`)
**Purpose**: Establish many-to-many relationship between roles and permissions

**Tables Created**:
- `role_permissions` - Junction table linking roles to permissions

**Dependencies**: Requires `roles` and `permissions` tables
**Key Features**:
- Implements RBAC permission assignments
- Tracks when permissions were assigned and by whom
- Composite primary key on (role_id, permission_id)

### 003: Users Table (`003_create_users_table.py`)
**Purpose**: Create the core users table

**Tables Created**:
- `users` - Main user accounts and profiles

**Dependencies**: Requires `roles` table for role assignment
**Key Features**:
- Complete user profile management
- OAuth integration support
- TOTP/2FA security features
- Soft delete capability
- Audit timestamps

### 004: Groups and User Groups (`004_create_groups_tables.py`)
**Purpose**: Add group management and user membership

**Tables Created**:
- `groups` - User groups/teams
- `user_groups` - Many-to-many user-group membership

**Dependencies**: Requires `users` table for ownership and membership
**Key Features**:
- Group ownership by users
- Member count tracking
- Group settings and metadata
- User roles within groups

### 005: Authentication Tables (`005_create_auth_tables.py`)
**Purpose**: Add OAuth and password reset functionality

**Tables Created**:
- `oauth_accounts` - OAuth provider accounts (primary implementation)
- `oauth2account` - Alternative OAuth implementation
- `password_reset_tokens` - Password reset tokens (primary implementation)
- `passwordresettoken` - Alternative password reset implementation

**Dependencies**: Requires `users` table for account linking
**Key Features**:
- Multiple OAuth provider support
- Secure password reset workflow
- Token expiration and revocation
- Client tracking (IP, user agent)

### 006: Session Management (`006_create_session_tables.py`)
**Purpose**: Add user session tracking and analytics

**Tables Created**:
- `user_sessions` - Active user sessions
- `sessionanalytics` - Session analytics and security metrics

**Dependencies**: Requires `users` table for session ownership
**Key Features**:
- Session token management
- Device fingerprinting
- Security monitoring
- Session analytics and metrics

### 007: Session Activities (`007_create_session_activities.py`)
**Purpose**: Add detailed session activity logging

**Tables Created**:
- `session_activities` - Detailed activity logs per session

**Dependencies**: Requires `user_sessions` and `users` tables
**Key Features**:
- Request-level activity tracking
- Audit trail for user actions
- Performance monitoring
- Security event logging

## Migration Benefits

### 1. **Logical Organization**
- Each migration focuses on a single functional area
- Clear dependency chain prevents foreign key errors
- Easy to understand and review changes

### 2. **Incremental Deployment**
- Can deploy specific functionality in stages
- Easier rollback to specific points
- Reduced risk of large migration failures

### 3. **Development Workflow**
- Smaller, focused migrations are easier to review
- Team members can work on different functional areas
- Less merge conflicts in migration files

### 4. **Maintenance**
- Easier to locate specific table/feature changes
- Clear history of when features were added
- Simplified debugging and troubleshooting

## Dependency Graph

```
001_base_tables (item, permissions, roles)
    ↓
002_role_permissions (role_permissions)
    ↓  
003_users_table (users) ← depends on roles
    ↓
004_groups_tables (groups, user_groups) ← depends on users
    ↓
005_auth_tables (oauth_*, password_reset_*) ← depends on users
    ↓
006_session_tables (user_sessions, sessionanalytics) ← depends on users
    ↓
007_session_activities (session_activities) ← depends on user_sessions, users
```

## Migration Commands

### Apply All Migrations
```bash
python scripts/migrate.py upgrade
```

### Apply Specific Migration
```bash
python scripts/migrate.py upgrade 003_users_table
```

### Rollback to Specific Point
```bash
python scripts/migrate.py downgrade 002_role_permissions
```

### Check Current State
```bash
python scripts/migrate.py current
python scripts/migrate.py history
```

## Best Practices

### 1. **Always Test Locally First**
- Apply migrations to development database
- Verify data integrity and relationships
- Test rollback functionality

### 2. **Review Migration Content**
- Check foreign key constraints are correct
- Verify index creation for performance
- Ensure proper column types and constraints

### 3. **Backup Before Production**
- Always backup production database before migrations
- Test migration on production-like data
- Have rollback plan ready

### 4. **Monitor Performance**
- Large table migrations may take time
- Consider maintenance windows for production
- Monitor database performance after migrations

## Future Migrations

When adding new features:

1. **Create focused migrations** for single functional areas
2. **Consider dependencies** - create independent tables first
3. **Add relationships** in separate migration after both tables exist
4. **Update ERD documentation** after applying migrations
5. **Test both upgrade and downgrade** paths

## Related Documentation

- [Migration Management Script](../../scripts/migrate.py)
- [ERD Generator](../../scripts/generate_erd.py) 
- [Database Overview](./database-overview.md)
- [Module ERDs](./database/README.md)

---

*This migration structure provides a solid foundation for TruLedgr's database evolution while maintaining clarity and reliability.*
