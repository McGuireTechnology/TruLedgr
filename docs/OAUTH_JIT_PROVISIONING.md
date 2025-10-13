# OAuth with JIT Provisioning - Implementation Update

## Summary

Updated the OAuth authentication flow to use a **unified login screen** with **Just-In-Time (JIT) user provisioning**, eliminating the need for identifier-first authentication enumeration.

## Changes Made

### 1. **Removed Identifier-First Auth Endpoint**

**Rationale:** Privacy and UX improvement
- Prevents username/email enumeration attacks
- Simplifies login flow - all options visible upfront
- No need to query which auth methods are available

**Removed:**
- `POST /auth/check-auth-methods` endpoint
- `AuthMethodsRequest` schema
- `AuthMethodsResponse` schema

**Files Modified:**
- `api/routers/oauth.py` - Removed endpoint and related code
- `api/schemas/oauth.py` - Removed schemas with explanatory comment

### 2. **Updated Login Flow Design**

**New UX Flow:**
```
Login Screen (All Options Visible)
├── Username/Email + Password → Traditional login
├── Google Button → OAuth JIT provisioning
├── Microsoft Button → OAuth JIT provisioning
└── Apple Button → OAuth JIT provisioning
```

**Benefits:**
- ✅ Simple, intuitive interface
- ✅ No enumeration of existing accounts
- ✅ Privacy-friendly (no information leakage)
- ✅ Faster login (no multi-step identifier check)

### 3. **Just-In-Time (JIT) User Provisioning**

**How It Works:**

When a user signs in with OAuth:

1. **User clicks OAuth provider button** (Google/Microsoft/Apple)
2. **OAuth flow completes** with authorization code
3. **Backend receives user info** from OAuth provider (email, name, id)
4. **Check if user exists:**
   - By `provider_user_id` in `oauth_connections` table
   - By `email` in `users` table
5. **If user doesn't exist:** Create new user automatically
   - Email from OAuth provider
   - Auto-generate username from email or OAuth name
   - No password (OAuth-only account)
   - Create OAuth connection record
6. **If user exists:** Link OAuth connection to existing account
7. **Return JWT token** for TruLedgr API access

**Database Support:**
- `oauth_connections` table with unique constraint on `(user_id, provider)`
- Supports multiple OAuth connections per user (one per provider)
- Cascade delete when user is removed

### 4. **Updated Documentation**

**OAUTH_IMPLEMENTATION.md Changes:**
- Removed identifier-first auth endpoint documentation
- Updated overview to highlight JIT provisioning
- Simplified frontend integration example (single-screen login)
- Updated benefits section (no enumeration, JIT provisioning)
- Added JIT provisioning explanation in callback documentation

### 5. **OAuth Callback Enhancement**

**Added TODO Comments for JIT Implementation:**

The OAuth callback endpoint (`POST /auth/oauth/callback`) needs to implement:

```python
# 1. Exchange authorization code for access token with OAuth provider
# 2. Fetch user info from OAuth provider (email, name, id)
# 3. Look up user by OAuth provider_user_id or email
# 4. If user doesn't exist, create new user (JIT provisioning):
#    - Generate username from email or OAuth name
#    - Set email from OAuth provider
#    - Leave hashed_password empty (OAuth-only account)
# 5. Create or update OAuth connection
# 6. Return JWT access token
```

**Dependencies:**
- Requires `httpx` library for OAuth provider HTTP requests
- State management for CSRF protection

## Frontend Integration

### Before (Identifier-First)
```typescript
// Multi-step process
1. User enters identifier
2. Frontend checks available auth methods
3. Show password field OR OAuth buttons
4. User authenticates
```

### After (Unified Screen)
```typescript
// Single screen
1. Show all options: password fields + OAuth buttons
2. User chooses their preferred method
3. Authenticate directly
```

### Example Login Component

```vue
<template>
  <div class="login">
    <!-- Password Login -->
    <input v-model="identifier" placeholder="Username or email" />
    <input v-model="password" type="password" placeholder="Password" />
    <button @click="loginWithPassword">Sign In</button>

    <!-- OAuth Buttons -->
    <button @click="loginWithOAuth('google')">Continue with Google</button>
    <button @click="loginWithOAuth('microsoft')">Continue with Microsoft</button>
    <button @click="loginWithOAuth('apple')">Continue with Apple</button>
  </div>
</template>
```

