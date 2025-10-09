# TruLedgr TODO List

Last Updated: 2025-10-09

## 🍎 Apple Platform (iOS/macOS/visionOS)

### Core Architecture

- [ ] Implement actual financial data models (replacing Item.swift)
  - [ ] Account model with balance tracking
  - [ ] Transaction model with categorization
  - [ ] MonthlyReport model with worksheets
  - [ ] Budget model with categories
  - [ ] RecurringTransaction model
- [ ] Set up SwiftData relationships between models
- [ ] Implement data migration strategy
- [ ] Add data validation and constraints

### Authentication & Security

- [ ] Add OAuth2 authentication flows
  - [ ] Google Sign-In integration
  - [ ] Apple Sign-In integration
  - [ ] Microsoft authentication
  - [ ] GitHub authentication
- [ ] Implement secure token storage (Keychain)
- [ ] Add biometric authentication (Face ID/Touch ID)
- [ ] Implement session management

### API Integration

- [x] Integrate with backend API (localhost:8000)
  - [x] Set up URLSession networking layer
  - [ ] Implement API client with Codable models
  - [ ] Add request/response interceptors
  - [x] Implement error handling
- [ ] Add offline mode support
- [ ] Implement data sync conflict resolution
- [ ] Add retry logic for failed requests

### User Interface

- [ ] Build transaction tracking UI
  - [ ] Transaction list view with filtering
  - [ ] Transaction detail view
  - [ ] Add transaction form
  - [ ] Edit transaction form
  - [ ] Transaction categorization picker
- [ ] Implement monthly reporting views
  - [ ] Monthly overview dashboard
  - [ ] Worksheet view with sections
  - [ ] Income/expense breakdown charts
  - [ ] Budget vs actual comparison
  - [ ] Year-over-year comparison
- [ ] Build account management UI
  - [ ] Account list view
  - [ ] Account detail with transaction history
  - [ ] Add/edit account forms
  - [ ] Account balance trends
- [ ] Add settings/preferences screen
- [ ] Implement dark mode support (already configured)

### Data Synchronization

- [ ] Add CloudKit sync configuration
  - [ ] Configure CloudKit schema
  - [ ] Implement CKRecord transformations
  - [ ] Add conflict resolution strategy
  - [ ] Handle CloudKit errors
- [ ] Add push notification support
  - [ ] Configure APNs
  - [ ] Handle notification payloads
  - [ ] Implement notification actions

### Testing

- [ ] Write unit tests for data models
- [ ] Write unit tests for business logic
- [ ] Write unit tests for networking layer
- [ ] Add UI tests for critical flows
- [ ] Add snapshot tests for views
- [ ] Implement test fixtures and mocks

### App Store Preparation

- [ ] Design and create app icons
- [ ] Create App Store screenshots
- [ ] Write App Store description
- [ ] Add App Store keywords
- [ ] Create privacy policy
- [ ] Configure App Store Connect

---

## 🌐 Web Dashboard (Vite + Vue.js)

### Core Features

- [ ] Set up Vite + Vue 3 project structure
- [ ] Configure Vue Router for navigation
- [ ] Set up Pinia for state management
- [ ] Implement TypeScript types for API models

### Authentication

- [ ] Build OAuth2 login flow
  - [ ] Google OAuth integration
  - [ ] Microsoft OAuth integration
  - [ ] GitHub OAuth integration
  - [ ] Apple OAuth integration
- [ ] Implement JWT token management
- [ ] Add protected route guards
- [ ] Build login page UI
- [ ] Build signup page UI

### Dashboard Views

- [ ] Build main dashboard/overview
  - [ ] Account summary cards
  - [ ] Recent transactions list
  - [ ] Monthly summary widget
  - [ ] Budget status indicators
- [ ] Build accounts management page
  - [ ] Account list with balances
  - [ ] Add/edit account forms
  - [ ] Account transaction history
- [ ] Build transactions page
  - [ ] Transaction table with sorting/filtering
  - [ ] Add transaction modal
  - [ ] Edit transaction modal
  - [ ] Bulk import transactions
- [ ] Build monthly reports page
  - [ ] Month selector
  - [ ] Worksheet sections
  - [ ] Income/expense charts
  - [ ] Downloadable PDF reports

