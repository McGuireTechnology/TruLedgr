# TruLedgr Developer Guide

A comprehensive technical guide for developers working on the TruLedgr Personal Finance Application.

## 🏗️ Architecture Overview

TruLedgr is built as a modern full-stack application with the following architecture:

- **Backend**: FastAPI (Python) with SQLModel ORM
- **Frontend**: Vue.js 3 with TypeScript and Composition API
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **State Management**: Pinia for Vue.js
- **Styling**: Tailwind CSS with custom components
- **Authentication**: Session-based with TOTP support
- **API**: RESTful API with OpenAPI/Swagger documentation

## 🚀 Development Setup

### Prerequisites

```bash
# Required versions
Python 3.8+
Node.js 16+
npm 8+
Git
```

### Initial Setup

```bash
# Clone repository
git clone https://github.com/McGuireTechnology/truledgr.git
cd truledgr

# Install Python dependencies
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev,docs]"

# Install Node.js dependencies
npm install

# Setup environment
cp .env.local.example .env
# Edit .env with your configuration
```

### Development Environment

```bash
# Option 1: Start all services
npm run dev

# Option 2: Start services individually
npm run dev:backend    # FastAPI on :8000
npm run dev:dashboard  # Vue.js on :5173
npm run dev:landing    # Landing page on :5174

# Option 3: Use VS Code tasks
# Ctrl+Shift+P -> "Tasks: Run Task" -> Choose task
```

## 📁 Project Structure Deep Dive

### Backend Structure (`/api`)

```
api/
├── main.py                 # FastAPI app factory and ASGI config
├── deps.py                 # Global dependencies and utilities
├── authentication/         # Authentication system
│   ├── deps.py            # Auth dependencies
│   ├── router.py          # Auth endpoints
│   ├── schemas.py         # Pydantic models
│   ├── service.py         # Business logic
│   ├── oauth2/            # OAuth2 implementation
│   ├── passwords/         # Password handling
│   ├── security/          # Security utilities
│   ├── sessions/          # Session management
│   ├── totp/             # TOTP implementation
│   └── utils/            # Auth utilities
├── authorization/         # RBAC system
│   ├── models.py         # Authorization models
│   ├── policy.py         # Permission policies
│   ├── router.py         # Authorization endpoints
│   └── service.py        # Authorization logic
├── common/               # Shared utilities
│   ├── contracts.py      # Interface definitions
│   ├── deps.py          # Common dependencies
│   ├── exceptions.py    # Custom exceptions
│   ├── models.py        # Base models
│   ├── types.py         # Custom types
│   └── utils.py         # Utility functions
├── db/                  # Database layer
│   ├── base.py         # Base model class
│   ├── deps.py         # DB dependencies
│   ├── seed.py         # Database seeding
│   └── session.py      # Session management
├── groups/             # Financial groups (households)
│   ├── crud.py        # Database operations
│   ├── models.py      # SQLModel models
│   ├── router.py      # API endpoints
│   ├── schemas.py     # Pydantic schemas
│   └── service.py     # Business logic
├── items/             # Financial transactions
│   ├── crud.py       # Database operations
│   ├── models.py     # SQLModel models
│   ├── router.py     # API endpoints
│   └── service.py    # Business logic
├── settings/          # Configuration
│   └── deps.py       # Settings dependencies
└── users/            # User management
    ├── crud.py      # Database operations
    ├── deps.py      # User dependencies
    ├── exceptions.py # User-specific exceptions
    ├── models.py    # SQLModel models
    ├── router.py    # API endpoints
    ├── schemas.py   # Pydantic schemas
    └── service.py   # Business logic
```

### Frontend Structure (`/dashboard`)

```
dashboard/
├── App.vue              # Root component
├── main.ts             # Vue app initialization
├── style.css          # Global styles
├── components/         # Reusable components
│   ├── ConfirmModal.vue
│   ├── groups/        # Group-specific components
│   ├── layout/        # Layout components
│   └── modals/        # Modal components
├── domains/           # Feature modules
│   ├── index.ts      # Domain exports
│   ├── authentication/ # Auth domain
│   ├── authorization/  # Authorization domain
│   ├── groups/        # Groups domain
│   └── users/         # Users domain
├── router/           # Vue Router configuration
│   └── index.ts
├── services/         # API services
│   ├── api.ts       # Base API client
│   ├── items.ts     # Items service
│   └── users.ts     # Users service
├── shared/          # Shared utilities
│   └── api.ts      # Shared API utilities
├── stores/         # Pinia stores
│   ├── auth.ts    # Authentication store
│   ├── groups.ts  # Groups store
│   └── users.ts   # Users store
├── types/         # TypeScript type definitions
├── utils/         # Utility functions
└── views/         # Page components
    ├── Dashboard.vue
    ├── Login.vue
    └── ...
```

