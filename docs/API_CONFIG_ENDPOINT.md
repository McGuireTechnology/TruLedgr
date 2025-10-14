# API Configuration Endpoint

## Overview

The `/config` endpoint allows frontend applications to dynamically discover which authentication methods are available and configured. This enables frontends to show/hide login options based on backend configuration.

## Endpoint

**URL:** `GET /config`  
**Authentication:** Not required (public endpoint)  
**Response Type:** JSON

## Response Schema

```json
{
  "authentication_methods": [
    {
      "type": "string",      // "google", "microsoft", "apple"
      "enabled": boolean,     // true if configured and available
      "name": "string"        // Display name for UI
    }
  ],
  "password_auth_enabled": boolean  // Always true currently
}
```

## Example Response

### When No OAuth is Configured

```json
{
  "authentication_methods": [
    {
      "type": "google",
      "enabled": false,
      "name": "Google"
    },
    {
      "type": "microsoft",
      "enabled": false,
      "name": "Microsoft"
    },
    {
      "type": "apple",
      "enabled": false,
      "name": "Apple"
    }
  ],
  "password_auth_enabled": true
}
```

### When Google and Microsoft are Configured

```json
{
  "authentication_methods": [
    {
      "type": "google",
      "enabled": true,
      "name": "Google"
    },
    {
      "type": "microsoft",
      "enabled": true,
      "name": "Microsoft"
    },
    {
      "type": "apple",
      "enabled": false,
      "name": "Apple"
    }
  ],
  "password_auth_enabled": true
}
```

## Frontend Integration

### Vue 3 Example

```vue
<template>
  <div class="login">
    <h1>Sign In</h1>

    <!-- Password Login (always shown) -->
    <div v-if="config.password_auth_enabled" class="password-login">
      <input v-model="identifier" placeholder="Username or email" />
      <input v-model="password" type="password" placeholder="Password" />
      <button @click="loginWithPassword">Sign In</button>
    </div>

    <!-- OAuth Providers (only shown if enabled) -->
    <div class="oauth-login">
      <p v-if="hasOAuthProviders" class="divider">Or sign in with</p>
      
      <button
        v-for="method in enabledOAuthMethods"
        :key="method.type"
        @click="loginWithOAuth(method.type)"
        :class="`oauth-btn ${method.type}`"
      >
        Continue with {{ method.name }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { api } from '@/api';

const identifier = ref('');
const password = ref('');
const config = ref({
  authentication_methods: [],
  password_auth_enabled: true
});

// Get enabled OAuth methods
const enabledOAuthMethods = computed(() => {
  return config.value.authentication_methods.filter(m => m.enabled);
});

const hasOAuthProviders = computed(() => {
  return enabledOAuthMethods.value.length > 0;
});

// Fetch API config on mount
onMounted(async () => {
  try {
    const response = await api.get('/config');
    config.value = response.data;
  } catch (error) {
    console.error('Failed to load API config:', error);
  }
});

async function loginWithPassword() {
  const isEmail = identifier.value.includes('@');
  const payload = {
    password: password.value,
    ...(isEmail ? { email: identifier.value } : { username: identifier.value })
  };

  const response = await api.post('/auth/login', payload);
  localStorage.setItem('token', response.data.access_token);
  window.location.href = '/dashboard';
}

async function loginWithOAuth(provider) {
  const response = await api.post('/auth/oauth/initiate', {
    provider: provider,
    redirect_uri: `${window.location.origin}/auth/callback`
  });

  window.location.href = response.data.authorization_url;
}
</script>
```

### React Example

```jsx
import { useState, useEffect } from 'react';
import axios from 'axios';

function Login() {
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [config, setConfig] = useState({
    authentication_methods: [],
    password_auth_enabled: true
  });

  // Fetch API config on mount
  useEffect(() => {
    axios.get('/config')
      .then(response => setConfig(response.data))
      .catch(error => console.error('Failed to load API config:', error));
  }, []);

  const enabledOAuthMethods = config.authentication_methods.filter(m => m.enabled);

  const loginWithPassword = async () => {
    const isEmail = identifier.includes('@');
    const payload = {
      password,
      ...(isEmail ? { email: identifier } : { username: identifier })
    };

    const response = await axios.post('/auth/login', payload);
    localStorage.setItem('token', response.data.access_token);
    window.location.href = '/dashboard';
  };

  const loginWithOAuth = async (provider) => {
    const response = await axios.post('/auth/oauth/initiate', {
      provider,
      redirect_uri: `${window.location.origin}/auth/callback`
    });

    window.location.href = response.data.authorization_url;
  };

  return (
    <div className="login">
      <h1>Sign In</h1>

      {/* Password Login */}
      {config.password_auth_enabled && (
        <div className="password-login">
          <input
            value={identifier}
            onChange={(e) => setIdentifier(e.target.value)}
            placeholder="Username or email"
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
          />
          <button onClick={loginWithPassword}>Sign In</button>
        </div>
      )}

      {/* OAuth Providers */}
      {enabledOAuthMethods.length > 0 && (
        <div className="oauth-login">
          <p className="divider">Or sign in with</p>
          {enabledOAuthMethods.map(method => (
            <button
              key={method.type}
              onClick={() => loginWithOAuth(method.type)}
              className={`oauth-btn ${method.type}`}
            >
              Continue with {method.name}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default Login;
```

