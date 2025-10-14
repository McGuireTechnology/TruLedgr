# 🔧 TruLedgr API - User Management Endpoints

## Overview

Complete CRUD (Create, Read, Update, Delete) endpoints for user management have been implemented. These endpoints provide full user administration capabilities with proper authentication, authorization, and role-based access control.

## 📚 Endpoints Summary

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| **GET** | `/users` | List all users (paginated) | Admin only |
| **GET** | `/users/{user_id}` | Get user by ID | Admin or own profile |
| **POST** | `/users` | Create new user | Admin only |
| **PUT** | `/users/{user_id}` | Full update user | Admin (all fields) or own profile (limited) |
| **PATCH** | `/users/{user_id}` | Partial update user | Admin (all fields) or own profile (limited) |
| **DELETE** | `/users/{user_id}` | Delete user | Admin only |

## 🔐 Authorization Rules

### Admin Users
- Can list all users
- Can view any user's profile
- Can create new users
- Can update any user (all fields: email, is_active, is_admin, is_business)
- Can delete any user (except themselves)

### Regular Users
- Cannot list all users
- Can only view their own profile
- Cannot create users (use `/auth/register` instead)
- Can only update their own profile (limited to: email, is_business)
- Cannot delete users

## 📖 API Reference

### Base URL
```
http://localhost:8000
```

### Authentication
All endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

---

## 1. List All Users

**GET** `/users`

Get paginated list of all users (admin only).

### Query Parameters
- `page` (integer, default: 1) - Page number (minimum: 1)
- `page_size` (integer, default: 10) - Items per page (1-100)

### Request Example
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/users?page=1&page_size=10"
```

### Response (200 OK)
```json
{
  "users": [
    {
      "id": "a5a54bd6-f1f1-49f5-adc4-2ef0593c96fd",
      "email": "test@example.com",
      "is_active": true,
      "is_admin": true,
      "is_business": false,
      "created_at": "2025-10-13T04:42:45.206292",
      "last_login": "2025-10-13T04:57:05.789343"
    },
    {
      "id": "8c30289a-7c1e-473a-b5df-ba8cb52fcb7e",
      "email": "regular@example.com",
      "is_active": true,
      "is_admin": false,
      "is_business": true,
      "created_at": "2025-10-13T04:58:14.399048",
      "last_login": "2025-10-13T04:59:19.623002"
    }
  ],
  "total": 2,
  "page": 1,
  "page_size": 10
}
```

### Error Responses
- **401 Unauthorized** - Not authenticated
- **403 Forbidden** - Admin access required

---

## 2. Get User by ID

**GET** `/users/{user_id}`

Get specific user by ID. Users can get their own profile, admins can get any user.

### Path Parameters
- `user_id` (string, required) - UUID of the user

### Request Example
```bash
# Admin viewing any user
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8000/users/8c30289a-7c1e-473a-b5df-ba8cb52fcb7e

# User viewing own profile
curl -H "Authorization: Bearer $USER_TOKEN" \
  http://localhost:8000/users/8c30289a-7c1e-473a-b5df-ba8cb52fcb7e
```

### Response (200 OK)
```json
{
  "id": "8c30289a-7c1e-473a-b5df-ba8cb52fcb7e",
  "email": "regular@example.com",
  "is_active": true,
  "is_admin": false,
  "is_business": true,
  "created_at": "2025-10-13T04:58:14.399048",
  "last_login": "2025-10-13T04:59:19.623002"
}
```

### Error Responses
- **400 Bad Request** - Invalid user ID format
- **401 Unauthorized** - Not authenticated
- **403 Forbidden** - Access denied (can only view own profile)
- **404 Not Found** - User not found

---

## 3. Create New User

**POST** `/users`

Create a new user account (admin only). This is for admin-created accounts without passwords. Regular users should use `/auth/register`.

### Request Body
```json
{
  "email": "newuser@example.com",
  "is_active": true,
  "is_admin": false,
  "is_business": true
}
```

### Request Example
```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "email": "newuser@example.com",
    "is_active": true,
    "is_admin": false,
    "is_business": true
  }'
```

### Response (201 Created)
```json
{
  "id": "6bbc28a2-a822-4467-a7be-3b1a42d470de",
  "email": "newuser@example.com",
  "is_active": true,
  "is_admin": false,
  "is_business": true,
  "created_at": "2025-10-13T04:56:54.161951",
  "last_login": null
}
```

### Error Responses
- **400 Bad Request** - Email already registered or invalid data
- **401 Unauthorized** - Not authenticated
- **403 Forbidden** - Admin access required

---

## 4. Update User (Full - PUT)

**PUT** `/users/{user_id}`

Full update of user. All fields must be provided.

**Permissions:**
- **Admins**: Can update all fields (email, is_active, is_admin, is_business)
- **Regular users**: Can only update their own email and is_business flag

### Path Parameters
- `user_id` (string, required) - UUID of the user

### Request Body
```json
{
  "email": "updated@example.com",
  "is_active": true,
  "is_admin": false,
  "is_business": true
}
```

### Request Example
```bash
# Admin updating any user
curl -X PUT http://localhost:8000/users/8c30289a-7c1e-473a-b5df-ba8cb52fcb7e \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "email": "updated@example.com",
    "is_active": true,
    "is_admin": false,
    "is_business": true
  }'

