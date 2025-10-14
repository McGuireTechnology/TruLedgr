# TruLedgr API - Setup Guide

This guide covers setting up the authentication system with user registration and login.

## Quick Start

### 1. Install Dependencies

```bash
cd /Users/nathan/Documents/TruLedgr
poetry install
```

### 2. Configure Environment

Copy the example environment file and configure it:

```bash
cp api/.env.example api/.env
```

Edit `api/.env` and set your values:

```env
SECRET_KEY=your-very-secret-key-min-32-characters-long
DATABASE_URL=sqlite+aiosqlite:///./truledgr.db
```

### 3. Initialize Database

Create the database tables:

```bash
poetry run python -m api.init_db
```

### 4. Run the API

Start the development server:

```bash
poetry run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## API Endpoints

### Authentication

#### Register a New User

```bash
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}

Response (201 Created):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Login

```bash
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}

Response (200 OK):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Get Current User (Dashboard)

```bash
GET /auth/me
Authorization: Bearer <access_token>

Response (200 OK):
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "is_active": true,
  "is_admin": false,
  "is_business": false,
  "created_at": "2025-10-12T10:00:00Z",
  "last_login": "2025-10-12T15:30:00Z"
}
```

#### Logout

```bash
POST /auth/logout
Authorization: Bearer <access_token>

Response (204 No Content)
```

## Testing with curl

### Register

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}'
```

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}'
```

### Get Current User

```bash
TOKEN="your-access-token-here"
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

## Frontend Integration

### Registration Flow

1. User fills out registration form
2. Frontend sends POST to `/auth/register`
3. Receives access token
4. Store token in localStorage/cookies
5. Redirect to dashboard
6. Use token for authenticated requests

### Login Flow

1. User fills out login form
2. Frontend sends POST to `/auth/login`
3. Receives access token
4. Store token in localStorage/cookies
5. Redirect to dashboard
6. Use token for authenticated requests

### Dashboard Verification

1. On dashboard load, send GET to `/auth/me` with token
2. Display user information
3. If 401 error, redirect to login

### Example JavaScript

```javascript
// Register
async function register(email, password) {
  const response = await fetch('http://localhost:8000/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }
  
  const data = await response.json();
  localStorage.setItem('access_token', data.access_token);
  return data;
}

// Login
async function login(email, password) {
  const response = await fetch('http://localhost:8000/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }
  
  const data = await response.json();
  localStorage.setItem('access_token', data.access_token);
  return data;
}

// Get current user (dashboard)
async function getCurrentUser() {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('http://localhost:8000/auth/me', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  if (!response.ok) {
    if (response.status === 401) {
      // Token expired or invalid, redirect to login
      window.location.href = '/login';
      return;
    }
    const error = await response.json();
    throw new Error(error.detail);
  }
  
  return await response.json();
}

// Logout
async function logout() {
  localStorage.removeItem('access_token');
  window.location.href = '/login';
}
```

## Architecture

The API follows Clean Architecture and Domain-Driven Design principles:

- **Entities**: Domain models (User)
- **Value Objects**: Immutable domain values (UserId, EmailAddress)
- **Repositories**: Data access abstraction
- **Services**: Business logic (Authentication, Password, Token)
- **Routers**: HTTP endpoints
- **Schemas**: Request/response validation (Pydantic)
- **Dependencies**: Dependency injection for FastAPI

## Security Features

- ✅ Passwords hashed with bcrypt
- ✅ JWT tokens for stateless authentication
- ✅ Email validation
- ✅ Password length requirements (8-72 characters)
- ✅ Token expiration (30 minutes default)
- ✅ CORS protection
- ✅ SQL injection protection (SQLAlchemy ORM)

## Database

### SQLite (Development)

Default configuration uses SQLite with async support:
```
DATABASE_URL=sqlite+aiosqlite:///./truledgr.db
```

### PostgreSQL (Production)

For production, switch to PostgreSQL:
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/truledgr
```

## Next Steps

1. ✅ User registration and login implemented
2. ✅ JWT authentication working
3. ✅ Dashboard endpoint (/auth/me) for verification
4. 🔄 Frontend integration with Vue/React/iOS/Android
5. 📋 Add more user management features
6. 📋 Implement account, transaction, and reporting endpoints

## Troubleshooting

### Port Already in Use

If port 8000 is already in use:
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
poetry run uvicorn api.main:app --reload --port 8001
```

### Database Errors

Reset database:
```bash
rm truledgr.db
poetry run python -m api.init_db
```

### Import Errors

Reinstall dependencies:
```bash
poetry install --no-cache
```

### CORS Errors

Update ALLOWED_ORIGINS in .env:
```env
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:8080
```
