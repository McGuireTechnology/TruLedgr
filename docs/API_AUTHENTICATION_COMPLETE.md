# 🎉 TruLedgr API - User Authentication Complete!

## ✅ What's Been Implemented

Your TruLedgr API now has a complete user authentication system with registration and login functionality, following Clean Architecture and Domain-Driven Design principles.

### Features Implemented

1. **User Registration** (`POST /auth/register`)
   - Create new user accounts
   - Email validation
   - Password hashing with bcrypt
   - Returns JWT access token immediately

2. **User Login** (`POST /auth/login`)
   - Authenticate with email and password
   - Password verification
   - Returns JWT access token
   - Records login timestamp

3. **Dashboard/User Info** (`GET /auth/me`)
   - Get current authenticated user information
   - Verifies JWT token
   - Returns user profile data
   - **This serves as your dashboard verification endpoint**

4. **Logout** (`POST /auth/logout`)
   - Stateless JWT logout (client-side token removal)
   - Can be extended with token blacklisting if needed

## 🚀 API Endpoints

### Base URL
```
http://localhost:8000
```

### Health Check
```bash
GET /health
# Response: {"status":"healthy","message":"Bonjour, TruLedgr is running!"}
```

### Register New User
```bash
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}

# Response (201 Created):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Login
```bash
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}

# Response (200 OK):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Get Current User (Dashboard)
```bash
GET /auth/me
Authorization: Bearer <your_access_token>

# Response (200 OK):
{
  "id": "a5a54bd6-f1f1-49f5-adc4-2ef0593c96fd",
  "email": "test@example.com",
  "is_active": true,
  "is_admin": false,
  "is_business": false,
  "created_at": "2025-10-13T04:42:45.206292",
  "last_login": "2025-10-13T04:42:59.602846"
}
```

## 🔌 Frontend Integration

### JavaScript/TypeScript Example

```javascript
// Configuration
const API_BASE_URL = 'http://localhost:8000';

// Register new user
async function register(email, password) {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
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

// Login user
async function login(email, password) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
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

// Get current user (for dashboard)
async function getCurrentUser() {
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    throw new Error('No authentication token found');
  }
  
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  if (!response.ok) {
    if (response.status === 401) {
      // Token expired or invalid - redirect to login
      localStorage.removeItem('access_token');
      window.location.href = '/login';
      return;
    }
    const error = await response.json();
    throw new Error(error.detail);
  }
  
  return await response.json();
}

// Logout
function logout() {
  localStorage.removeItem('access_token');
  window.location.href = '/login';
}

// Use in your components:
// Registration page
document.getElementById('register-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  
  try {
    await register(email, password);
    window.location.href = '/dashboard';
  } catch (error) {
    alert(error.message);
  }
});

// Login page
document.getElementById('login-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  
  try {
    await login(email, password);
    window.location.href = '/dashboard';
  } catch (error) {
    alert(error.message);
  }
});

// Dashboard page
document.addEventListener('DOMContentLoaded', async () => {
  try {
    const user = await getCurrentUser();
    document.getElementById('user-email').textContent = user.email;
    document.getElementById('user-id').textContent = user.id;
    document.getElementById('last-login').textContent = 
      new Date(user.last_login).toLocaleString();
  } catch (error) {
    console.error('Failed to load user:', error);
  }
});
```

### Vue.js Example

```vue
<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const API_BASE_URL = 'http://localhost:8000';
const router = useRouter();

const email = ref('');
const password = ref('');
const user = ref(null);
const error = ref('');

// Register
async function handleRegister() {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: email.value,
        password: password.value
      })
    });
    
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.detail);
    }
    
    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
    router.push('/dashboard');
  } catch (err) {
    error.value = err.message;
  }
}

// Login
async function handleLogin() {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: email.value,
        password: password.value
      })
    });
    
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.detail);
    }
    
    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
    router.push('/dashboard');
  } catch (err) {
    error.value = err.message;
  }
}

// Load user for dashboard
async function loadUser() {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
      return;
    }
    
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (!response.ok) {
      localStorage.removeItem('access_token');
      router.push('/login');
      return;
    }
    
    user.value = await response.json();
  } catch (err) {
    error.value = err.message;
  }
}

// Call on dashboard mount
onMounted(() => {
  if (router.currentRoute.value.path === '/dashboard') {
    loadUser();
  }
});
</script>

<template>
  <!-- Dashboard View -->
  <div v-if="user" class="dashboard">
    <h1>Welcome, {{ user.email }}!</h1>
    <div class="user-info">
      <p><strong>ID:</strong> {{ user.id }}</p>
      <p><strong>Email:</strong> {{ user.email }}</p>
      <p><strong>Active:</strong> {{ user.is_active ? 'Yes' : 'No' }}</p>
      <p><strong>Last Login:</strong> {{ new Date(user.last_login).toLocaleString() }}</p>
    </div>
    <button @click="logout">Logout</button>
  </div>
</template>
```

### iOS/SwiftUI Example

