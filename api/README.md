# TruLedgr API

FastAPI backend for TruLedgr personal finance application, following Domain-Driven Design, Clean Architecture, and Dependency Inversion principles.

## Architecture

This API follows a **type-based** organizational structure where components are grouped by their type (entities, repositories, services) rather than by architectural layer. This reduces nesting and makes the codebase more navigable.

### Project Structure

```
api/
├── entities/              # Domain entities (business objects with identity)
├── value_objects/         # Domain value objects (immutable values)
├── repositories/          # Repository patterns (interfaces & implementations)
│   ├── base.py           # UnitOfWork Protocol
│   ├── user.py           # UserRepository Protocol (interface)
│   ├── session.py        # SessionRepository Protocol (interface)
│   ├── repositories.py   # SQLAlchemy implementations
│   ├── models.py         # SQLAlchemy ORM models
│   └── mappers.py        # Entity ↔ Model converters
├── services/              # Domain & application services
├── routers/               # FastAPI endpoints (presentation)
├── schemas/               # Pydantic DTOs (API contracts)
├── config/                # Configuration
├── exceptions/            # Custom exceptions
├── utils/                 # Utilities
├── locales/               # Internationalization
├── tests/                 # Test suite
└── main.py               # FastAPI application entry
```

### Component Flow

```
Router (FastAPI)
   ↓
Schema (Pydantic DTO)
   ↓
Service (Use Case)
   ↓
Repository Interface (Protocol)
   ↑
Repository Implementation (SQLAlchemy)
   ↓
Mapper (Entity ↔ Model)
   ↓
Model (SQLAlchemy ORM)
   ↓
Database
```

## Design Principles

### Domain-Driven Design (DDD)
- **Entities** contain business logic and have identity
- **Value Objects** are immutable and self-validating
- **Repository Interfaces** define data access contracts
- **Domain Services** handle multi-entity business logic

### Clean Architecture
- **Dependencies flow inward**: Infrastructure → Domain
- **Domain is pure Python**: No framework dependencies
- **Abstractions are owned by domain**: Interfaces live with domain

### Dependency Inversion
- **Domain defines interfaces** (Protocols in `repositories/`)
- **Infrastructure provides implementations** (concrete classes)
- **High-level doesn't depend on low-level** details

## Key Concepts

### Repository Pattern

**Interface** (domain) - defines contract:
```python
# repositories/user.py
class UserRepository(Protocol):
    async def get_by_id(self, user_id: UserId) -> Optional[User]: ...
```

**Implementation** (infrastructure) - uses SQLAlchemy:
```python
# repositories/repositories.py
class SqlAlchemyUserRepository(UserRepository):
    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        model = self._session.query(UserModel).filter_by(id=str(user_id)).first()
        return UserMapper.to_entity(model) if model else None
```

### Entity vs Model Separation

**Entity** (domain) - business logic:
```python
# entities/user.py
class User:
    def __init__(self, id: UserId, email: EmailAddress):
        self.id = id
        self.email = email
    
    def change_email(self, new_email: EmailAddress):
        # Business validation
        self.email = new_email
```

**Model** (infrastructure) - database mapping:
```python
# repositories/models.py
class UserModel(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
```

**Mapper** bridges the two:
```python
# repositories/mappers.py
class UserMapper:
    @staticmethod
    def to_entity(model: UserModel) -> User:
        return User(id=UserId(model.id), email=EmailAddress(model.email))
    
    @staticmethod
    def to_model(entity: User) -> UserModel:
        return UserModel(id=str(entity.id), email=str(entity.email))
```

### Unit of Work Pattern

Manages transactions across multiple repositories:

```python
async with uow:
    user = await uow.users.get_by_email(email)
    session = await uow.sessions.create(session)
    await uow.commit()  # Atomic commit
```

## Development

### Running the API

```bash
# Activate Poetry environment
poetry shell

# Run development server
poetry run uvicorn api.main:app --reload

# API available at http://localhost:8000
# Documentation at http://localhost:8000/docs
```

### Adding a New Feature

1. **Create Entity** (`entities/`)
   - Define business logic
   - No database dependencies

2. **Create Value Objects** (`value_objects/`)
   - Immutable domain values
   - Self-validating

3. **Create Repository Interface** (`repositories/new_entity.py`)
   - Protocol defining data access
   - Use domain types

4. **Create Model** (`repositories/models.py`)
   - SQLAlchemy ORM model
   - Database schema

5. **Create Mapper** (`repositories/mappers.py`)
   - `to_entity()` method
   - `to_model()` method

6. **Create Implementation** (`repositories/repositories.py`)
   - Implement Protocol
   - Use mapper for conversions

7. **Update UnitOfWork** (`repositories/base.py`)
   - Add property to Protocol

8. **Create Service** (`services/`)
   - Orchestrate business workflow

9. **Create Schemas** (`schemas/`)
   - Define API DTOs

10. **Create Router** (`routers/`)
    - Define endpoints

## Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=api

# Run specific test file
poetry run pytest tests/test_users.py
```

### Test Strategy

- **Unit Tests**: Domain entities and value objects (no database)
- **Integration Tests**: Repository implementations (with test database)
- **End-to-End Tests**: API endpoints (full stack)

## Documentation

- **[Complete DDD & Clean Architecture Guide](../docs/architecture/ddd-clean-architecture.md)** - Detailed architectural patterns
- **[Architecture Summary](../docs/architecture/ARCHITECTURE_SUMMARY.md)** - Quick reference
- **[API Documentation](../docs/developer/architecture/api.md)** - API design and endpoints

## Dependencies

- **FastAPI**: Web framework
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation and schemas
- **Poetry**: Dependency management

## Configuration

Environment variables:
- `ALLOWED_ORIGINS`: Comma-separated CORS origins
- `DATABASE_URL`: Database connection string (future)
- `SECRET_KEY`: JWT signing key (future)

## License

Copyright © 2025 McGuire Technology, LLC
