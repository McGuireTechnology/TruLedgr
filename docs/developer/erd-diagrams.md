# TruLedgr Entity Relationship Diagrams

This document contains comprehensive Entity Relationship Diagrams (ERDs) for the TruLedgr application, covering both the database schema and API layer relationships.

## Database Schema ERD

### Core User Management

```mermaid
erDiagram
    USERS {
        string id PK "ULID Primary Key"
        string username UK "Unique username"
        string email UK "Unique email"
        string password_hash "Argon2 hashed password"
        boolean is_active "Account status"
        boolean is_verified "Email verification"
        boolean is_superuser "Admin privileges"
        string first_name "User first name"
        string last_name "User last name"
        datetime last_login_at "Last login timestamp"
        boolean is_oauth_user "OAuth authentication flag"
        string oauth_provider "OAuth provider name"
        string oauth_provider_id "External OAuth ID"
        string profile_picture_url "Profile picture URL"
        boolean email_verified "OAuth email verification"
        datetime created_at "Record creation time"
        datetime updated_at "Record update time"
        boolean is_deleted "Soft delete flag"
        datetime deleted_at "Soft delete timestamp"
    }

    USER_SESSIONS {
        string id PK "ULID Primary Key"
        string user_id FK "Foreign key to users"
        string session_token_hash "Hashed session token"
        string ip_address "Client IP address"
        string user_agent "Client user agent"
        boolean is_active "Session status"
        datetime expires_at "Session expiration"
        datetime last_activity "Last activity time"
        datetime created_at "Session creation time"
        datetime updated_at "Session update time"
    }

    SESSION_ACTIVITIES {
        string id PK "ULID Primary Key"
        string user_id FK "Foreign key to users"
        string session_id FK "Foreign key to user_sessions"
        string activity_type "Type of activity"
        string endpoint "API endpoint accessed"
        string method "HTTP method"
        integer status_code "Response status code"
        string ip_address "Client IP address"
        string user_agent "Client user agent"
        json request_data "Sanitized request data"
        json response_data "Sanitized response data"
        datetime created_at "Activity timestamp"
    }

    USERS ||--o{ USER_SESSIONS : "has many"
    USERS ||--o{ SESSION_ACTIVITIES : "has many"
    USER_SESSIONS ||--o{ SESSION_ACTIVITIES : "tracks"
```

### Role-Based Access Control (RBAC)

```mermaid
erDiagram
    ROLES {
        string id PK "ULID Primary Key"
        string name UK "Unique role name"
        string description "Role description"
        boolean is_system_role "System role flag"
        boolean is_active "Role status"
        datetime created_at "Record creation time"
        datetime updated_at "Record update time"
        boolean is_deleted "Soft delete flag"
        datetime deleted_at "Soft delete timestamp"
    }

    PERMISSIONS {
        string id PK "ULID Primary Key"
        string name UK "Unique permission name"
        string description "Permission description"
        string resource "Resource type"
        string action "Action allowed"
        boolean is_system "System permission flag"
        datetime created_at "Record creation time"
        datetime updated_at "Record update time"
    }

    ROLE_PERMISSIONS {
        string role_id PK,FK "Foreign key to roles"
        string permission_id PK,FK "Foreign key to permissions"
        string assigned_by FK "User who assigned permission"
        datetime assigned_at "Assignment timestamp"
    }

    USER_ROLES {
        string user_id PK,FK "Foreign key to users"
        string role_id PK,FK "Foreign key to roles"
        string assigned_by FK "User who assigned role"
        datetime assigned_at "Assignment timestamp"
    }

    ROLES ||--o{ ROLE_PERMISSIONS : "has permissions"
    PERMISSIONS ||--o{ ROLE_PERMISSIONS : "granted to roles"
    USERS ||--o{ USER_ROLES : "has roles"
    ROLES ||--o{ USER_ROLES : "assigned to users"
```

### Group Management