```swift
import Foundation

struct APIClient {
    static let baseURL = "http://localhost:8000"
    
    // Register
    static func register(email: String, password: String) async throws -> TokenResponse {
        let url = URL(string: "\(baseURL)/auth/register")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = ["email": email, "password": password]
        request.httpBody = try JSONEncoder().encode(body)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 201 else {
            throw APIError.invalidResponse
        }
        
        let tokenResponse = try JSONDecoder().decode(TokenResponse.self, from: data)
        UserDefaults.standard.set(tokenResponse.accessToken, forKey: "access_token")
        return tokenResponse
    }
    
    // Login
    static func login(email: String, password: String) async throws -> TokenResponse {
        let url = URL(string: "\(baseURL)/auth/login")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = ["email": email, "password": password]
        request.httpBody = try JSONEncoder().encode(body)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw APIError.invalidCredentials
        }
        
        let tokenResponse = try JSONDecoder().decode(TokenResponse.self, from: data)
        UserDefaults.standard.set(tokenResponse.accessToken, forKey: "access_token")
        return tokenResponse
    }
    
    // Get current user
    static func getCurrentUser() async throws -> UserResponse {
        guard let token = UserDefaults.standard.string(forKey: "access_token") else {
            throw APIError.notAuthenticated
        }
        
        let url = URL(string: "\(baseURL)/auth/me")!
        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw APIError.notAuthenticated
        }
        
        return try JSONDecoder().decode(UserResponse.self, from: data)
    }
}

// Models
struct TokenResponse: Codable {
    let accessToken: String
    let tokenType: String
    
    enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"
        case tokenType = "token_type"
    }
}

struct UserResponse: Codable {
    let id: String
    let email: String
    let isActive: Bool
    let isAdmin: Bool
    let isBusiness: Bool
    let createdAt: String
    let lastLogin: String?
    
    enum CodingKeys: String, CodingKey {
        case id, email
        case isActive = "is_active"
        case isAdmin = "is_admin"
        case isBusiness = "is_business"
        case createdAt = "created_at"
        case lastLogin = "last_login"
    }
}

enum APIError: Error {
    case invalidResponse
    case invalidCredentials
    case notAuthenticated
}
```

## 📚 Interactive API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You can test all endpoints directly in the browser!

## 🔒 Security Features

- ✅ Password hashing with bcrypt (industry standard)
- ✅ JWT tokens for stateless authentication
- ✅ Email validation (format and uniqueness)
- ✅ Password length requirements (8-72 characters)
- ✅ Token expiration (30 minutes, configurable)
- ✅ CORS protection with configurable origins
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ Async database operations for scalability

## 🗄️ Database

Currently using SQLite (`truledgr.db`) for development. The database has been initialized with the `users` table.

### Database Schema

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    is_business BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    last_login DATETIME
);
```

## 🚦 Running the API

The API is currently running at:
```
http://0.0.0.0:8000
```

To restart it:
```bash
cd /Users/nathan/Documents/TruLedgr
set -a && source api/.env && set +a
poetry run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Or in background:
```bash
cd /Users/nathan/Documents/TruLedgr
nohup poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 > api.log 2>&1 &
```

## 📝 Environment Configuration

The API is configured via `/Users/nathan/Documents/TruLedgr/api/.env`:

```env
SECRET_KEY=development-secret-key-change-this-in-production-min-32-chars-long
DATABASE_URL=sqlite+aiosqlite:///./truledgr.db
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:8000,http://localhost:3000,https://dash.truledgr.app
```

## 🎯 Testing the Workflows

### Signup → Dashboard Flow

1. **User fills registration form** in your frontend
2. **Frontend sends** `POST /auth/register` with email and password
3. **API returns** access token
4. **Frontend stores** token in localStorage/cookies
5. **Frontend redirects** to dashboard
6. **Dashboard loads**, calls `GET /auth/me` with token
7. **API returns** user information
8. **Dashboard displays** "Welcome, user@example.com!"

### Login → Dashboard Flow

1. **User fills login form** in your frontend
2. **Frontend sends** `POST /auth/login` with email and password
3. **API returns** access token
4. **Frontend stores** token
5. **Frontend redirects** to dashboard
6. **Dashboard verifies** authentication via `GET /auth/me`
7. **Dashboard displays** user information

## ✅ Test User Created

A test user has been created and verified:
- **Email**: `test@example.com`
- **Password**: `SecurePass123`

You can use this to test your frontend immediately!

## 🎨 Architecture

The API follows Clean Architecture and DDD:

```
api/
├── entities/           # Domain entities (User)
├── value_objects/      # Immutable values (UserId, EmailAddress)
├── repositories/       # Data access
│   ├── models/        # SQLAlchemy models
│   ├── mappers/       # Entity↔Model converters
│   └── user_repository.py
├── services/          # Business logic
│   ├── auth.py       # Authentication service
│   └── auth_exceptions.py
├── routers/           # HTTP endpoints
│   └── auth.py       # Registration, login, /me
├── schemas/           # Pydantic request/response
│   └── auth.py
├── dependencies/      # FastAPI dependencies
│   ├── database.py   # DB session, UnitOfWork
│   └── auth.py       # get_current_user
└── config/            # Settings
    └── settings.py
```

## 🚀 Next Steps

Your API is ready for frontend integration! Here's what you can do next:

1. **Connect your Vue/React/iOS/Android frontend** using the examples above
2. **Test the complete flow** from registration to dashboard
3. **Add more features**:
   - Password reset
   - Email verification
   - Profile updates
   - Account management
   - Financial data endpoints (accounts, transactions, etc.)

4. **Production deployment**:
   - Change `SECRET_KEY` to a secure random value
   - Switch to PostgreSQL database
   - Set up HTTPS
   - Configure CORS for production domains
   - Add rate limiting
   - Implement token blacklisting for logout

## 📖 Documentation

For more details, see:
- `API_SETUP_GUIDE.md` - Complete setup instructions
- `REFACTORING_SUMMARY.md` - Architecture details
- http://localhost:8000/docs - Interactive API docs

## 🎉 Success!

Your TruLedgr API is fully operational with:
- ✅ User registration
- ✅ User login
- ✅ JWT authentication
- ✅ Dashboard verification endpoint (/auth/me)
- ✅ Clean Architecture
- ✅ Comprehensive documentation
- ✅ Ready for frontend integration!

Happy coding! 🚀