## Use Cases

### 1. Development Environment
- OAuth not configured → Show only password login
- Frontend automatically adapts without code changes

### 2. Staging Environment
- Google OAuth configured for testing
- Frontend shows password + Google login
- Microsoft and Apple buttons hidden

### 3. Production Environment
- All OAuth providers configured
- Frontend shows all authentication options

## Benefits

### For Developers
- **No hardcoded configuration** - Frontend adapts automatically
- **Environment agnostic** - Same frontend code works everywhere
- **Easy testing** - Test with/without OAuth in different environments

### For Users
- **Cleaner UI** - Only see available login options
- **No confusion** - Don't see disabled/broken OAuth buttons
- **Better UX** - Tailored to what's actually available

## Testing

### Test Endpoint

```bash
curl http://localhost:8000/config | python3 -m json.tool
```

### Expected Response (No OAuth Configured)

```json
{
  "authentication_methods": [
    {
      "type": "google",
      "enabled": false,
      "name": "Google"
    },
    {
      "type": "microsoft",
      "enabled": false,
      "name": "Microsoft"
    },
    {
      "type": "apple",
      "enabled": false,
      "name": "Apple"
    }
  ],
  "password_auth_enabled": true
}
```

### Test with OAuth Configured

Add to `api/.env`:
```bash
OAUTH_GOOGLE_CLIENT_ID=your_client_id
OAUTH_GOOGLE_CLIENT_SECRET=your_secret
```

Restart server and test:
```bash
curl http://localhost:8000/config | python3 -m json.tool
```

Now Google should show `"enabled": true`

## Implementation Details

### Configuration Detection

The endpoint checks for OAuth credentials in settings:

```python
google_enabled = bool(
    settings.oauth_google_client_id and
    settings.oauth_google_client_secret
)
```

An OAuth provider is considered "enabled" only if **both** client ID and client secret are configured.

### Adding New Authentication Methods

To add a new authentication method (e.g., GitHub OAuth):

1. **Add to settings** (`api/config/settings.py`):
   ```python
   oauth_github_client_id: Optional[str] = None
   oauth_github_client_secret: Optional[str] = None
   ```

2. **Add to config router** (`api/routers/config.py`):
   ```python
   github_enabled = bool(
       settings.oauth_github_client_id and
       settings.oauth_github_client_secret
   )
   
   AuthenticationMethod(
       type="github",
       enabled=github_enabled,
       name="GitHub"
   )
   ```

3. **Frontend automatically picks it up!** 🎉

## Caching Recommendations

### Frontend Caching

**Recommended:** Cache config response for the session

```javascript
// Cache in session storage
const getCachedConfig = async () => {
  const cached = sessionStorage.getItem('api_config');
  if (cached) {
    return JSON.parse(cached);
  }
  
  const response = await api.get('/config');
  sessionStorage.setItem('api_config', JSON.stringify(response.data));
  return response.data;
};
```

### Backend Caching

Currently not cached (fast enough without it), but could add:

```python
from functools import lru_cache

@lru_cache(maxsize=1)
def get_config():
    # Config logic
    pass
```

## Security Considerations

### Why This Endpoint is Public

1. **No sensitive data** - Only reveals which auth methods are available
2. **Enhances security** - Prevents users from trying unavailable methods
3. **Standard practice** - Similar to OAuth discovery endpoints
4. **No credentials exposed** - Only boolean enabled/disabled flags

### What's NOT Exposed

- ❌ OAuth client IDs/secrets
- ❌ Redirect URIs
- ❌ API keys
- ❌ User data
- ❌ Database configuration

## Future Enhancements

### Potential Additions

```json
{
  "authentication_methods": [...],
  "password_auth_enabled": true,
  "features": {
    "registration_enabled": true,
    "password_reset_enabled": true,
    "two_factor_auth_enabled": false,
    "account_linking_enabled": true
  },
  "version": "0.1.0",
  "api_url": "https://api.truledgr.app"
}
```

## Files Created/Modified

### New Files

1. **`api/schemas/config.py`** - Configuration response schemas
2. **`api/routers/config.py`** - Configuration endpoint router
3. **`API_CONFIG_ENDPOINT.md`** - This documentation

### Modified Files

1. **`api/routers/__init__.py`** - Export config router
2. **`api/main.py`** - Include config router in app

## Summary

✅ **Endpoint:** `GET /config`  
✅ **Purpose:** Dynamic authentication method discovery  
✅ **Authentication:** Not required (public)  
✅ **Response:** JSON with enabled auth methods  
✅ **Frontend:** Adapts UI based on configuration  
✅ **Benefits:** Environment-agnostic, cleaner UI, better UX  

The frontend can now automatically adapt to backend configuration without hardcoding which authentication methods are available!
