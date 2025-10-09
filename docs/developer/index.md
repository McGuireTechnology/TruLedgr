# Developer Documentation

Technical documentation for TruLedgr contributors, API consumers, and self-hosters.

!!! info "For End Users"
    Looking to use TruLedgr? Start with the [User Guide](../guide/index.md) instead.

## Quick Navigation

<div class="grid cards" markdown>

-   :material-architecture: __Architecture__

    ---

    System design, components, and technical overview
    
    [:octicons-arrow-right-24: View docs](architecture/index.md)

-   :material-api: __API Reference__

    ---

    REST API endpoints, models, and authentication
    
    [:octicons-arrow-right-24: View docs](api/index.md)

-   :material-code-braces: __Contributing__

    ---

    Setup guide, development workflow, and code standards
    
    [:octicons-arrow-right-24: View docs](contributing/index.md)

-   :material-rocket-launch: __Deployment__

    ---

    Self-hosting, production deployment, and CI/CD
    
    [:octicons-arrow-right-24: View docs](deployment/index.md)

</div>

## Getting Started as a Developer

### 1. Set Up Your Development Environment

Clone the repository and set up dependencies:

```bash
# Clone the repo
git clone https://github.com/McGuireTechnology/TruLedgr.git
cd TruLedgr

# Backend setup (Python/Poetry)
cd api
poetry install
poetry run uvicorn api.main:app --reload

# Dashboard setup (Node/npm)
cd ../dashboard
npm install
npm run dev
```

[Full setup guide →](contributing/dev-setup.md)

### 2. Understand the Architecture

TruLedgr uses a modern multi-platform architecture:

- **Backend:** FastAPI (Python) with PostgreSQL
- **Web:** Vue 3 + Vite
- **Mobile:** Native Swift (iOS/macOS) and Kotlin/Java (Android)

[Explore architecture →](architecture/index.md)

### 3. Read the API Documentation

The FastAPI backend exposes a RESTful API with OpenAPI documentation:

- Interactive docs at `/docs`
- Alternative docs at `/redoc`
- OpenAPI spec at `/openapi.json`

[API reference →](api/index.md)

### 4. Make Your First Contribution

- Read [contributing guidelines](contributing/index.md)
- Check [open issues](https://github.com/McGuireTechnology/TruLedgr/issues)
- Review [code style guide](contributing/style.md)
- Submit a pull request!

## Technology Stack

### Backend

- **Language:** Python 3.11+
- **Framework:** FastAPI with async/await
- **ORM:** SQLAlchemy 2.0
- **Database:** PostgreSQL (production), SQLite (development)
- **Auth:** OAuth2 with JWT tokens
- **Deployment:** DigitalOcean App Platform

### Frontend Web

- **Framework:** Vue 3 Composition API
- **Build Tool:** Vite
- **Language:** TypeScript
- **State:** Pinia
- **Deployment:** DigitalOcean Static Site

### Mobile

- **iOS/macOS:** Swift + SwiftUI
- **Android:** Kotlin + Jetpack Compose
- **API Client:** Native HTTP libraries

### DevOps

- **CI/CD:** GitHub Actions
- **Testing:** pytest (Python), Vitest (JavaScript)
- **Linting:** Ruff, Black (Python), ESLint (JavaScript)
- **Documentation:** MkDocs with Material theme

## API Consumers

Building an integration with TruLedgr?

- **[Authentication Guide](api/authentication.md)** - OAuth2 flows and token management
- **[API Endpoints](api/endpoints.md)** - Available routes and methods
- **[Data Models](api/models.md)** - Request/response schemas
- **[Rate Limits](api/index.md#rate-limiting)** - Usage limits and quotas

## Self-Hosting

Want to run TruLedgr on your own infrastructure?

- **[Deployment Guide](deployment/index.md)** - Complete setup instructions
- **[Environment Variables](deployment/environment.md)** - Configuration reference
- **[Database Setup](architecture/database.md)** - Schema and migrations

## Contributing

We welcome contributions! Here's how to get involved:

1. **[Fork the repository](https://github.com/McGuireTechnology/TruLedgr/fork)**
2. **[Set up your environment](contributing/dev-setup.md)**
3. **[Read the workflow guide](contributing/workflow.md)**
4. **[Submit a pull request](contributing/index.md)**

See also:

- [Code of Conduct](https://github.com/McGuireTechnology/TruLedgr/blob/main/CODE_OF_CONDUCT.md)
- [Security Policy](https://github.com/McGuireTechnology/TruLedgr/blob/main/SECURITY.md)
- [License](https://github.com/McGuireTechnology/TruLedgr/blob/main/LICENSE)

## Community

- **GitHub:** [McGuireTechnology/TruLedgr](https://github.com/McGuireTechnology/TruLedgr)
- **Issues:** [Report bugs or request features](https://github.com/McGuireTechnology/TruLedgr/issues)
- **Discussions:** [Ask questions and share ideas](https://github.com/McGuireTechnology/TruLedgr/discussions)
- **Pull Requests:** [View open PRs](https://github.com/McGuireTechnology/TruLedgr/pulls)
