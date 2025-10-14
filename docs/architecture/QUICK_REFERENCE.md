# TruLedgr API Architecture Quick Reference

## 💡 The Golden Rule

> **If a component only exists to support another component, colocate them.**
> 
> **If a component has value independently, separate it.**

---

## Component Organization

```
api/
├── entities/              ← Domain entities (business objects)
├── value_objects/         ← Immutable domain values
├── repositories/          ← Repository interfaces + implementations
│   ├── user.py           ← UserRepository Protocol (interface)
│   ├── repositories.py   ← SQLAlchemy implementations
│   ├── models.py         ← Database models (colocated!)
│   └── mappers.py        ← Entity ↔ Model converters (colocated!)
├── services/              ← Business logic orchestration
├── routers/               ← FastAPI endpoints
├── schemas/               ← API DTOs (Pydantic)
├── config/                ← Configuration
├── exceptions/            ← Custom exceptions
└── utils/                 ← Shared utilities
```

### Why models & mappers are in repositories/

✅ **Colocated** because they only exist to support repository implementations  
✅ **Encapsulated** - rest of app doesn't need to know about them  
✅ **Change together** - when persistence changes, all three update  
✅ **Clear boundary** - everything in `repositories/` is infrastructure  

See: [Why Models & Mappers Live in repositories/](MODELS_MAPPERS_LOCATION.md)

---

## Dependency Flow

```
┌─────────────────────────────────────────┐
│     Presentation (routers/, schemas/)    │
│              Depends on ↓                │
├─────────────────────────────────────────┤
│      Application (services/)             │
│              Depends on ↓                │
├─────────────────────────────────────────┤
│   Domain (entities/, value_objects/)     │
│   + Repository Interfaces (protocols)    │
│              Depended on by ↑            │
├─────────────────────────────────────────┤
│      Infrastructure (repositories/)      │
│   - Repository implementations           │
│   - Models (colocated)                   │
│   - Mappers (colocated)                  │
└─────────────────────────────────────────┘
```

**Rule**: Dependencies point **inward** toward domain

---

## Quick Decision Tree

**"Where does this code go?"**

```
Is it a business rule or entity behavior?
  └─ YES → entities/ or value_objects/

Is it a repository data access contract?
  └─ YES → repositories/user.py (Protocol interface)

Is it a database table structure?
  └─ YES → repositories/models.py (ORM model)

Does it convert between entity and model?
  └─ YES → repositories/mappers.py (mapper)

Does it implement a repository?
  └─ YES → repositories/repositories.py (concrete class)

Does it orchestrate business logic?
  └─ YES → services/ (domain or application service)

Is it an HTTP endpoint?
  └─ YES → routers/ (FastAPI route)

Is it API input/output?
  └─ YES → schemas/ (Pydantic DTO)

Is it a configuration setting?
  └─ YES → config/

Is it a custom error type?
  └─ YES → exceptions/

Is it a shared utility?
  └─ YES → utils/
```

---

## Component Purposes (One-Liner)

| Component | Purpose |
|-----------|---------|
| **entities/** | Business objects with identity and behavior |
| **value_objects/** | Immutable, self-validating domain values |
| **repositories/** (interfaces) | Data access contracts defined by domain |
| **repositories/models.py** | SQLAlchemy ORM database tables |
| **repositories/mappers.py** | Entity ↔ Model bidirectional converters |
| **repositories/repositories.py** | Concrete SQLAlchemy implementations |
| **services/** | Business logic orchestration and use cases |
| **routers/** | FastAPI HTTP endpoints |
| **schemas/** | Pydantic API request/response DTOs |
| **config/** | Environment and configuration management |
| **exceptions/** | Custom domain and application exceptions |
| **utils/** | Shared helper functions |

---

## Anti-Patterns (Don't Do This!)

❌ **DON'T**: Import SQLAlchemy in domain entities
```python
from sqlalchemy import Column  # NO! Domain = framework-agnostic
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

❌ **DON'T**: Expose domain entities in API
```python
async def get_user() -> User:  # NO! Use DTO/Schema
```

❌ **DON'T**: Create top-level models/ or mappers/ directories
```
api/
├── models/      # NO! These belong in repositories/
├── mappers/     # NO! These belong in repositories/
```

---

## Patterns (Do This!)

✅ **DO**: Keep domain pure Python
```python
# entities/user.py
class User:
    def __init__(self, id: UserId, email: EmailAddress):
        self.id = id
        self.email = email
```

✅ **DO**: Return domain entities from repositories
```python
async def get_user(user_id: UserId) -> Optional[User]:
    model = self._session.query(UserModel).filter_by(id=str(user_id)).first()
    return UserMapper.to_entity(model) if model else None
```

✅ **DO**: Put business logic in domain
```python
# entities/user.py
class User:
    def change_email(self, new_email: EmailAddress):
        if not new_email.is_valid():
            raise InvalidEmailError()
        self.email = new_email
```

✅ **DO**: Use DTOs for API contracts
```python
@router.get("/users/{id}")
async def get_user(id: str) -> UserResponse:
    user = await repo.get_by_id(UserId(id))
    return UserResponse.from_entity(user)
```

✅ **DO**: Colocate implementation details
```
repositories/
├── repositories.py   # Implementation
├── models.py        # Implementation detail (colocated)
└── mappers.py       # Implementation detail (colocated)
```

---

## Key Principles

1. **Domain-Driven Design**: Business logic in pure Python domain models
2. **Clean Architecture**: Dependencies flow inward toward domain
3. **Dependency Inversion**: Domain defines interfaces; infrastructure implements
4. **Repository Pattern**: Abstract data access through Protocols
5. **Unit of Work**: Atomic transactions across repositories
6. **Separation of Concerns**: Each component has one clear responsibility
7. **Encapsulation**: Hide implementation details
8. **Cohesion**: Things that change together stay together

---

## Test Strategy

```
Unit Tests          → Test domain (entities, value objects, services)
                      No database, no framework dependencies

Integration Tests   → Test repositories with real database
                      Test mappers (entity ↔ model conversion)

End-to-End Tests   → Test API endpoints (full stack)
```

---

## Adding a New Feature (Checklist)

- [ ] 1. Create **entity** in `entities/`
- [ ] 2. Create **value objects** in `value_objects/`
- [ ] 3. Create **repository interface** (Protocol) in `repositories/new_entity.py`
- [ ] 4. Create **model** (SQLAlchemy) in `repositories/models.py`
- [ ] 5. Create **mapper** in `repositories/mappers.py`
- [ ] 6. Create **repository implementation** in `repositories/repositories.py`
- [ ] 7. Update **UnitOfWork** in `repositories/base.py`
- [ ] 8. Create **service** in `services/`
- [ ] 9. Create **schemas** (DTOs) in `schemas/`
- [ ] 10. Create **router** in `routers/`
- [ ] 11. Write **tests**

---

## Resources

- 📖 [Complete DDD & Clean Architecture Guide](ddd-clean-architecture.md)
- 📋 [Architecture Summary](ARCHITECTURE_SUMMARY.md)
- 🤔 [Why Models & Mappers Live in repositories/](MODELS_MAPPERS_LOCATION.md)
- � [Component Colocation Analysis](COLOCATION_ANALYSIS.md)
- �🚀 [API README](../api/README.md)

---

**Remember**: Code organization should reflect the problem domain, not the technical framework.
