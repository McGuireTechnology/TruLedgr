# Architecture Overview

## System Architecture

TruLedgr follows a multi-platform architecture with a central FastAPI backend serving multiple frontend applications.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vue.js Web    │    │  iOS/macOS App  │    │  Android App    │
│  (Port 3000)    │    │   (SwiftUI)     │    │ (Jetpack Compose)│
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼───────────────┐
                    │      FastAPI Backend       │
                    │       (Port 8000)          │
                    │                             │
                    │  ┌─────────────────────┐    │
                    │  │    SQLite/PostgreSQL │    │
                    │  │      Database       │    │
                    │  └─────────────────────┘    │
                    └─────────────────────────────┘
```

## Core Principles

- **API-First**: All business logic resides in the FastAPI backend
- **Platform Native**: Each frontend uses native technologies and patterns
- **Shared Data**: All applications work with the same financial data
- **Monthly Cycles**: System designed around monthly financial reporting periods

## Technology Stack

- **Backend**: FastAPI (Python) with Pydantic models
- **Database**: SQLite for development, PostgreSQL for production
- **Web Frontend**: Vite + Vue.js 3 with Composition API
- **iOS/macOS**: SwiftUI with Apple Multiplatform
- **Android**: Jetpack Compose with Material Design 3
- **Documentation**: MkDocs with Material theme
- **Deployment**: DigitalOcean (all components)

## Data Flow

1. All financial data is stored in the central database
2. FastAPI provides RESTful endpoints for data access
3. Frontend applications consume the API for all operations
4. Real-time updates are handled through API polling or WebSocket connections
5. Monthly reports and worksheets are generated server-side

## Security

- OAuth2 authentication with multiple providers
- JWT tokens for API authentication
- HTTPS/TLS encryption for all communications
- Database encryption for sensitive financial data
- Audit trails for all financial transactions