```mermaid
erDiagram
    GROUPS {
        string id PK "ULID Primary Key"
        string name "Group name"
        string slug UK "URL-friendly identifier"
        string description "Group description"
        string owner_id FK "Foreign key to users"
        boolean is_active "Group status"
        boolean is_public "Public visibility"
        integer max_members "Maximum member count"
        integer member_count "Current member count"
        json settings "Group configuration"
        datetime created_at "Record creation time"
        datetime updated_at "Record update time"
        boolean is_deleted "Soft delete flag"
        datetime deleted_at "Soft delete timestamp"
    }

    USER_GROUPS {
        string user_id PK,FK "Foreign key to users"
        string group_id PK,FK "Foreign key to groups"
        string role "Member role in group"
        datetime joined_at "Membership start time"
        datetime created_at "Record creation time"
        datetime updated_at "Record update time"
    }

    USERS ||--o{ GROUPS : "owns"
    USERS ||--o{ USER_GROUPS : "member of"
    GROUPS ||--o{ USER_GROUPS : "has members"
```

### Authentication Support

```mermaid
erDiagram
    PASSWORD_RESET_TOKENS {
        string id PK "ULID Primary Key"
        string user_id FK "Foreign key to users"
        string email "User email"
        string token_hash "Hashed reset token"
        datetime expires_at "Token expiration"
        boolean is_used "Token usage flag"
        string ip_address "Request IP address"
        string user_agent "Request user agent"
        datetime created_at "Token creation time"
        datetime updated_at "Token update time"
    }

    OAUTH_ACCOUNTS {
        string id PK "ULID Primary Key"
        string user_id FK "Foreign key to users"
        string provider "OAuth provider name"
        string provider_user_id "External user ID"
        string provider_email "Provider email"
        string access_token "Encrypted access token"
        string refresh_token "Encrypted refresh token"
        datetime token_expires_at "Token expiration"
        json provider_data "Additional provider data"
        datetime created_at "Account link time"
        datetime updated_at "Account update time"
    }

    OAUTH2ACCOUNT {
        string user_id FK "Foreign key to users"
        string provider "OAuth provider"
        string provider_user_id "External user ID"
        string email "OAuth email"
        datetime created_at "Link creation time"
    }

    USERS ||--o{ PASSWORD_RESET_TOKENS : "can request reset"
    USERS ||--o{ OAUTH_ACCOUNTS : "linked accounts"
    USERS ||--o{ OAUTH2ACCOUNT : "oauth links"
```

### Financial Data Models

```mermaid
erDiagram
    INSTITUTIONS {
        string id PK "ULID Primary Key"
        string name "Institution name"
        string institution_type "Type of institution"
        string primary_source "Primary data source"
        string plaid_institution_id "Plaid identifier"
        string website_url "Institution website"
        string logo_url "Institution logo"
        string support_email "Support email"
        string support_phone "Support phone"
        boolean is_active "Institution status"
        string health_status "Operational status"
        datetime created_at "Record creation time"
        datetime updated_at "Record update time"
        boolean is_deleted "Soft delete flag"
        datetime deleted_at "Soft delete timestamp"
    }

    ACCOUNTS {
        string id PK "ULID Primary Key"
        string user_id FK "Foreign key to users"
        string institution_id FK "Foreign key to institutions"
        string account_name "User-defined name"
        string account_type "Account type"
        string account_subtype "Account subtype"
        decimal balance "Current balance"
        decimal available_balance "Available balance"
        string currency "Account currency"
        boolean is_active "Account status"
        boolean is_manual "Manual entry flag"
        datetime created_at "Record creation time"
        datetime updated_at "Record update time"
        boolean is_deleted "Soft delete flag"
        datetime deleted_at "Soft delete timestamp"
    }

    TRANSACTIONS {
        string id PK "ULID Primary Key"
        string user_id FK "Foreign key to users"
        string account_id FK "Foreign key to accounts"
        decimal amount "Transaction amount"
        string currency "Transaction currency"
        string description "Transaction description"
        string merchant_name "Merchant name"
        string category "Transaction category"
        string subcategory "Transaction subcategory"
        date transaction_date "Transaction date"
        date posted_date "Posted date"
        boolean pending "Pending status"
        string transaction_code "Bank transaction code"
        datetime created_at "Record creation time"
        datetime updated_at "Record update time"
        boolean is_deleted "Soft delete flag"
        datetime deleted_at "Soft delete timestamp"
    }

    USERS ||--o{ ACCOUNTS : "owns"
    INSTITUTIONS ||--o{ ACCOUNTS : "provides"
    ACCOUNTS ||--o{ TRANSACTIONS : "contains"
    USERS ||--o{ TRANSACTIONS : "performs"
```