# Regular user updating own profile
curl -X PUT http://localhost:8000/users/8c30289a-7c1e-473a-b5df-ba8cb52fcb7e \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -d '{
    "email": "mynewemail@example.com",
    "is_active": true,
    "is_admin": false,
    "is_business": true
  }'
```

### Response (200 OK)
```json
{
  "id": "8c30289a-7c1e-473a-b5df-ba8cb52fcb7e",
  "email": "updated@example.com",
  "is_active": true,
  "is_admin": false,
  "is_business": true,
  "created_at": "2025-10-13T04:58:14.399048",
  "last_login": "2025-10-13T04:59:19.623002"
}
```

### Error Responses
- **400 Bad Request** - Invalid data or email already in use
- **401 Unauthorized** - Not authenticated
- **403 Forbidden** - Access denied
- **404 Not Found** - User not found

---

## 5. Update User (Partial - PATCH)

**PATCH** `/users/{user_id}`

Partial update of user. Only provide fields you want to update.

**Permissions:**
- **Admins**: Can update all fields (email, is_active, is_admin, is_business)
- **Regular users**: Can only update their own email and is_business flag

### Path Parameters
- `user_id` (string, required) - UUID of the user

### Request Body (all fields optional)
```json
{
  "email": "newemail@example.com",
  "is_active": false,
  "is_admin": true,
  "is_business": true
}
```

### Request Example
```bash
# Admin deactivating a user
curl -X PATCH http://localhost:8000/users/8c30289a-7c1e-473a-b5df-ba8cb52fcb7e \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"is_active": false}'

# Regular user upgrading to business account
curl -X PATCH http://localhost:8000/users/8c30289a-7c1e-473a-b5df-ba8cb52fcb7e \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -d '{"is_business": true}'

# Admin promoting user to admin
curl -X PATCH http://localhost:8000/users/8c30289a-7c1e-473a-b5df-ba8cb52fcb7e \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"is_admin": true}'
```

### Response (200 OK)
```json
{
  "id": "8c30289a-7c1e-473a-b5df-ba8cb52fcb7e",
  "email": "regular@example.com",
  "is_active": true,
  "is_admin": false,
  "is_business": true,
  "created_at": "2025-10-13T04:58:14.399048",
  "last_login": "2025-10-13T04:59:19.623002"
}
```

### Error Responses
- **400 Bad Request** - Invalid data or email already in use
- **401 Unauthorized** - Not authenticated
- **403 Forbidden** - Access denied
- **404 Not Found** - User not found

---

## 6. Delete User

**DELETE** `/users/{user_id}`

Permanently delete a user (admin only). Admins cannot delete themselves.

### Path Parameters
- `user_id` (string, required) - UUID of the user

### Request Example
```bash
curl -X DELETE http://localhost:8000/users/8c30289a-7c1e-473a-b5df-ba8cb52fcb7e \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### Response (204 No Content)
No response body. Success indicated by 204 status code.

### Error Responses
- **400 Bad Request** - Cannot delete your own account or invalid user ID
- **401 Unauthorized** - Not authenticated
- **403 Forbidden** - Admin access required
- **404 Not Found** - User not found

---

## 🧪 Complete Testing Script

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"

echo "🔐 Step 1: Login as admin"
ADMIN_TOKEN=$(curl -s -X POST $BASE_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123"}' \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])")
echo "✅ Admin token obtained"

echo ""
echo "📋 Step 2: List all users"
curl -s -H "Authorization: Bearer $ADMIN_TOKEN" \
  "$BASE_URL/users?page=1&page_size=10" | python3 -m json.tool
echo ""

echo "➕ Step 3: Create new user"
NEW_USER=$(curl -s -X POST $BASE_URL/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "email":"testuser@example.com",
    "is_active":true,
    "is_admin":false,
    "is_business":true
  }')
echo "$NEW_USER" | python3 -m json.tool
NEW_USER_ID=$(echo "$NEW_USER" | python3 -c "import json,sys; print(json.load(sys.stdin)['id'])")
echo "✅ Created user with ID: $NEW_USER_ID"
echo ""

echo "👁️  Step 4: Get user by ID"
curl -s -H "Authorization: Bearer $ADMIN_TOKEN" \
  "$BASE_URL/users/$NEW_USER_ID" | python3 -m json.tool
echo ""

echo "✏️  Step 5: Update user (PATCH)"
curl -s -X PATCH "$BASE_URL/users/$NEW_USER_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"is_business":false}' | python3 -m json.tool
echo ""

