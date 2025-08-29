# TruLedgr Database Overview

## Introduction

This document provides a comprehensive overview of the TruLedgr database architecture, migration system, and documentation structure. The TruLedgr application uses a modular database design with proper migration management and automated documentation generation.

## Database Architecture

### Technology Stack
- **Database**: SQLite (dev/test) / PostgreSQL (production)
- **ORM**: SQLModel (FastAPI + SQLAlchemy)
- **Migrations**: Alembic
- **Documentation**: Automated ERD generation with Mermaid diagrams

### Module Structure

The database is organized into logical modules:

| Module | Tables | Primary Purpose |
|--------|--------|----------------|
| **Users** | 4 | User management, sessions, and profile data |
| **Authentication** | 4 | OAuth providers, password resets, and security tokens |
| **Authorization** | 3 | Role-based access control (RBAC) with permissions |
| **Groups** | 2 | User groups and team management |
| **Items** | 1 | General items and entities |

### Database Statistics
- **Total Tables**: 15 (excluding migration metadata)
- **Cross-Module Relationships**: Extensive foreign key relationships
- **Security Features**: Soft deletes, audit timestamps, session tracking
- **Scalability**: Modular design for easy expansion

## Migration Management

### Alembic Configuration

The database uses Alembic for migration management with the following setup:

```bash
# Location
/migrations/
├── env.py              # Alembic environment configuration
├── script.py.mako      # Migration template with SQLModel support
└── versions/           # Migration files
    └── da3322f0a7e8_initial_migration_with_all_existing_.py
```

### Migration Commands

```bash
# Create new migration
python scripts/migrate.py create "description"

# Apply migrations
python scripts/migrate.py upgrade

# Check current version
python scripts/migrate.py current

# View migration history
python scripts/migrate.py history

# Check for schema drift
python scripts/migrate.py check
```

### Features
- **Async Support**: Configured for async SQLModel operations
- **SQLModel Integration**: Automatic import handling in migration templates
- **Schema Validation**: Built-in drift detection
- **Production Ready**: Supports both SQLite (dev) and PostgreSQL (prod)

## Documentation System

### Automated ERD Generation

The project includes an advanced ERD generation system that creates comprehensive documentation:

```bash
# Generate all module ERDs
python scripts/generate_erd.py

# Generate specific module ERD
python scripts/generate_erd.py --module users

# Generate just the diagram (no tables)
python scripts/generate_erd.py --module auth --format mermaid
```

### Generated Documentation

The ERD generator creates:

1. **Module-specific ERDs** (`docs/developer/database/`)
   - Individual ERD files for each module
   - Cross-module relationship mapping
   - Detailed table descriptions
   - Constraint and foreign key documentation

2. **Comprehensive Table Information**
   - Column types and constraints
   - Primary and foreign keys
   - Unique constraints and indexes
   - Relationship mappings

3. **Interactive Navigation**
   - Index file with module overview
   - Cross-references between modules
   - Statistics and metadata

### Documentation Structure

```
docs/developer/
├── database-overview.md          # This file
├── database/                     # Auto-generated ERDs
│   ├── README.md                # Module index
│   ├── users-erd.md            # Users module ERD
│   ├── authentication-erd.md   # Authentication module ERD
│   ├── authorization-erd.md    # Authorization module ERD
│   ├── groups-erd.md           # Groups module ERD
│   └── items-erd.md            # Items module ERD
└── modules/
    └── common.md               # Common utilities documentation
```

## Key Database Features

### Security & Audit
- **Soft Deletes**: `is_deleted`, `deleted_at` fields
- **Audit Timestamps**: `created_at`, `updated_at` tracking  
- **Session Management**: Comprehensive session tracking with analytics
- **Activity Logging**: Detailed activity and audit trails

### Authentication & Authorization
- **Multi-Provider OAuth**: Support for multiple OAuth providers
- **TOTP/2FA**: Time-based one-time passwords with backup codes
- **Role-Based Access Control**: Flexible permission system
- **Password Security**: Secure password handling with reset tokens

### User Management
- **Profile Management**: Complete user profiles with verification
- **Group Management**: User groups with roles and permissions
- **Session Analytics**: Detailed session tracking and analytics
- **Device Tracking**: Device fingerprinting and security monitoring

## Development Workflow

### Schema Changes

1. **Modify Models**: Update SQLModel classes in `api/*/models.py`
2. **Generate Migration**: `python scripts/migrate.py create "description"`
3. **Review Migration**: Check generated migration file
4. **Apply Migration**: `python scripts/migrate.py upgrade`
5. **Update Documentation**: `python scripts/generate_erd.py`

### Best Practices

- Always review generated migrations before applying
- Use descriptive migration messages
- Test migrations on development data first
- Keep ERD documentation up-to-date
- Follow module naming conventions

### Testing

- **Migration Testing**: Automatic schema validation
- **Data Integrity**: Foreign key constraint validation
- **Performance**: Index usage analysis
- **Security**: Permission and access control testing

## Maintenance

### Regular Tasks

1. **Documentation Updates**: Re-run ERD generation after schema changes
2. **Migration Cleanup**: Archive old migration files periodically
3. **Schema Validation**: Run drift detection regularly
4. **Performance Analysis**: Monitor query performance and indexing

### Monitoring

- Database schema drift detection
- Migration status tracking
- Relationship integrity validation
- Documentation freshness checks

## Related Documentation

- [ERD Module Index](./database/README.md) - Complete module ERD documentation
- [Common Utilities](./modules/common.md) - Shared database utilities
- [Migration Guide](../../scripts/migrate.py) - Migration management script
- [ERD Generator](../../scripts/generate_erd.py) - Documentation generation tool

---

*This documentation is automatically maintained and updated as part of the database schema management process.*
