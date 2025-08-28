# Development Overview

Welcome to the TruLedgr developer documentation! This section provides comprehensive technical information for developers who want to contribute to, extend, or deploy TruLedgr.

## 🏗️ Architecture Overview

TruLedgr is built as a modern, full-stack personal finance application with a clear separation of concerns and scalable architecture.

### Technology Stack

#### Backend
- **Framework**: FastAPI (Python 3.8+)
- **Database**: SQLite (development) / PostgreSQL (production)
- **ORM**: SQLModel (built on SQLAlchemy + Pydantic)
- **Authentication**: Session-based with TOTP support
- **API**: RESTful with OpenAPI/Swagger documentation
- **Async**: Full async/await support for I/O operations

#### Frontend
- **Framework**: Vue.js 3 with Composition API
- **Language**: TypeScript for type safety
- **Build Tool**: Vite for fast development and builds
- **State Management**: Pinia for reactive state
- **Styling**: Tailwind CSS with custom components
- **Charts**: Chart.js for financial visualizations

#### Development Tools
- **Package Management**: pip (Python), npm (Node.js)
- **Code Quality**: Black, isort, Pylint (Python), ESLint, Prettier (TypeScript)
- **Testing**: pytest (backend), Vitest (frontend)
- **Documentation**: MkDocs with Material theme

### System Architecture

```mermaid
graph TB
    Client[Web Browser] --> Frontend[Vue.js Frontend]
    Frontend --> API[FastAPI Backend]
    API --> Database[(SQLite/PostgreSQL)]
    API --> Auth[Authentication Service]
    API --> Files[File Storage]
    
    subgraph "Frontend Layer"
        Frontend --> Router[Vue Router]
        Frontend --> Store[Pinia Store]
        Frontend --> Components[Vue Components]
    end
    
    subgraph "Backend Layer"
        API --> Routes[API Routes]
        Routes --> Services[Business Logic]
        Services --> Models[Database Models]
        Services --> Auth
    end
```

### Design Principles

#### Backend Principles
- **Clean Architecture**: Clear separation between layers
- **Domain-Driven Design**: Business logic organized by domain
- **Dependency Injection**: Testable and maintainable code
- **API-First**: OpenAPI specification drives development
- **Security by Default**: Authentication and authorization built-in

#### Frontend Principles
- **Component-Based**: Reusable, testable components
- **Type Safety**: TypeScript for compile-time error detection
- **Reactive State**: Pinia for predictable state management
- **Progressive Enhancement**: Works without JavaScript for core features
- **Mobile-First**: Responsive design for all screen sizes

## 🎯 Development Philosophy

### Code Quality Standards

#### Python (Backend)
- **PEP 8 Compliance**: Standard Python style guide
- **Type Hints**: Full type annotations for better IDE support
- **Docstrings**: Comprehensive documentation for all public functions
- **Unit Testing**: High test coverage with pytest
- **Async Best Practices**: Proper async/await usage

#### TypeScript (Frontend)
- **Strict TypeScript**: Enabled strict mode for maximum type safety
- **Composition API**: Preferred over Options API for Vue components
- **Props Validation**: Runtime validation for component props
- **ESLint Rules**: Comprehensive linting for code consistency
- **Component Testing**: Unit tests for critical components

### Security First

#### Authentication & Authorization
- **Session-Based Auth**: Secure HTTP-only cookies
- **Password Security**: Argon2 hashing with salt
- **Two-Factor Auth**: TOTP support for enhanced security
- **Role-Based Access**: Granular permissions system

#### Data Protection
- **Input Validation**: Pydantic models for API validation
- **SQL Injection Prevention**: SQLModel parameterized queries
- **XSS Protection**: Content Security Policy headers
- **CORS Configuration**: Restricted cross-origin requests

### Performance Optimization

#### Backend Performance
- **Async Operations**: Non-blocking I/O for database operations
- **Connection Pooling**: Efficient database connection management
- **Query Optimization**: Eager loading and query optimization
- **Caching Strategy**: Redis for session and data caching (planned)

#### Frontend Performance
- **Code Splitting**: Lazy loading of route components
- **Tree Shaking**: Remove unused code from bundles
- **Image Optimization**: WebP format with fallbacks
- **Bundle Analysis**: Regular bundle size monitoring

## 🚀 Getting Started for Developers

### Prerequisites

Before you begin development, ensure you have:

