# ✅ Added Username Field - Complete

## Changes Made

A `username` field has been added to the TruLedgr API as an alternative login method and public profile name.

## Summary of Changes

### 1. Domain Layer - User Entity

**`api/entities/user.py`**
- Added `username: str` field between `id` and `email`
- Username is now a core part of the User entity

### 2. Infrastructure Layer - Database Model

**`api/repositories/models/user.py`**
- Added `username` column with constraints:
  - Type: `VARCHAR(50)`
  - Unique: Yes
  - Nullable: No
  - Indexed: Yes
- Updated `__repr__` to include username

### 3. Infrastructure Layer - Mapper

**`api/repositories/mappers/user.py`**
- Updated `to_entity()` to map `username` from model to entity
- Updated `to_model()` to map `username` from entity to model
- Updated `update_model_from_entity()` to sync username changes

### 4. Repository Layer

**`api/repositories/user.py` (Interface)**
- Added `get_by_username(username: str) -> Optional[User]`
- Added `exists_by_username(username: str) -> bool`

**`api/repositories/user_repository.py` (Implementation)**
- Implemented `get_by_username()` with database query
- Implemented `exists_by_username()` for uniqueness checks

### 5. Presentation Layer - Schemas

**`api/schemas/auth.py`**
- **UserRegistrationRequest**: Added required `username` field
  - Validation: 3-50 characters, alphanumeric with _ and -
  - Pattern: `^[a-zA-Z0-9_-]+$`
- **LoginRequest**: Updated to support login with either username OR email
  - Both fields are now optional
  - At least one must be provided
- **UserResponse**: Added `username` field in response
- **UserUpdateRequest**: Added `username` field (required for PUT)
- **UserPartialUpdateRequest**: Added optional `username` field (for PATCH)

### 6. API Layer - Authentication Router

**`api/routers/auth.py`**

**Registration** (`POST /auth/register`):
- Now requires `username` in addition to email
- Checks for duplicate username before creating user
- Creates user with username field

**Login** (`POST /auth/login`):
- Now accepts login with either `username` or `email`
- Validates that at least one identifier is provided
- Supports password authentication with username
- Returns JWT token on successful authentication

**Current User** (`GET /auth/me`):
- Returns `username` in user profile response

### 7. API Layer - User Management Router

**`api/routers/users.py`**

**List Users** (`GET /users`):
- Includes `username` in user list responses

**Get User** (`GET /users/{user_id}`):
- Includes `username` in user detail response

**Create User** (`POST /users` - Admin only):
- Requires `username` field
- Checks for duplicate username before creation

**Update User** (`PUT /users/{user_id}`):
- Allows updating username
- Checks for duplicate username before update
- Prevents username conflicts

**Partial Update** (`PATCH /users/{user_id}`):
- Allows optionally updating username
- Validates username uniqueness if provided

## Database Schema Changes

### Before
```sql
CREATE TABLE users (
    id UUID NOT NULL,
    email VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL,
    is_admin BOOLEAN NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    last_login DATETIME,
    PRIMARY KEY (id)
)
```

### After
```sql
CREATE TABLE users (
    id UUID NOT NULL,
    username VARCHAR(50) NOT NULL,  -- NEW FIELD
    email VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL,
    is_admin BOOLEAN NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    last_login DATETIME,
    PRIMARY KEY (id)
)

CREATE UNIQUE INDEX ix_users_username ON users (username)  -- NEW INDEX
CREATE UNIQUE INDEX ix_users_email ON users (email)
```

## API Examples

### Registration with Username
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Login with Email (Original Method)
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Login with Username (New Method)
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "SecurePass123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Get Current User Profile
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/auth/me
```

**Response:**
```json
{
  "id": "4f6559b6-2d95-49b0-bfac-2908391873ad",
  "username": "johndoe",
  "email": "john@example.com",
  "is_active": true,
  "is_admin": false,
  "created_at": "2025-10-13T05:25:59.455046",
  "last_login": "2025-10-13T05:26:16.845394"
}
```

## Username Validation Rules

- **Length**: 3-50 characters
- **Allowed Characters**: 
  - Lowercase letters: a-z
  - Uppercase letters: A-Z
  - Numbers: 0-9
  - Underscore: _
  - Hyphen: -
- **Pattern**: `^[a-zA-Z0-9_-]+$`
- **Uniqueness**: Must be unique across all users
- **Required**: Cannot be null or empty

## Valid Username Examples

✅ `johndoe`
✅ `jane_doe`
✅ `user123`
✅ `mary-jane`
✅ `admin_user_2025`

## Invalid Username Examples

❌ `jo` (too short, minimum 3 characters)
❌ `john.doe` (contains period, not allowed)
❌ `john doe` (contains space, not allowed)
❌ `john@doe` (contains @, not allowed)
❌ `user#123` (contains #, not allowed)