## 🛠️ Development Workflows

### Adding a New Feature

1. **Backend Development**
   ```bash
   # 1. Create models
   # api/new_feature/models.py
   
   # 2. Create schemas
   # api/new_feature/schemas.py
   
   # 3. Create CRUD operations
   # api/new_feature/crud.py
   
   # 4. Create service layer
   # api/new_feature/service.py
   
   # 5. Create API router
   # api/new_feature/router.py
   
   # 6. Register router in main.py
   ```

2. **Frontend Development**
   ```bash
   # 1. Create domain module
   # dashboard/domains/new_feature/
   
   # 2. Create API service
   # dashboard/services/new_feature.ts
   
   # 3. Create Pinia store
   # dashboard/stores/new_feature.ts
   
   # 4. Create components
   # dashboard/components/new_feature/
   
   # 5. Create views
   # dashboard/views/NewFeature.vue
   
   # 6. Add routes
   # dashboard/router/index.ts
   ```

### Database Migrations

```bash
# Create new migration
python scripts/create_migration.py "description"

# Run migrations
python scripts/migrate_complete_schema.py

# Seed database
python -c "from api.db.seed import seed_database; seed_database()"
```

### Testing Workflow

```bash
# Backend tests
python -m pytest tests/ -v
python -m pytest tests/test_users.py -v
python -m pytest tests/test_auth_flows.py -v

# Frontend tests
npm run test:unit
npm run test:e2e

# Coverage reports
python -m pytest --cov=api tests/
npm run test:coverage
```

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=sqlite:///./dev.db
DATABASE_URL_ASYNC=sqlite+aiosqlite:///./dev.db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:5173", "http://localhost:5174"]

# Application
ENVIRONMENT=development
DEBUG=True
```

### Development Tools Configuration

#### VS Code Settings
```json
{
  "python.defaultInterpreterPath": "./.venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "editor.formatOnSave": true
}
```

#### Git Hooks (pre-commit)
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v2.6.2
    hooks:
      - id: prettier
```

## 🏛️ Architecture Patterns

### Backend Patterns

#### Repository Pattern
```python
# api/users/crud.py
class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, user_data: UserCreate) -> User:
        # Implementation
        pass
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        # Implementation
        pass
```

#### Service Layer Pattern
```python
# api/users/service.py
class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        # Business logic here
        user = await self.user_repo.create(user_data)
        return UserResponse.from_orm(user)
```

#### Dependency Injection
```python
# api/users/deps.py
async def get_user_service(
    session: AsyncSession = Depends(get_session)
) -> UserService:
    user_repo = UserRepository(session)
    return UserService(user_repo)

# api/users/router.py
@router.post("/users/")
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.create_user(user_data)
```

### Frontend Patterns

#### Composition API Pattern
```typescript
// composables/useFinancialData.ts
export function useFinancialData() {
  const transactions = ref<Transaction[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  const fetchTransactions = async () => {
    loading.value = true
    try {
      transactions.value = await api.getTransactions()
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }
  
  return {
    transactions: readonly(transactions),
    loading: readonly(loading),
    error: readonly(error),
    fetchTransactions
  }
}
```

#### Store Pattern (Pinia)
```typescript
// stores/financial.ts
export const useFinancialStore = defineStore('financial', () => {
  const transactions = ref<Transaction[]>([])
  const budget = ref<Budget | null>(null)
  
  const addTransaction = async (transaction: TransactionCreate) => {
    const newTransaction = await api.createTransaction(transaction)
    transactions.value.push(newTransaction)
  }
  
  const totalExpenses = computed(() => 
    transactions.value.reduce((sum, t) => sum + t.amount, 0)
  )
  
  return {
    transactions,
    budget,
    addTransaction,
    totalExpenses
  }
})
```

## 🧪 Testing Strategy

### Backend Testing

#### Unit Tests
```python
# tests/test_user_service.py
import pytest
from api.users.service import UserService
from api.users.schemas import UserCreate

@pytest.mark.asyncio
async def test_create_user(mock_user_repo):
    user_service = UserService(mock_user_repo)
    user_data = UserCreate(email="test@example.com", password="password")
    
    result = await user_service.create_user(user_data)
    
    assert result.email == "test@example.com"
    mock_user_repo.create.assert_called_once()
```