### UI/UX

- [ ] Implement responsive design (mobile-first)
- [ ] Add dark mode toggle
- [ ] Create reusable component library
- [ ] Add loading states and skeletons
- [ ] Implement error handling UI
- [ ] Add toast notifications

### Testing & Quality

- [ ] Write unit tests with Vitest
- [ ] Write component tests
- [ ] Add E2E tests with Playwright
- [ ] Set up ESLint + Prettier
- [ ] Add accessibility testing

---

## 🤖 Android Application

### Project Setup

- [x] Create Android Studio project structure
- [x] Set up Kotlin with Compose
- [x] Configure Gradle build system
- [ ] Set up dependency injection (Hilt/Koin)

### Core Architecture

- [ ] Implement MVVM architecture
- [ ] Set up Room database
- [ ] Create data models matching API
- [ ] Implement repository pattern

### Authentication

- [ ] Integrate OAuth2 authentication
  - [ ] Google Sign-In
  - [ ] GitHub OAuth
  - [ ] Microsoft OAuth
- [ ] Implement secure token storage
- [ ] Add biometric authentication

### API Integration

- [x] Set up basic HTTP networking (HttpURLConnection)
- [x] Implement API health check
- [ ] Set up Retrofit for full API client
- [ ] Add offline support with Room
- [ ] Implement data sync

### User Interface

- [ ] Build transaction tracking screens
- [ ] Build monthly reporting screens
- [ ] Build account management screens
- [x] Implement Material Design 3
- [x] Add dark theme support (system default)

### Testing

- [ ] Write unit tests
- [ ] Write instrumentation tests
- [ ] Add UI tests

---

## 🔧 Backend API (FastAPI)

### Core Infrastructure

- [ ] Finalize database schema with Alembic
- [ ] Set up PostgreSQL for production
- [ ] Implement connection pooling
- [ ] Add database indexing strategy
- [ ] Set up Redis for caching

### Authentication & Authorization

- [ ] Complete OAuth2 provider integrations
  - [ ] Google OAuth endpoint
  - [ ] Microsoft OAuth endpoint
  - [ ] GitHub OAuth endpoint
  - [ ] Apple OAuth endpoint
- [ ] Implement JWT token generation/validation
- [ ] Add refresh token rotation
- [ ] Implement user session management
- [ ] Add rate limiting middleware

### API Endpoints

- [ ] Implement accounts endpoints
  - [ ] GET /api/accounts (list)
  - [ ] POST /api/accounts (create)
  - [ ] GET /api/accounts/{id} (detail)
  - [ ] PUT /api/accounts/{id} (update)
  - [ ] DELETE /api/accounts/{id} (soft delete)
- [ ] Implement transactions endpoints
  - [ ] GET /api/transactions (list with pagination)
  - [ ] POST /api/transactions (create)
  - [ ] GET /api/transactions/{id} (detail)
  - [ ] PUT /api/transactions/{id} (update)
  - [ ] DELETE /api/transactions/{id} (soft delete)
  - [ ] POST /api/transactions/bulk (bulk import)
- [ ] Implement monthly reports endpoints
  - [ ] GET /api/reports/monthly/{year}/{month}
  - [ ] POST /api/reports/monthly (generate)
  - [ ] GET /api/reports/monthly/{id}/pdf (export)
- [ ] Implement budget endpoints
- [ ] Implement recurring transactions endpoints

### Data Management

- [ ] Implement proper decimal handling for monetary values
- [ ] Add transaction-level ACID compliance
- [ ] Implement audit trail for modifications
- [ ] Add soft delete functionality
- [ ] Implement data export (CSV, JSON)
- [ ] Add data import validation

### File Storage

- [ ] Configure DigitalOcean Spaces for production
- [ ] Implement file upload endpoints
- [ ] Add document storage for receipts
- [ ] Implement secure file access

### Testing

- [ ] Write unit tests for models
- [ ] Write unit tests for business logic
- [ ] Write integration tests for endpoints
- [ ] Add performance tests
- [ ] Implement test fixtures

### Documentation