echo "✏️  Step 6: Update user (PUT)"
curl -s -X PUT "$BASE_URL/users/$NEW_USER_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "email":"updated@example.com",
    "is_active":true,
    "is_admin":false,
    "is_business":true
  }' | python3 -m json.tool
echo ""

echo "🗑️  Step 7: Delete user"
curl -i -X DELETE "$BASE_URL/users/$NEW_USER_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
echo "✅ User deleted"
echo ""

echo "✅ All tests completed!"
```

## 🎯 Use Cases

### Admin Dashboard - User Management
```javascript
// List all users with pagination
async function loadUsers(page = 1, pageSize = 10) {
  const response = await fetch(
    `${API_BASE_URL}/users?page=${page}&page_size=${pageSize}`,
    {
      headers: { 'Authorization': `Bearer ${adminToken}` }
    }
  );
  const data = await response.json();
  return data; // { users: [...], total, page, page_size }
}

// Deactivate user
async function deactivateUser(userId) {
  const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${adminToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ is_active: false })
  });
  return response.json();
}

// Promote user to admin
async function makeAdmin(userId) {
  const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${adminToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ is_admin: true })
  });
  return response.json();
}

// Delete user
async function deleteUser(userId) {
  const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${adminToken}` }
  });
  return response.status === 204;
}
```

### User Profile Settings
```javascript
// Get current user profile
async function getMyProfile() {
  const token = localStorage.getItem('access_token');
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
}

// Update email
async function updateEmail(userId, newEmail) {
  const token = localStorage.getItem('access_token');
  const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ email: newEmail })
  });
  return response.json();
}

// Upgrade to business account
async function upgradeToBusiness(userId) {
  const token = localStorage.getItem('access_token');
  const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ is_business: true })
  });
  return response.json();
}
```

## 🔒 Security Features

1. **Role-Based Access Control (RBAC)**
   - Admin vs regular user permissions
   - Field-level access control
   - Cannot delete own admin account

2. **Input Validation**
   - Email format validation
   - UUID format validation
   - Email uniqueness checks

3. **Authentication Required**
   - All endpoints require valid JWT token
   - Token validation on every request

4. **Authorization Checks**
   - Users can only access their own data (except admins)
   - Admins have full access to all operations
   - Specific permissions for each field

## 🏗️ Architecture

The implementation follows Clean Architecture principles:

### Domain Layer
- `User` entity with business logic (activate, deactivate, record_login)
- `UserId` and `EmailAddress` value objects with validation

### Infrastructure Layer
- `SqlAlchemyUserRepository` - Data persistence
- `UserMapper` - Entity ↔ Model conversion
- Added `list_all()` and `count()` methods for pagination

### Application Layer
- User management business logic in router
- Authorization checks
- Transaction management via Unit of Work

### Presentation Layer
- RESTful API endpoints
- Request/response schemas with Pydantic
- OpenAPI documentation

## 📊 Data Models

### UserResponse (GET responses)
```typescript
{
  id: string;              // UUID
  email: string;
  is_active: boolean;
  is_admin: boolean;
  is_business: boolean;
  created_at: string;      // ISO 8601 datetime
  last_login: string | null; // ISO 8601 datetime
}
```

### UserUpdateRequest (PUT)
```typescript
{
  email: string;           // Email format
  is_active: boolean;
  is_admin: boolean;
  is_business: boolean;
}
```

### UserPartialUpdateRequest (PATCH)
```typescript
{
  email?: string;          // All fields optional
  is_active?: boolean;
  is_admin?: boolean;
  is_business?: boolean;
}
```

### UserListResponse (GET /users)
```typescript
{
  users: UserResponse[];
  total: number;           // Total count
  page: number;            // Current page
  page_size: number;       // Items per page
}
```

## 📝 Next Steps

1. **Password Management**
   - Add change password endpoint
   - Add reset password flow
   - Add set password for admin-created users

2. **Enhanced Features**
   - Search/filter users by email, status
   - Sort users by various fields
   - Bulk operations (activate/deactivate multiple)
   - User activity logs
   - Email verification status

3. **Soft Deletes**
   - Implement soft delete instead of hard delete
   - Add restore deleted user endpoint
   - Maintain audit trail

4. **Production**
   - Rate limiting for admin endpoints
   - Audit logging for all admin actions
   - User data export (GDPR compliance)
   - Batch user import

## ✅ Testing Results

All endpoints tested and verified:
- ✅ GET /users - List with pagination (admin only)
- ✅ GET /users/{user_id} - Get by ID (with proper authorization)
- ✅ POST /users - Create user (admin only)
- ✅ PUT /users/{user_id} - Full update (with field-level permissions)
- ✅ PATCH /users/{user_id} - Partial update (with field-level permissions)
- ✅ DELETE /users/{user_id} - Delete user (admin only)
- ✅ Authorization enforcement (admin vs regular user)
- ✅ Error handling (404, 403, 401, 400)

## 🎉 Status

**Complete and Production-Ready!** All user management endpoints are fully functional with comprehensive authorization, validation, and error handling.
