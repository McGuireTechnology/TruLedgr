# Component Colocation Analysis

## 💡 Applying The Golden Rule

> **If a component only exists to support another component, colocate them. If a component has value independently, separate it.**

## Current Structure Analysis

### ✅ Already Correctly Colocated

**`repositories/`** - Well organized!
```
repositories/
├── models/          ✅ Colocated (only used by repositories)
├── mappers/         ✅ Colocated (only used by repositories)
├── repositories.py  
├── user.py         (interface)
├── session.py      (interface)
└── base.py         (UnitOfWork)
```
**Status**: Perfect! Models and mappers exist solely to support repository implementations.

---

## Components That Should Be Colocated

### 1. **Schemas with Routers** ⚠️ CONSIDER

**Current**:
```
api/
├── routers/
│   ├── auth.py
│   └── users.py
└── schemas/
    └── __init__.py
```

**Analysis**:
- Schemas (Pydantic DTOs) define request/response contracts for API endpoints
- Each router typically has its own request/response schemas
- Question: Are schemas used by multiple routers, or are they router-specific?

**Decision Matrix**:

✅ **Colocate if**:
- Schemas are 1:1 with routers (AuthRouter → AuthSchemas)
- Schemas aren't reused across routers
- No other layers depend on schemas (services don't use them)

❌ **Keep separate if**:
- Schemas are shared across multiple routers
- Services or other layers use schemas
- You want API contracts separate from implementation

**Recommendation**: **Keep separate for TruLedgr** because:
- Schemas represent the API contract (documentation value)
- May want to version schemas independently
- Could be shared across routers
- Enables API-first development

**Alternative Structure** (if you want colocation):
```
routers/
├── auth/
│   ├── router.py      # FastAPI routes
│   └── schemas.py     # Request/response DTOs
└── users/
    ├── router.py
    └── schemas.py
```

---

### 2. **Dependencies/Middleware with Routers** ❓ MAYBE

**Potential Issue**:
- FastAPI dependencies (like `Depends(get_current_user)`) are often router-specific
- Middleware might be application-wide

**Current Pattern** (assumed):
```
api/
├── routers/
│   └── auth.py
└── dependencies/    # (if it exists)
    └── auth.py
```

**Analysis**:

✅ **Colocate if**:
- Dependencies are only used by specific routers
- Each router has unique dependencies

❌ **Keep separate if**:
- Dependencies are shared across multiple routers
- They represent reusable components

**Recommendation**: **Keep separate** because dependencies like `get_current_user` are likely used by multiple routers.

---

### 3. **Test Files with Components** ⚠️ STRONGLY CONSIDER

**Current** (typical):
```
api/
├── entities/
│   └── user.py
├── repositories/
│   └── repositories.py
└── tests/
    ├── test_entities.py
    ├── test_repositories.py
    └── test_services.py
```

**Alternative** (colocated):
```
api/
├── entities/
│   ├── user.py
│   └── test_user.py          # ✅ Tests next to implementation
├── repositories/
│   ├── repositories.py
│   └── test_repositories.py  # ✅ Tests next to implementation
└── services/
    ├── auth.py
    └── test_auth.py           # ✅ Tests next to implementation
```

**Benefits of Colocation**:
- ✅ Tests and implementation visible together
- ✅ When you modify code, test is right there
- ✅ Refactoring moves test with code
- ✅ Clear 1:1 relationship

**Benefits of Separation**:
- ✅ Tests don't clutter production code directory
- ✅ Easy to exclude from distribution (`tests/` in gitignore)
- ✅ Separate test configuration
- ✅ Traditional Python convention

**Recommendation**: **Personal preference**, but modern trend is toward colocation. Consider:
```
api/
├── entities/
│   ├── __init__.py
│   ├── user.py
│   └── user_test.py         # or test_user.py
└── tests/                    # Only for integration/e2e tests
    ├── integration/
    └── e2e/
```

---

### 4. **Service-Specific Exceptions** ⚠️ CONSIDER

**Current**:
```
api/
├── services/
│   └── auth.py
└── exceptions/
    ├── auth_exceptions.py
    ├── user_exceptions.py
    └── domain_exceptions.py
```

**Analysis**:

✅ **Colocate if**:
- Exceptions are specific to one service/module
- Exception is an implementation detail

❌ **Keep separate if**:
- Exceptions are part of domain model (domain exceptions)
- Exceptions are raised by multiple components
- Exceptions are in public API contract

**Recommendation**: **Hybrid approach**:
```
api/
├── exceptions/
│   ├── domain.py          # Shared domain exceptions
│   └── base.py           # Base exception classes
├── services/
│   └── auth/
│       ├── service.py
│       └── exceptions.py  # Auth-specific exceptions
└── repositories/
    └── exceptions.py      # Repository-specific exceptions
```

Or **keep separate** if exceptions are part of your domain model and used across layers.

---

## Components That Should NOT Be Colocated

### ❌ 1. **Entities with Anything Else**

**Current** (correct):
```
api/
├── entities/
│   └── user.py
```

**Why NOT colocate**:
- Entities are **pure domain** - framework-agnostic
- Used by repositories, services, schemas, etc.
- Represent core business concepts
- Should have no dependencies on infrastructure

**Status**: ✅ **Keep as-is**

---

### ❌ 2. **Value Objects with Anything Else**

**Current** (correct):
```
api/
├── value_objects/
│   └── ids.py
```

**Why NOT colocate**:
- Value objects are **shared domain primitives**
- Used across entities, repositories, services
- Represent fundamental domain concepts
- Must remain independent

**Status**: ✅ **Keep as-is**

---

### ❌ 3. **Config with Anything Else**

**Current** (correct):
```
api/
├── config/
```

**Why NOT colocate**:
- Configuration is **application-wide**
- Used by all layers
- Should be centralized
- Environment-specific

**Status**: ✅ **Keep as-is**

---

### ❌ 4. **Utils with Anything Else**

**Current** (correct):
```
api/
├── utils/
```

**Why NOT colocate**:
- Utils are **shared helpers**
- Used across multiple components
- Generic, reusable functions
- No single "owner"

**Status**: ✅ **Keep as-is**

---

## Special Case: Services Structure

### Current Issue in `auth.py`:

```python
from ..domain.entities import User  # ❌ No domain/ directory
from .models import UserModel        # ❌ models is in repositories/
from .mappers import UserMapper      # ❌ mappers is in repositories/
```

**Problems**:
1. Services importing models/mappers (infrastructure details)
2. Services bypassing repository abstraction
3. Services directly using SQLAlchemy session

**Should Be**:
```python
# services/auth.py
from ..entities import User
from ..value_objects import UserId, EmailAddress
from ..repositories import UserRepository  # Use interface!
```

**Recommendation**: **Refactor services to use repositories, not models directly**

---

## Recommended Structure for TruLedgr

```
api/
├── entities/              ✅ Independent (domain core)
├── value_objects/         ✅ Independent (domain core)
│
├── repositories/          ✅ Correctly colocated
│   ├── models/           ✅ Only used by repositories
│   ├── mappers/          ✅ Only used by repositories
│   ├── user.py          (interface)
│   ├── repositories.py  (implementations)
│   └── base.py          (UnitOfWork)
│
├── services/              ✅ Independent (orchestration)
│   ├── auth.py
│   ├── user.py
│   └── session.py
│
├── routers/               ✅ Independent (presentation)
│   ├── auth.py
│   └── users.py
│
├── schemas/               ✅ Independent (API contracts)
│   ├── auth.py
│   └── users.py
│
├── exceptions/            ✅ Independent (shared)
├── config/                ✅ Independent (shared)
├── utils/                 ✅ Independent (shared)
├── locales/               ✅ Independent (i18n)
└── tests/                 ⚠️ Consider colocation
    ├── unit/
    ├── integration/
    └── e2e/
```

---

## Summary: Colocation Decisions

| Component | Should Colocate? | Reasoning |
|-----------|------------------|-----------|
| **models/** | ✅ YES (in repositories/) | Only used by repository implementations |
| **mappers/** | ✅ YES (in repositories/) | Only used by repository implementations |
| **schemas/** | ❌ NO | API contracts, may be shared, independent value |
| **tests/** | ⚠️ MAYBE | Personal preference, modern trend is colocation |
| **exceptions/** | ⚠️ MAYBE | If service-specific, yes; if domain, no |
| **dependencies/** | ❌ NO | Shared across routers |
| **entities/** | ❌ NO | Core domain, used everywhere |
| **value_objects/** | ❌ NO | Shared primitives, used everywhere |
| **config/** | ❌ NO | Application-wide settings |
| **utils/** | ❌ NO | Shared helpers |

---

## Action Items

### 1. ✅ Already Done
- [x] Models colocated with repositories
- [x] Mappers colocated with repositories

### 2. 🔧 Fix Import Issues
- [ ] Update `services/auth.py` to use repositories instead of models/mappers
- [ ] Remove direct SQLAlchemy usage from services
- [ ] Ensure services only depend on domain and repository interfaces

### 3. 🤔 Consider (Optional)
- [ ] Colocate unit tests with components they test
- [ ] Create service-specific exception modules if needed
- [ ] Organize routers into feature directories if they grow large

### 4. 📝 Document
- [ ] Add colocation decisions to architecture documentation
- [ ] Explain why schemas remain separate (API contract value)
- [ ] Document test organization strategy

---

## The Golden Rule in Practice

**Examples from TruLedgr**:

✅ **GOOD**: Models in repositories/
```
repositories/
├── models/           # Only repositories use these
└── repositories.py   # Uses models internally
```

✅ **GOOD**: Mappers in repositories/
```
repositories/
├── mappers/          # Only repositories use these
└── repositories.py   # Uses mappers internally
```

❌ **BAD**: Services importing models
```python
# services/auth.py
from .models import UserModel  # ❌ Violates abstraction!
```

✅ **GOOD**: Services using repositories
```python
# services/auth.py
from ..repositories import UserRepository  # ✅ Uses interface!
```

---

## Questions to Ask for Future Components

When adding a new component, ask:

1. **Is this component used by only one other component?**
   - YES → Colocate them
   - NO → Keep separate

2. **Does this component represent infrastructure for another?**
   - YES → Colocate with what it supports
   - NO → Keep separate

3. **Would other parts of the system benefit from this component?**
   - YES → Keep separate (shared)
   - NO → Colocate

4. **Is this component part of the domain model?**
   - YES → Keep separate (entities, value objects)
   - NO → Consider colocation

5. **Does this component have independent value?**
   - YES → Keep separate
   - NO → Colocate with its consumer

---

**Remember**: The goal is **discoverability** and **maintainability**, not rigid rules. If colocation makes the code easier to understand and maintain, do it. If separation provides clarity, do that instead.