## Frontend Impact

### TypeScript Interface Updates

**Before:**
```typescript
interface User {
  id: string;
  email: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
  last_login: string | null;
}
```

**After:**
```typescript
interface User {
  id: string;
  username: string;        // NEW FIELD
  email: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
  last_login: string | null;
}
```

### Registration Form Updates

**Before:**
```vue
<template>
  <form @submit.prevent="register">
    <input v-model="email" type="email" required />
    <input v-model="password" type="password" required />
    <button type="submit">Register</button>
  </form>
</template>

<script setup>
const email = ref('');
const password = ref('');

async function register() {
  await api.post('/auth/register', {
    email: email.value,
    password: password.value
  });
}
</script>
```

**After:**
```vue
<template>
  <form @submit.prevent="register">
    <input 
      v-model="username" 
      type="text" 
      placeholder="Username"
      pattern="^[a-zA-Z0-9_-]{3,50}$"
      required 
    />
    <input v-model="email" type="email" required />
    <input v-model="password" type="password" required />
    <button type="submit">Register</button>
  </form>
</template>

<script setup>
const username = ref('');
const email = ref('');
const password = ref('');

async function register() {
  await api.post('/auth/register', {
    username: username.value,
    email: email.value,
    password: password.value
  });
}
</script>
```

### Login Form Updates

**Before:**
```vue
<template>
  <form @submit.prevent="login">
    <input v-model="email" type="email" required />
    <input v-model="password" type="password" required />
    <button type="submit">Login</button>
  </form>
</template>

<script setup>
const email = ref('');
const password = ref('');

async function login() {
  const response = await api.post('/auth/login', {
    email: email.value,
    password: password.value
  });
  // Handle token...
}
</script>
```

**After (Supports Both Email and Username):**
```vue
<template>
  <form @submit.prevent="login">
    <input 
      v-model="identifier" 
      type="text" 
      placeholder="Username or Email"
      required 
    />
    <input v-model="password" type="password" required />
    <button type="submit">Login</button>
  </form>
</template>

<script setup>
const identifier = ref('');
const password = ref('');

async function login() {
  // Determine if identifier is email or username
  const isEmail = identifier.value.includes('@');
  
  const payload = {
    password: password.value,
    ...(isEmail 
      ? { email: identifier.value }
      : { username: identifier.value }
    )
  };
  
  const response = await api.post('/auth/login', payload);
  // Handle token...
}
</script>
```

## Testing Results

### ✅ Registration Test
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"johndoe","email":"john@example.com","password":"SecurePass123"}'
```

**Result:** Success - User created with username

### ✅ Login with Email Test
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"SecurePass123"}'
```

**Result:** Success - JWT token returned

### ✅ Login with Username Test
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"johndoe","password":"SecurePass123"}'
```

**Result:** Success - JWT token returned

### ✅ Get User Profile Test
```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/auth/me
```

**Result:** Success - Profile includes username field

## Benefits

1. **Better User Experience**: Users can choose memorable usernames instead of typing full email addresses
2. **Public Profile Name**: Username serves as a public identifier (instead of exposing email addresses)
3. **Flexibility**: Users can login with either username or email
4. **Privacy**: Email addresses don't need to be public-facing
5. **Social Features Ready**: Username field supports future social/sharing features

## Migration Notes

### For Development
The development database was recreated with the new schema:
```bash
rm -f truledgr.db
poetry run python -m api.init_db
```

### For Production
For production databases with existing users, you'll need to:

1. **Add the column** with a temporary default or allow NULL initially
2. **Migrate existing data** by generating usernames from existing data
3. **Update constraints** to make username NOT NULL and UNIQUE
4. **Update application** to use the new field

Example migration strategy:
```sql
-- Step 1: Add column (nullable initially)
ALTER TABLE users ADD COLUMN username VARCHAR(50);

-- Step 2: Generate usernames for existing users
-- (Use email prefix or generate from user ID)
UPDATE users SET username = LOWER(SPLIT_PART(email, '@', 1)) || '_' || SUBSTRING(id::text, 1, 8)
WHERE username IS NULL;

-- Step 3: Add constraints
ALTER TABLE users ALTER COLUMN username SET NOT NULL;
CREATE UNIQUE INDEX ix_users_username ON users (username);
```

## Summary

✅ **Username field successfully added**
- Database schema updated
- All API endpoints support username
- Login works with both username and email
- Registration requires username
- User profiles display username
- Uniqueness enforced at database level

The TruLedgr API now supports usernames as an alternative to email for authentication and as a public profile identifier.