## Security & Privacy

### Privacy Improvements

1. **No Account Enumeration:**
   - Cannot probe to find valid usernames/emails
   - No information leakage about existing accounts
   - Equal treatment of all identifiers

2. **No OAuth Connection Disclosure:**
   - Cannot map username → OAuth providers
   - Cannot discover which OAuth accounts are linked
   - Protected against reconnaissance attacks

### Security Features

1. **State Parameter:** CSRF protection in OAuth flow
2. **Unique Constraints:** One connection per provider per user
3. **Cascade Delete:** Clean up connections when user deleted
4. **Token Security:** Secure storage of OAuth tokens in database
5. **JIT Validation:** Only create users from verified OAuth providers

## API Endpoints (Current State)

### ✅ Working Endpoints

- `GET /auth/oauth/connections` - List user's OAuth connections
- `POST /auth/oauth/initiate` - Start OAuth flow
- `DELETE /auth/oauth/connections/{provider}` - Disconnect OAuth provider

### ⚠️ Needs Implementation

- `POST /auth/oauth/callback` - Complete OAuth flow (JIT provisioning)
  - Token exchange with OAuth providers
  - User info retrieval
  - JIT user account creation
  - OAuth connection creation/update
  - JWT token generation

## Next Steps

### 1. Add httpx Dependency

```bash
poetry add httpx
```

### 2. Implement OAuth Provider Services

Create `api/services/oauth_providers.py`:

```python
class GoogleOAuthProvider:
    async def exchange_code_for_token(code: str) -> dict
    async def get_user_info(access_token: str) -> dict

class MicrosoftOAuthProvider:
    async def exchange_code_for_token(code: str) -> dict
    async def get_user_info(access_token: str) -> dict

class AppleOAuthProvider:
    async def exchange_code_for_token(code: str) -> dict
    async def get_user_info(access_token: str) -> dict
```

### 3. Implement JIT Provisioning Logic

In `POST /auth/oauth/callback`:

```python
# Get user info from OAuth provider
user_info = await provider.get_user_info(access_token)

# Try to find existing user
user = await uow.oauth_connections.get_by_provider_user_id(
    provider, user_info['id']
)

if not user:
    # Try by email
    user = await uow.users.get_by_email(user_info['email'])

if not user:
    # JIT PROVISIONING - Create new user
    username = generate_username(user_info['email'], user_info['name'])
    user = User(
        id=UserId(uuid.uuid4()),
        username=username,
        email=EmailAddress(user_info['email']),
        hashed_password='',  # OAuth-only account
        is_active=True,
        is_admin=False
    )
    await uow.users.create(user)

# Create/update OAuth connection
# Return JWT token
```

### 4. Configure OAuth Apps

Set up OAuth applications with each provider and configure environment variables.

### 5. Test End-to-End

- Test new user sign-up via OAuth
- Test existing user OAuth linking
- Test multiple OAuth providers per user
- Test disconnect functionality

## Benefits Summary

| Aspect | Before | After |
|--------|--------|-------|
| **UX** | Multi-step identifier-first | Single unified screen |
| **Privacy** | Username enumeration possible | No enumeration |
| **New Users** | Separate registration flow | Instant JIT provisioning |
| **Complexity** | Check methods → Choose → Auth | Choose → Auth |
| **Security** | Username mapping attacks possible | No information leakage |

## Migration Notes

- **No database changes required** - oauth_connections table already supports JIT
- **No breaking changes** - Removed endpoint was internal-only
- **Frontend needs update** - Remove identifier check, show all options upfront
- **OAuth callback** - Update to support JIT provisioning when implemented

## Conclusion

This update significantly improves both **user experience** and **privacy** by:

1. Eliminating the multi-step identifier-first flow
2. Preventing account enumeration attacks
3. Enabling instant sign-up via OAuth (JIT provisioning)
4. Simplifying the frontend login interface

The OAuth foundation is complete and ready for JIT provisioning implementation once the callback handler is built with httpx.
