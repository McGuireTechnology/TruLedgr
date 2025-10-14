# Why Models & Mappers Live in `repositories/`

## The Question

Why are `models.py` and `mappers.py` located inside the `repositories/` directory instead of being separate top-level component types like `entities/` or `services/`?

## The Short Answer

**Models and mappers are infrastructure implementation details that exist solely to support repository implementations.** They have no purpose outside the context of repositories, so they're colocated with the code that uses them.

## The Long Answer

### 1. **Models and Mappers are Repository Implementation Details**

The repository interface (Protocol) defines **what** operations are available:

```python
# repositories/user.py (interface)
class UserRepository(Protocol):
    async def get_by_id(self, user_id: UserId) -> Optional[User]: ...
    async def create(self, user: User) -> User: ...
```

The models and mappers define **how** the repository is implemented:

```python
# repositories/models.py (implementation detail)
class UserModel(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)

# repositories/mappers.py (implementation detail)
class UserMapper:
    @staticmethod
    def to_entity(model: UserModel) -> User: ...

# repositories/repositories.py (uses models & mappers)
class SqlAlchemyUserRepository(UserRepository):
    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        model = self._session.query(UserModel).filter_by(id=str(user_id)).first()
        return UserMapper.to_entity(model) if model else None
```

**Key insight**: Models and mappers only exist because we're using SQLAlchemy as our persistence mechanism. If we switched to MongoDB, we'd have different models (documents) and different mappers, but they'd still live in `repositories/` because they're still repository implementation details.

### 2. **Encapsulation and Information Hiding**

By keeping models and mappers inside `repositories/`, we're saying:

> "These are internal implementation details. The rest of the application doesn't need to know about them."

**Good** (current structure):
```
repositories/
├── user.py              # Public interface (Protocol)
├── session.py           # Public interface (Protocol)
├── repositories.py      # Implementations (use models & mappers)
├── models.py           # Internal detail (database schema)
└── mappers.py          # Internal detail (conversion logic)
```

The domain layer and application services only depend on the interfaces (`user.py`, `session.py`). They never import from `models.py` or `mappers.py`.

**Bad** (hypothetical alternative):
```
api/
├── models/             # Separate top-level directory
│   └── user_model.py
├── mappers/            # Separate top-level directory
│   └── user_mapper.py
└── repositories/
    └── user.py
```

This structure implies models and mappers are first-class architectural components that other parts of the system might depend on. But they shouldn't be! Only repositories should use them.

### 3. **Cohesion: Things That Change Together Stay Together**

When you change how a repository persists data:
- You modify the **model** (database schema)
- You modify the **mapper** (conversion logic)
- You modify the **repository implementation** (queries)

All three changes happen **together** and are **related**. Keeping them in the same directory reflects this high cohesion.

**Example**: Adding a new field to User

```python
# repositories/models.py
class UserModel(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    email = Column(String)
    timezone = Column(String)  # NEW FIELD

# repositories/mappers.py
class UserMapper:
    @staticmethod
    def to_entity(model: UserModel) -> User:
        return User(
            id=UserId(model.id),
            email=EmailAddress(model.email),
            timezone=model.timezone  # NEW FIELD
        )

# repositories/repositories.py
class SqlAlchemyUserRepository(UserRepository):
    async def update(self, user: User) -> User:
        user_model.timezone = user.timezone  # NEW FIELD
```

All changes are localized to the `repositories/` directory. You don't have to hunt through multiple top-level directories.

### 4. **Clear Dependency Direction**

Our architecture follows the **Dependency Inversion Principle**:

```
entities/          (Domain - no dependencies)
   ↑
repositories/      (Interfaces - depend on domain)
   ↑
repositories/      (Implementations - depend on interfaces)
├── models.py      (Infrastructure - depend on SQLAlchemy)
└── mappers.py     (Infrastructure - depend on domain & models)
```

Models and mappers are at the **bottom** of the dependency hierarchy. They're the most "infrastructure-y" components. Putting them in a separate top-level directory would suggest they're at the same level as domain entities, which is incorrect.

### 5. **Replaceability and Plugin Architecture**

Imagine we want to support **multiple persistence mechanisms**:

```
repositories/
├── user.py                    # Interface (shared)
├── session.py                 # Interface (shared)
│
├── sqlalchemy/                # SQLAlchemy implementation
│   ├── repositories.py
│   ├── models.py
│   └── mappers.py
│
├── mongodb/                   # MongoDB implementation
│   ├── repositories.py
│   ├── documents.py          # MongoDB "models"
│   └── mappers.py
│
└── inmemory/                  # In-memory implementation (testing)
    ├── repositories.py
    └── store.py
```