- [ ] Complete OpenAPI schema documentation
- [ ] Add endpoint usage examples
- [ ] Document authentication flows
- [ ] Create API client examples

---

## 📚 Documentation (MkDocs)

### Content Development

- [ ] Fill out feature documentation pages
  - [ ] Complete docs/features/accounts.md
  - [ ] Complete docs/features/transactions.md
  - [ ] Complete docs/features/reports.md
  - [ ] Complete docs/features/budgeting.md
- [ ] Complete user guide pages
  - [ ] Write docs/guide/getting-started.md
  - [ ] Write docs/guide/dashboard.md
  - [ ] Write docs/guide/transactions.md
  - [ ] Write docs/guide/monthly-reports.md
- [ ] Complete platform app documentation
  - [ ] Write docs/apps/web.md
  - [ ] Write docs/apps/ios.md
  - [ ] Write docs/apps/android.md
  - [ ] Write docs/apps/macos.md

### Developer Documentation

- [ ] Complete API documentation
  - [ ] Authentication guide
  - [ ] Endpoint reference
  - [ ] Data models
  - [ ] Error handling
- [ ] Write architecture documentation
  - [ ] System overview
  - [ ] Database schema
  - [ ] Data flow diagrams
- [ ] Create contributing guide
  - [ ] Development setup
  - [ ] Code style guide
  - [ ] Pull request process

### Assets & Branding

- [ ] Design and add logo (docs/assets/logo.png)
- [ ] Create favicon (docs/assets/favicon.png)
- [ ] Add screenshot images
- [ ] Create diagram assets

---

## 🚀 DevOps & Deployment

### CI/CD Pipeline

- [ ] Set up GitHub Actions for API
  - [ ] Run tests on PR
  - [ ] Deploy to staging
  - [ ] Deploy to production
- [ ] Set up GitHub Actions for web dashboard
- [ ] Set up GitHub Actions for documentation
- [ ] Add automated security scanning

### Infrastructure (DigitalOcean)

- [ ] Set up PostgreSQL managed database
- [ ] Configure App Platform for API
- [ ] Configure App Platform for web dashboard
- [ ] Set up DigitalOcean Spaces for file storage
- [ ] Configure CDN for static assets
- [ ] Set up monitoring and alerts

### Environment Configuration

- [ ] Create production environment variables
- [ ] Set up staging environment
- [ ] Configure database backups
- [ ] Implement database migration strategy

### Security

- [ ] Set up SSL certificates
- [ ] Configure CORS policies
- [ ] Implement security headers
- [ ] Add dependency vulnerability scanning
- [ ] Set up secrets management

---

## 📊 Business & Planning

### Legal & Compliance

- [ ] Create privacy policy
- [ ] Create terms of service
- [ ] Research financial data regulations
- [ ] Plan GDPR compliance strategy
- [ ] Plan data retention policy

### Marketing

- [ ] Create landing page content
- [ ] Plan social media presence
- [ ] Create demo videos/screenshots
- [ ] Write blog posts about features
- [ ] Plan launch strategy

### Product

- [ ] Define MVP feature set
- [ ] Create product roadmap
- [ ] Plan beta testing program
- [ ] Define success metrics
- [ ] Set up analytics

---

## 🔄 Cross-Platform Concerns

### Data Synchronization

- [ ] Design sync conflict resolution strategy
- [ ] Implement optimistic locking
- [ ] Add sync status indicators
- [ ] Handle offline data changes

### Consistency

- [ ] Ensure API contract consistency across platforms
- [ ] Standardize error handling
- [ ] Unify data validation rules
- [ ] Create shared type definitions

### Testing

- [ ] Create end-to-end test suite
- [ ] Test cross-platform data sync
- [ ] Test OAuth flows on all platforms
- [ ] Performance testing

---

## 📝 Notes

### Priority Levels (suggested)

- 🔴 **Critical**: MVP blockers
- 🟡 **High**: Important for beta release
- 🟢 **Medium**: Nice to have for v1.0
- 🔵 **Low**: Future enhancements

### Current Focus

Working on Apple platform MVP:

1. Data models
2. API integration
3. Basic transaction UI
4. Monthly reports view

Next up: Web dashboard authentication and basic CRUD operations
