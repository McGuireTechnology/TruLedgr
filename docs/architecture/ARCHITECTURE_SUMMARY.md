# TruLedgr API Architecture Summary

## Quick Reference

This document provides a quick overview of the TruLedgr API's architectural design. For detailed information, see the [complete DDD & Clean Architecture guide](ddd-clean-architecture.md).

## Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  routers/ (FastAPI endpoints) + schemas/ (Pydantic DTOs)    │
│                            ↓                                 │
├─────────────────────────────────────────────────────────────┤
│                    APPLICATION LAYER                         │
│         services/ (Use cases & orchestration)                │
│                            ↓                                 │
├─────────────────────────────────────────────────────────────┤
│                      DOMAIN LAYER                            │
│  entities/ + value_objects/ + repositories/ (interfaces)    │
│                            ↑                                 │
├─────────────────────────────────────────────────────────────┤
│                  INFRASTRUCTURE LAYER                        │
│    repositories/repositories.py (implementations)            │
│    repositories/models.py (SQLAlchemy ORM)                   │
│    repositories/mappers.py (Entity ↔ Model)                  │
└─────────────────────────────────────────────────────────────┘
```

## Component Directory

| Component | Location | Purpose | Dependencies |
|-----------|----------|---------|--------------|
| **Entities** | `entities/` | Business objects with identity | None (pure Python) |
| **Value Objects** | `value_objects/` | Immutable domain values | None (pure Python) |
| **Repository Interfaces** | `repositories/*.py` (Protocols) | Data access contracts | Entities, Value Objects |
| **Repository Implementations** | `repositories/repositories.py` | SQLAlchemy concrete repos | Interfaces, Models, Mappers |
| **Models** | `repositories/models.py` | SQLAlchemy ORM tables | SQLAlchemy only |
| **Mappers** | `repositories/mappers.py` | Entity ↔ Model conversion | Entities, Models, Value Objects |
| **Services** | `services/` | Business logic orchestration | Entities, Repositories |
| **Schemas** | `schemas/` | API DTOs (Pydantic) | Entities (for conversion) |
| **Routers** | `routers/` | FastAPI endpoints | Services, Schemas |

## Design Principles

### 💡 The Golden Rule

> **If a component only exists to support another component, colocate them. If a component has value independently, separate it.**

This principle guides our organizational decisions—for example, models and mappers live in `repositories/` because they exist solely to support repository implementations. See [detailed explanation](MODELS_MAPPERS_LOCATION.md).

### 1. Domain-Driven Design (DDD)
- Business logic lives in `entities/` and `value_objects/`
- Domain is framework-agnostic (no FastAPI, no SQLAlchemy)
- Ubiquitous language shared across codebase

### 2. Clean Architecture
- Dependencies point inward toward domain
- Domain layer at the center, knows nothing about outer layers
- Infrastructure depends on domain, not vice versa

### 3. Dependency Inversion
- Domain defines repository **interfaces** (Protocols)
- Infrastructure provides repository **implementations**
- High-level policy not dependent on low-level details

## Component Responsibilities

### Domain Layer (Core Business Logic)

#### Entities (`entities/`)
```python
# Example: User entity with business logic
class User:
    def __init__(self, id: UserId, email: EmailAddress):
        self.id = id
        self.email = email
    
    def change_email(self, new_email: EmailAddress):
        # Business validation here
        if not new_email.is_valid():
            raise InvalidEmailError()
        self.email = new_email
```

#### Value Objects (`value_objects/`)
```python
# Example: Email address with validation
@dataclass(frozen=True)
class EmailAddress:
    value: str
    
    def __post_init__(self):
        if not self._is_valid_email(self.value):
            raise ValueError(f"Invalid email: {self.value}")
    
    def __str__(self) -> str:
        return self.value
```

#### Repository Interfaces (`repositories/`)
```python
# Example: Repository protocol (interface)
class UserRepository(Protocol):
    async def get_by_id(self, user_id: UserId) -> Optional[User]: ...
    async def create(self, user: User) -> User: ...
```

### Infrastructure Layer (Database & External Concerns)

#### Models (`repositories/models.py`)
```python
# Example: SQLAlchemy ORM model
class UserModel(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
```

#### Mappers (`repositories/mappers.py`)
```python
# Example: Bidirectional mapper
class UserMapper:
    @staticmethod
    def to_entity(model: UserModel) -> User:
        return User(
            id=UserId(model.id),
            email=EmailAddress(model.email)
        )
    
    @staticmethod
    def to_model(entity: User) -> UserModel:
        return UserModel(
            id=str(entity.id),
            email=str(entity.email)
        )
```

#### Repository Implementations (`repositories/repositories.py`)
```python
# Example: Concrete SQLAlchemy repository
class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: DatabaseSession):
        self._session = session
    
    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        model = self._session.query(UserModel).filter(
            UserModel.id == str(user_id)
        ).first()
        return UserMapper.to_entity(model) if model else None
```

### Application Layer (Use Cases)

#### Services (`services/`)
```python
# Example: Application service orchestrating domain
class RegisterUserService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
    
    async def execute(self, email: str, password: str) -> User:
        async with self.uow:
            # Check if user exists
            existing = await self.uow.users.get_by_email(EmailAddress(email))
            if existing:
                raise UserAlreadyExistsError()
            
            # Create new user (domain entity)
            user = User.create(email=EmailAddress(email))
            
            # Persist via repository
            user = await self.uow.users.create(user)
            
            # Commit transaction
            await self.uow.commit()
            
            return user
```

### Presentation Layer (API)

#### Schemas (`schemas/`)
```python
# Example: API DTO with conversion
class UserResponse(BaseModel):
    id: str
    email: str
    
    @classmethod
    def from_entity(cls, user: User) -> "UserResponse":
        return cls(
            id=str(user.id),
            email=str(user.email)
        )
```

#### Routers (`routers/`)
```python
# Example: FastAPI endpoint
@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    request: CreateUserRequest,
    service: RegisterUserService = Depends(get_register_service)
):
    user = await service.execute(request.email, request.password)
    return UserResponse.from_entity(user)
```

## Data Flow Example

```
1. HTTP Request → Router
2. Router validates request with Schema (Pydantic)
3. Router calls Application Service
4. Service creates Domain Entity with business rules
5. Service uses Repository Interface to persist
6. Repository Implementation converts Entity → Model (via Mapper)
7. Model saved to database (SQLAlchemy)
8. Database returns Model with ID
9. Repository converts Model → Entity (via Mapper)
10. Service returns Entity to Router
11. Router converts Entity → Schema (DTO)
12. HTTP Response sent to client
```

## Key Benefits

| Benefit | Description |
|---------|-------------|
| **Testability** | Domain logic testable without database or API framework |
| **Flexibility** | Can swap SQLAlchemy for MongoDB, FastAPI for Flask |
| **Maintainability** | Clear separation of concerns, easy to locate code |
| **Team Collaboration** | Different teams work on different layers independently |
| **Scalability** | Add features without modifying existing code (Open/Closed) |

## Anti-Patterns to Avoid

❌ **DON'T**: Import SQLAlchemy in domain entities
```python
from sqlalchemy import Column  # NO! Domain should be framework-agnostic
```

❌ **DON'T**: Return ORM models from repositories
```python
async def get_user() -> UserModel:  # NO! Return domain entity
```

❌ **DON'T**: Put business logic in routers
```python
@router.post("/users")
async def create(email: str):
    if not email.endswith("@company.com"):  # NO! Use domain entity
```

❌ **DON'T**: Expose domain entities directly in API
```python
async def get_user() -> User:  # NO! Use DTO/Schema
```

## Quick Decision Tree

**Where should this code go?**

```
Is it a business rule or validation?
  └─ YES → Entity or Value Object (entities/, value_objects/)

Does it orchestrate multiple entities?
  └─ YES → Domain Service (services/)

Does it define a use case workflow?
  └─ YES → Application Service (services/)

Does it persist data?
  └─ YES → Repository Implementation (repositories/repositories.py)

Does it represent a database table?
  └─ YES → Model (repositories/models.py)

Does it convert between layers?
  └─ YES → Mapper (repositories/mappers.py)

Is it an HTTP endpoint?
  └─ YES → Router (routers/)

Is it API input/output?
  └─ YES → Schema (schemas/)
```

## Getting Started

1. **Read**: [Complete DDD & Clean Architecture Guide](ddd-clean-architecture.md)
2. **Explore**: Check existing files in `repositories/user.py` (interface) and `repositories/repositories.py` (implementation)
3. **Implement**: Follow the pattern when adding new features
4. **Test**: Write unit tests for domain logic without database

## Questions?

- See [complete guide](ddd-clean-architecture.md) for detailed explanations
- Check sequence diagrams for request flow
- Review anti-patterns section to avoid common mistakes