```bash
# Required Software
Python 3.8+          # Backend development
Node.js 16+          # Frontend development  
Git                  # Version control
VS Code              # Recommended IDE (optional)

# Recommended Tools
Docker               # Containerization (optional)
PostgreSQL           # Production database (optional)
Redis                # Caching (planned feature)
```

### Development Environment Setup

Quick setup for new developers:

1. **Clone the Repository**
   ```bash
   git clone https://github.com/McGuireTechnology/truledgr.git
   cd truledgr
   ```

2. **Backend Setup**
   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   
   # Install dependencies
   pip install -e ".[dev,docs]"
   
   # Initialize database
   python scripts/migrate_complete_schema.py
   ```

3. **Frontend Setup**
   ```bash
   # Install Node.js dependencies
   npm install
   
   # Start development server
   npm run dev:dashboard
   ```

4. **Environment Configuration**
   ```bash
   # Copy environment template
   cp .env.local.example .env
   
   # Edit .env with your settings
   # Key variables: DATABASE_URL, SECRET_KEY
   ```

### Project Structure Deep Dive

#### Backend Structure (`/api`)

```
api/
├── main.py                 # FastAPI app factory
├── deps.py                 # Global dependencies
├── authentication/         # Auth system
│   ├── router.py          # Auth endpoints
│   ├── service.py         # Auth business logic
│   ├── models.py          # Auth database models
│   └── schemas.py         # Pydantic request/response models
├── users/                 # User management
├── groups/                # Household/family groups
├── items/                 # Financial transactions
├── common/                # Shared utilities
├── db/                    # Database configuration
└── settings/              # Application settings
```

#### Frontend Structure (`/dashboard`)

```
dashboard/
├── main.ts                # Vue app initialization
├── App.vue               # Root component
├── components/           # Reusable UI components
├── views/                # Page components
├── router/               # Vue Router configuration
├── stores/               # Pinia state management
├── services/             # API client services
├── types/                # TypeScript type definitions
└── utils/                # Utility functions
```

### Development Workflow

#### Feature Development Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/expense-categories
   ```

2. **Backend Development**
   - Create database models
   - Implement business logic
   - Create API endpoints
   - Write unit tests

3. **Frontend Development**
   - Create API service
   - Implement UI components
   - Add route and navigation
   - Write component tests

4. **Integration Testing**
   - Test API endpoints
   - Test frontend integration
   - End-to-end testing

5. **Code Review & Merge**
   - Submit pull request
   - Address review feedback
   - Merge to main branch

## 📚 Development Resources

### API Documentation

#### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs (development)
- **ReDoc**: http://localhost:8000/redoc (development)
- **OpenAPI JSON**: http://localhost:8000/openapi.json

#### API Testing Tools
```bash
# Using curl
curl -X POST "http://localhost:8000/api/users/" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password"}'

# Using HTTPie
http POST localhost:8000/api/users/ email=test@example.com password=password
```

### Database Management

#### Development Database
```bash
# View database contents
sqlite3 dev.db
.tables
.schema users
SELECT * FROM users;
```

#### Migrations
```bash
# Run migrations
python scripts/migrate_complete_schema.py

# Seed test data
python -c "from api.db.seed import seed_database; seed_database()"
```

### Testing Framework

#### Backend Testing
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_users.py -v

# Run with coverage
python -m pytest --cov=api tests/
```

#### Frontend Testing
```bash
# Run unit tests
npm run test:unit

# Run end-to-end tests
npm run test:e2e

# Run with coverage
npm run test:coverage
```

## 🔧 Development Tools Integration

### VS Code Configuration

Recommended VS Code extensions for TruLedgr development:

- **Python**: Python language support
- **Pylance**: Advanced Python language server
- **Vetur/Volar**: Vue.js language support
- **TypeScript Vue Plugin**: Vue TypeScript integration
- **GitLens**: Enhanced Git capabilities
- **Thunder Client**: API testing within VS Code
- **Error Lens**: Inline error highlighting

### Code Quality Tools

#### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

#### Linting and Formatting
```bash
# Python formatting
black api/
isort api/