### Activity and Audit Trail

```mermaid
erDiagram
    ACTIVITIES {
        string id PK "ULID Primary Key"
        string user_id FK "Foreign key to users"
        string session_id FK "Related session"
        string activity_type "Type of activity"
        string description "Activity description"
        json metadata "Additional data"
        string ip_address "Client IP address"
        string user_agent "Client information"
        string status "Activity status"
        datetime created_at "Activity timestamp"
        datetime updated_at "Record update time"
    }

    SESSIONANALYTICS {
        string session_id FK "Foreign key to sessions"
        string user_id FK "Foreign key to users"
        json analytics_data "Session analytics"
        datetime created_at "Analytics timestamp"
    }

    USERS ||--o{ ACTIVITIES : "performs"
    USER_SESSIONS ||--o{ SESSIONANALYTICS : "tracked by"
    USERS ||--o{ SESSIONANALYTICS : "analytics for"
```

## API Layer Entity Relationships

### Authentication Flow

```mermaid
graph TD
    A[Client Request] --> B{Authentication Required?}
    B -->|Yes| C[Check JWT Token]
    B -->|No| D[Public Endpoint]
    C --> E{Token Valid?}
    E -->|Yes| F[Extract User Info]
    E -->|No| G[Return 401 Unauthorized]
    F --> H[Check Permissions]
    H --> I{Authorized?}
    I -->|Yes| J[Process Request]
    I -->|No| K[Return 403 Forbidden]
    J --> L[Return Response]
    D --> L
```

### User Management API Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant A as Auth API
    participant U as User API
    participant DB as Database
    participant S as Session Store

    C->>A: POST /auth/login
    A->>DB: Validate credentials
    DB-->>A: User data
    A->>S: Create session
    S-->>A: Session token
    A-->>C: JWT + Session token

    C->>U: GET /users/me (with JWT)
    U->>A: Validate token
    A-->>U: User ID + permissions
    U->>DB: Get user data
    DB-->>U: User profile
    U-->>C: User profile data

    C->>U: PUT /users/me (update profile)
    U->>A: Validate token + permissions
    A-->>U: Authorization OK
    U->>DB: Update user data
    DB-->>U: Updated user
    U-->>C: Updated profile
```

### RBAC API Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant A as Auth API
    participant R as RBAC API
    participant DB as Database

    C->>R: GET /roles (with JWT)
    R->>A: Validate token
    A-->>R: User permissions
    R->>R: Check 'role:read' permission
    R->>DB: Query roles
    DB-->>R: Role list
    R-->>C: Filtered role list

    C->>R: POST /roles (create role)
    R->>A: Validate token
    A-->>R: User permissions
    R->>R: Check 'role:create' permission
    R->>DB: Create role
    DB-->>R: New role
    R-->>C: Created role data
```

### Financial Data API Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant F as Financial API
    participant P as Plaid Service
    participant DB as Database
    participant Q as Background Queue

    C->>F: POST /accounts/connect (Plaid token)
    F->>P: Exchange public token
    P-->>F: Access token + account data
    F->>DB: Store accounts + transactions
    F->>Q: Queue sync job
    F-->>C: Account connection success

    C->>F: GET /transactions
    F->>DB: Query user transactions
    DB-->>F: Transaction list
    F-->>C: Paginated transactions

    Q->>P: Sync latest transactions
    P-->>Q: New transaction data
    Q->>DB: Update transactions
    Q->>F: Webhook notification
    F->>C: Real-time update (WebSocket)
```

## Database Indexes and Performance

### Primary Indexes

```mermaid
graph LR
    A[Primary Keys - ULID] --> B[Clustered Index]
    C[Foreign Keys] --> D[Non-Clustered Index]
    E[Unique Constraints] --> F[Unique Index]
    G[Search Fields] --> H[Composite Index]