Each persistence mechanism has its own models/mappers because they're **implementation-specific**. Keeping them colocated with their repository implementation makes this plugin architecture natural.

If models and mappers were top-level directories, how would you organize multiple implementations? It becomes awkward:

```
models/
├── sqlalchemy/
│   └── user_model.py
└── mongodb/
    └── user_document.py

mappers/
├── sqlalchemy/
│   └── user_mapper.py
└── mongodb/
    └── user_mapper.py

repositories/
├── sqlalchemy/
│   └── user_repository.py
└── mongodb/
    └── user_repository.py
```

This separates related components and makes it harder to understand what goes with what.

### 6. **The Repository Pattern is the Boundary**

In Clean Architecture, the repository is the **adapter** between domain and infrastructure:

```
┌─────────────────────────────────────────────────┐
│              DOMAIN LAYER                       │
│  entities/ + value_objects/                     │
│                                                  │
│  Repository Interfaces (protocols)              │
└──────────────────┬──────────────────────────────┘
                   │ Boundary
┌──────────────────▼──────────────────────────────┐
│         INFRASTRUCTURE LAYER                     │
│                                                   │
│  Repository Implementations                      │
│  ├── models.py (ORM)                            │
│  └── mappers.py (conversion)                    │
│                                                   │
│  Database                                        │
└──────────────────────────────────────────────────┘
```

Everything below the boundary (models, mappers, repositories) is infrastructure. Keeping them together in `repositories/` reinforces that they're all on the same side of the architectural boundary.

### 7. **Practical Considerations**

**Discoverability**: When debugging a repository issue, you want to see:
- The interface definition
- The implementation
- The database model
- The mapper

All in one place. You don't want to jump between `repositories/`, `models/`, and `mappers/` directories.

**Import paths**: With everything in `repositories/`:

```python
# Clear that these are all repository-related
from ..repositories import UserRepository
from ..repositories.models import UserModel
from ..repositories.mappers import UserMapper
from ..repositories.repositories import SqlAlchemyUserRepository
```

Versus scattered:

```python
# Unclear relationship
from ..repositories import UserRepository
from ..models import UserModel
from ..mappers import UserMapper
from ..repositories.implementations import SqlAlchemyUserRepository
```

## When Would Models/Mappers Be Separate?

There are scenarios where you **would** separate them:

### 1. **Shared Models Across Repositories**

If you have a complex database schema where models are shared:

```python
# Many-to-many relationships
class UserModel(Base): ...
class GroupModel(Base): ...
class UserGroupModel(Base):  # Join table used by both UserRepository and GroupRepository
    ...
```

Then having a separate `models/` directory makes sense because models aren't owned by a single repository.

### 2. **Complex Mapping Logic**

If mappers contain significant business logic or are reused across different contexts:

```python
# Mapper used by repository AND by external API clients
class UserMapper:
    @staticmethod
    def to_entity(data: dict) -> User:
        # Complex validation and transformation
        ...
    
    @staticmethod
    def to_legacy_format(user: User) -> dict:
        # Used by legacy API adapter
        ...
```

Then a separate `mappers/` directory might be justified.

### 3. **Code Generation**

If your models are generated from a schema (e.g., protobuf, GraphQL):

```
generated/
└── models/       # Generated from .proto files
```

Then keeping generated code separate makes sense.

## TruLedgr Decision

For TruLedgr, we keep models and mappers in `repositories/` because:

1. ✅ **Simple one-to-one mapping**: Each entity has one model
2. ✅ **No shared models**: Models aren't used across multiple repositories
3. ✅ **Mappers are simple**: Basic type conversion, no complex logic
4. ✅ **SQLAlchemy is the only persistence mechanism** (for now)
5. ✅ **Easier to navigate**: Related code stays together
6. ✅ **Clear architectural boundary**: Infrastructure is encapsulated

## Summary

**Models and mappers are implementation details of repositories, not first-class architectural components.** They exist solely to support repository implementations and have no purpose outside that context.

By keeping them in `repositories/`, we:
- Encapsulate infrastructure details
- Keep related code together
- Make dependencies clear
- Simplify navigation
- Support future plugin architectures

**Rule of thumb**: If a component only exists to support another component, colocate them. If a component has value independently, separate it.

Models and mappers have **no value** outside of repository implementations, so they belong in `repositories/`.