# TypeScript/Vue formatting
npm run lint
npm run format
```

## 🚀 Deployment Architecture

### Development Deployment
- **Single server**: All services on one machine
- **SQLite database**: File-based database
- **Hot reload**: Automatic code reloading
- **Debug mode**: Detailed error messages

### Production Deployment
- **Multi-container**: Separate containers for frontend/backend
- **PostgreSQL**: Production database with connection pooling
- **Reverse proxy**: Nginx for static files and load balancing
- **HTTPS**: SSL/TLS encryption for all traffic
- **Monitoring**: Application performance monitoring

### Environment Configuration

#### Development
```bash
# .env.dev
DATABASE_URL=sqlite:///./dev.db
DEBUG=True
LOG_LEVEL=DEBUG
CORS_ORIGINS=["http://localhost:5173"]
```

#### Production
```bash
# .env.prod
DATABASE_URL=postgresql://user:pass@localhost/truledgr
DEBUG=False
LOG_LEVEL=INFO
CORS_ORIGINS=["https://truledgr.app"]
SECURE_COOKIES=True
```

## 🎯 Contributing Guidelines

### Code Review Process

#### Pull Request Requirements
- [ ] Feature branch created from main
- [ ] All tests passing
- [ ] Code follows style guidelines  
- [ ] Documentation updated
- [ ] Performance impact assessed
- [ ] Security implications reviewed

#### Review Checklist
- **Functionality**: Does the code work as intended?
- **Tests**: Are there adequate tests for new features?
- **Performance**: Will this impact application performance?
- **Security**: Are there any security vulnerabilities?
- **Documentation**: Is the code well-documented?

### Release Process

#### Version Management
- **Semantic Versioning**: Major.Minor.Patch (e.g., 1.2.3)
- **Git Tags**: Version tags for releases
- **Changelog**: Detailed release notes
- **Migration Scripts**: Database migration for schema changes

#### Deployment Pipeline
1. **Feature Development**: Individual feature branches
2. **Integration Testing**: Merge to development branch
3. **Staging Deployment**: Deploy to staging environment
4. **User Acceptance Testing**: Stakeholder review
5. **Production Deployment**: Deploy to production
6. **Post-deployment Monitoring**: Verify successful deployment

## 📈 Performance Monitoring

### Application Metrics

#### Backend Metrics
- **Response Times**: API endpoint performance
- **Database Queries**: Query execution time and frequency
- **Memory Usage**: Python process memory consumption
- **Error Rates**: Application error frequency and types

#### Frontend Metrics
- **Bundle Size**: JavaScript bundle size tracking
- **Load Times**: Page load performance
- **User Interactions**: Component performance metrics
- **Core Web Vitals**: Google performance metrics

### Monitoring Tools

#### Development Monitoring
- **FastAPI Debug**: Built-in development server
- **Vue DevTools**: Vue.js debugging browser extension
- **Browser DevTools**: Network, performance, and console monitoring

#### Production Monitoring (Planned)
- **Sentry**: Error tracking and performance monitoring
- **Grafana**: Metrics visualization and dashboards
- **Prometheus**: Metrics collection and alerting
- **Uptime Monitoring**: Service availability tracking

## 🔍 Debugging Guide

### Common Development Issues

#### Backend Issues
```python
# Debug database queries
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Add breakpoints
import pdb; pdb.set_trace()

# Check environment variables
from api.settings import get_settings
settings = get_settings()
print(settings.dict())
```

#### Frontend Issues
```typescript
// Vue component debugging
import { getCurrentInstance } from 'vue'
const instance = getCurrentInstance()
console.log('Component instance:', instance)

// Pinia store debugging
import { storeToRefs } from 'pinia'
const { transactions } = storeToRefs(useFinancialStore())
console.log('Store state:', transactions.value)
```

### Development Best Practices

#### Error Handling
- **Graceful Degradation**: Application continues working when possible
- **User-Friendly Messages**: Clear error messages for users
- **Developer Context**: Detailed logs for debugging
- **Error Boundaries**: Vue error boundaries for component errors

#### Code Organization
- **Single Responsibility**: Each function/component has one job
- **DRY Principle**: Don't repeat yourself
- **Clear Naming**: Descriptive variable and function names
- **Comment Complex Logic**: Explain non-obvious code sections

## 🎉 Next Steps

Ready to dive deeper into TruLedgr development?

1. **[Development Setup](setup.md)**: Complete environment configuration
2. **[Architecture Guide](architecture.md)**: Deep dive into system design
3. **[Backend Development](backend.md)**: FastAPI development patterns
4. **[Frontend Development](frontend.md)**: Vue.js best practices
5. **[Testing Guide](testing.md)**: Comprehensive testing strategies

Welcome to the TruLedgr development team! 🚀
