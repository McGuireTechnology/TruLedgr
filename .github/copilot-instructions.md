# TruLedgr AI Coding Agent Instructions

## Project Overview
TruLedgr is a comprehensive personal finance application suite with multi-platform support. The system includes financial account management, transaction tracking, monthly reporting, and extends into estate and tax planning tools.

## Architecture & Multi-Platform Structure

### Core Components
- `api/` - FastAPI backend with financial data models and business logic
- `dashboard/` - Vite/Vue.js web application (renamed from `vue/`)
- `apple/` - Apple Multiplatform app (iOS/macOS)
- `android/` - Android application
- Landing site: retired (use root MkDocs site)
- `docs/` - MkDocs technical documentation
- `pyproject.toml` - Python project configuration

### Technology Stack
- **Backend API**: FastAPI (Python) with Pydantic models
- **Dependency Management**: Poetry for Python package management and virtual environments
- **Frontend Web**: Vite + Vue.js for responsive web interface
- **Mobile**: Apple Multiplatform (SwiftUI) for iOS/macOS, native Android
- **Database**: SQLite for local development, PostgreSQL for production
- **File Storage**: Local disk for development, DigitalOcean S3 for production
- **Authentication**: OAuth2 with Google, Microsoft, GitHub, Apple providers
- **Documentation**: MkDocs for technical docs
- **Deployment**: DigitalOcean for all components (API, web, docs, landing)

## Development Workflow

### Backend Development (`api/`)
- Use Poetry for dependency management: `poetry install`, `poetry add <package>`
- Use FastAPI with async/await patterns for database operations
- Implement Pydantic models for financial data validation
- Structure around core domains: accounts, transactions, reports, estate planning, tax planning
- Use SQLAlchemy ORM with async support for database operations
- Implement proper decimal handling using Python's `decimal.Decimal` for monetary values

### Frontend Development
- **Web**: Vite + Vue 3 with Composition API
- **Mobile**: Native platform approaches (SwiftUI, Kotlin/Java)
- Share API contracts and data models across platforms
- Implement responsive design for monthly reporting cycles

### Database Strategy
- Use Alembic for database migrations
- Design for multi-tenancy (user isolation)
- Implement soft deletes for financial audit trails
- Plan for SQLite → PostgreSQL migration path

## Key Conventions

### Financial Data Handling
- Always use `decimal.Decimal` for monetary amounts in Python
- Implement transaction-level ACID compliance
- Maintain audit trails for all financial modifications
- Use UTC timestamps with proper timezone handling

### API Design
- RESTful endpoints with OpenAPI documentation
- Consistent error handling with proper HTTP status codes
- Implement rate limiting and authentication middleware
- Version API endpoints for backward compatibility

### Authentication & Security
- OAuth2 integration with multiple providers (Google, Microsoft, GitHub, Apple)
- JWT tokens for API authentication
- Secure session handling across web and mobile platforms
- Environment-specific configuration for auth callbacks

### Monthly Cycle Focus
- Design data models around monthly reporting periods
- Implement recurring transaction patterns
- Build worksheet/report generation for monthly financial reviews
- Plan for end-of-month processing workflows

## Deployment Architecture (DigitalOcean)
- **API**: App Platform or Droplets with PostgreSQL managed database
- **Web Frontend**: Static site deployment (App Platform)
- **Documentation**: Static site for MkDocs output
- **File Storage**: DigitalOcean Spaces (S3-compatible)
- **Database**: Managed PostgreSQL for production

## Development Environment Setup
1. Use Poetry to manage dependencies: `poetry init` and `poetry add fastapi sqlalchemy alembic`
2. Run development server with `poetry run uvicorn api.main:app --reload`
3. Set up SQLite for local development with realistic test data
4. Configure OAuth2 providers for local development
5. Implement environment-based configuration (local vs production)
6. Set up database migration workflow with Alembic: `poetry run alembic init alembic`

## Notes for AI Agents
- Focus on financial accuracy and audit compliance
- Implement proper error handling for financial operations
- Consider regulatory requirements for personal financial data
- Plan for data export/import capabilities (for user data portability)
- Design with monthly financial cycles as the primary user workflow
- Ensure cross-platform data consistency between web and mobile apps