```

### Index Strategy

| Table | Index Type | Columns | Purpose |
|-------|------------|---------|---------|
| users | Unique | email | User lookup |
| users | Unique | username | User lookup |
| users | Composite | (is_active, is_deleted) | Active user queries |
| user_sessions | Unique | session_token_hash | Session validation |
| user_sessions | Composite | (user_id, is_active) | User session queries |
| transactions | Composite | (user_id, transaction_date) | Transaction history |
| transactions | Composite | (account_id, pending) | Account transactions |
| activities | Composite | (user_id, created_at) | Activity timeline |
| role_permissions | Composite | (role_id, permission_id) | Permission checks |

## API Response Schemas

### User Response Schema

```mermaid
classDiagram
    class UserResponse {
        +string id
        +string username
        +string email
        +string first_name
        +string last_name
        +boolean is_active
        +boolean is_verified
        +datetime last_login_at
        +datetime created_at
        +datetime updated_at
        +RoleResponse[] roles
        +GroupResponse[] groups
    }

    class RoleResponse {
        +string id
        +string name
        +string description
        +PermissionResponse[] permissions
    }

    class PermissionResponse {
        +string id
        +string name
        +string resource
        +string action
    }

    class GroupResponse {
        +string id
        +string name
        +string role
        +datetime joined_at
    }

    UserResponse --> RoleResponse
    UserResponse --> GroupResponse
    RoleResponse --> PermissionResponse
```

### Financial Response Schema

```mermaid
classDiagram
    class AccountResponse {
        +string id
        +string account_name
        +string account_type
        +decimal balance
        +string currency
        +InstitutionResponse institution
        +TransactionResponse[] recent_transactions
    }

    class InstitutionResponse {
        +string id
        +string name
        +string logo_url
        +string website_url
    }

    class TransactionResponse {
        +string id
        +decimal amount
        +string description
        +string category
        +date transaction_date
        +boolean pending
    }

    AccountResponse --> InstitutionResponse
    AccountResponse --> TransactionResponse
```

## Data Flow Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web Dashboard]
        MOBILE[Mobile App]
        API_CLIENT[API Client]
    end

    subgraph "API Gateway"
        FASTAPI[FastAPI Application]
        AUTH[Authentication Middleware]
        RBAC[Authorization Middleware]
        RATE[Rate Limiting]
    end

    subgraph "Service Layer"
        USER_SVC[User Service]
        AUTH_SVC[Auth Service]
        FIN_SVC[Financial Service]
        GROUP_SVC[Group Service]
        ACTIVITY_SVC[Activity Service]
    end

    subgraph "Data Layer"
        POSTGRES[(PostgreSQL)]
        REDIS[(Redis Cache)]
        PLAID[Plaid API]
    end

    WEB --> FASTAPI
    MOBILE --> FASTAPI
    API_CLIENT --> FASTAPI

    FASTAPI --> AUTH
    AUTH --> RBAC
    RBAC --> RATE

    RATE --> USER_SVC
    RATE --> AUTH_SVC
    RATE --> FIN_SVC
    RATE --> GROUP_SVC
    RATE --> ACTIVITY_SVC

    USER_SVC --> POSTGRES
    AUTH_SVC --> POSTGRES
    AUTH_SVC --> REDIS
    FIN_SVC --> POSTGRES
    FIN_SVC --> PLAID
    GROUP_SVC --> POSTGRES
    ACTIVITY_SVC --> POSTGRES
```

## Security Model

```mermaid
graph TD
    A[Request] --> B[Rate Limiting]
    B --> C[Authentication]
    C --> D{JWT Valid?}
    D -->|No| E[Return 401]
    D -->|Yes| F[Extract User Claims]
    F --> G[Authorization Check]
    G --> H{Permission Check}
    H -->|No| I[Return 403]
    H -->|Yes| J[Resource Access]
    J --> K[Audit Log]
    K --> L[Response]
```

This comprehensive ERD documentation provides a complete view of your TruLedgr application's data architecture and API relationships. The diagrams use Mermaid syntax which renders well in GitHub, GitLab, and most documentation platforms.