#### Integration Tests
```python
# tests/test_auth_integration.py
@pytest.mark.asyncio
async def test_login_flow(client):
    # Create user
    user_data = {"email": "test@example.com", "password": "password"}
    response = await client.post("/api/users/", json=user_data)
    assert response.status_code == 201
    
    # Login
    login_data = {"email": "test@example.com", "password": "password"}
    response = await client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
```

### Frontend Testing

#### Component Tests
```typescript
// tests/components/TransactionForm.test.ts
import { mount } from '@vue/test-utils'
import TransactionForm from '@/components/TransactionForm.vue'

describe('TransactionForm', () => {
  it('submits transaction data', async () => {
    const wrapper = mount(TransactionForm)
    
    await wrapper.find('#amount').setValue('100.00')
    await wrapper.find('#description').setValue('Test transaction')
    await wrapper.find('form').trigger('submit')
    
    expect(wrapper.emitted('submit')).toBeTruthy()
  })
})
```

## 🚀 Deployment

### Development Deployment

```bash
# Using Docker Compose
docker-compose up -d

# Manual deployment
./scripts/deploy.sh development
```

### Production Deployment

```bash
# Build for production
npm run build

# Deploy to server
./scripts/deploy.sh production

# Using Docker
docker build -t truledgr:latest .
docker run -p 8000:8000 truledgr:latest
```

### Environment-Specific Configurations

#### Development
```bash
# .env.dev
DATABASE_URL=sqlite:///./dev.db
DEBUG=True
LOG_LEVEL=DEBUG
```

#### Production
```bash
# .env.prod
DATABASE_URL=postgresql://user:pass@localhost/truledgr
DEBUG=False
LOG_LEVEL=INFO
SECURE_COOKIES=True
```

## 🐛 Debugging

### Backend Debugging

```python
# Add breakpoints in VS Code or use pdb
import pdb; pdb.set_trace()

# Logging
import logging
logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

### Frontend Debugging

```typescript
// Vue DevTools
// Browser DevTools
console.log('Debug info:', data)

// Vue 3 debugging
import { getCurrentInstance } from 'vue'
const instance = getCurrentInstance()
console.log(instance)
```

## 📚 API Documentation

### Interactive Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### API Testing
```bash
# Using curl
curl -X POST "http://localhost:8000/api/users/" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password"}'

# Using httpie
http POST localhost:8000/api/users/ email=test@example.com password=password
```

## 🔍 Performance Optimization

### Backend Optimization
- Database query optimization with SQLModel
- Async/await for I/O operations
- Caching with Redis (planned)
- Database connection pooling

### Frontend Optimization
- Vue 3 tree-shaking
- Lazy loading of components
- Code splitting with Vite
- Image optimization

## 🛡️ Security Considerations

### Backend Security
- Input validation with Pydantic
- SQL injection prevention with SQLModel
- CORS configuration
- Rate limiting (planned)
- Security headers

### Frontend Security
- XSS prevention
- CSRF tokens
- Secure cookie handling
- Input sanitization

## 📝 Code Style Guidelines

### Python (Backend)
- Follow PEP 8
- Use Black for formatting
- Use isort for imports
- Type hints required
- Docstrings for public functions

### TypeScript (Frontend)
- Follow TypeScript best practices
- Use Prettier for formatting
- ESLint for linting
- Composition API preferred
- Props and emits typing required

## 🤝 Contributing

### Pull Request Process
1. Fork the repository
2. Create feature branch
3. Write tests
4. Ensure all tests pass
5. Update documentation
6. Submit pull request

### Code Review Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code follows style guidelines
- [ ] No security vulnerabilities
- [ ] Performance considerations addressed

## 🆘 Troubleshooting

### Common Issues

#### Database Issues
```bash
# Reset database
rm dev.db
python scripts/migrate_complete_schema.py
```

#### Node.js Issues
```bash
# Clear cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

#### Python Environment Issues
```bash
# Recreate virtual environment
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,docs]"
```

## 📈 Monitoring and Logging

### Application Logging
```python
# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### Error Tracking
- Sentry integration (planned)
- Application metrics
- Performance monitoring

## 🔧 Development Tools

### Recommended VS Code Extensions
- Python
- Pylance
- Vetur/Volar (Vue.js)
- GitLens
- Thunder Client (API testing)
- Error Lens

### Useful Commands
```bash
# Database inspection
sqlite3 dev.db ".tables"
sqlite3 dev.db "SELECT * FROM users;"

# Log monitoring
tail -f logs/app.log

# Process monitoring
ps aux | grep python
ps aux | grep node
```

This developer guide provides comprehensive technical information for anyone working on the TruLedgr codebase, including architecture details, development workflows, testing strategies, and best practices.
