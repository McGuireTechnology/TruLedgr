# Vue Dashboard Authentication Design

## Why No Separate Welcome/Landing Page?

### The Problem with `/welcome`
In the original design, we had three routes:
- `/` - Dashboard (protected)
- `/welcome` - Landing page with Sign Up/Log In buttons
- `/login` - Full login form
- `/signup` - Full signup form

This created **unnecessary complexity**:
1. **Extra redirect step**: Unauthenticated users visit `/` → redirected to `/welcome` → click "Log In" → `/login`
2. **Duplicate content**: Both `/welcome` and `/login` showed login options
3. **Confusing UX**: Why have a "landing" page when the app is a dashboard tool, not a marketing site?

### The Solution: Direct to Login
Modern apps use a simpler flow:
- `/` - Dashboard (protected, redirects to `/login` if not authenticated)
- `/login` - Full authentication page
- `/signup` - Full registration page

**Benefits:**
- **One less click**: Users go directly from `/` → `/login` → authenticated
- **Clearer intent**: `/login` is the entry point for unauthenticated users
- **Standard pattern**: Matches Gmail, GitHub, Stripe, Vercel, and most SaaS apps

### When You WOULD Use a Welcome Page
Keep a separate landing/welcome page ONLY if you need:
- Marketing content (pricing, features, testimonials)
- Public-facing content before authentication
- A "sales pitch" for new users

For TruLedgr (a personal finance tool), users already know why they're here. They just need to log in.

---

## Cloudflare-Style Authentication Layout

### Design Decisions

#### 1. OAuth Buttons First (Full Width)
**Why:** Most users prefer social login over email/password
- Faster (no form filling)
- More secure (delegated authentication)
- Fewer passwords to remember

**Implementation:**
```vue
<button class="btn-oauth-primary">
  <svg class="oauth-icon"><!-- Google icon --></svg>
  Continue with Google
</button>
```

**Order (Cloudflare-inspired):**
1. **Google** - Most popular OAuth provider
2. **Apple** - Required for iOS apps, increasingly popular
3. **Microsoft** - Important for enterprise users

#### 2. Email/Password Below
**Why:** Still necessary for users who:
- Don't have Google/Apple/Microsoft accounts
- Prefer not to link accounts
- Work in restricted environments

**Features:**
- Show/Hide password toggle (Cloudflare pattern)
- Clean, minimal styling
- Terms of service agreement text

#### 3. "OR" Divider
Visual separator between OAuth and traditional login methods.

```vue
<div class="auth-divider">
  <span>OR</span>
</div>
```

#### 4. Show/Hide Password Button
Cloudflare shows "Show" link next to password label.

**Why:** Better UX than password visibility icons
- More discoverable (text vs icon)
- Clearer intent ("Show" vs eye icon)
- Accessible (screen readers understand text)

---

## Future Authentication Methods

### Passkeys (WebAuthn)
**What:** Passwordless authentication using device biometrics
**Why:** 
- More secure than passwords (phishing-resistant)
- Better UX (one tap to log in)
- Industry standard (supported by Apple, Google, Microsoft)

**Implementation Plan:**
```javascript
// Register passkey
await navigator.credentials.create({
  publicKey: {
    challenge: new Uint8Array(32),
    rp: { name: "TruLedgr" },
    user: {
      id: new Uint8Array(16),
      name: email,
      displayName: name
    },
    pubKeyCredParams: [{ alg: -7, type: "public-key" }]
  }
})

// Authenticate with passkey
await navigator.credentials.get({
  publicKey: { challenge: new Uint8Array(32) }
})
```

**UI Addition:**
Add passkey button above OAuth buttons (most convenient method first):
```
[🔑 Continue with Passkey]
[G Continue with Google]
[🍎 Continue with Apple]
[Ⓜ️ Continue with Microsoft]
     OR
[Email/Password Form]
```

### Biometric Authentication
**What:** Device-native biometrics (Face ID, Touch ID, Windows Hello)
**Why:**
- Seamless UX on mobile/desktop
- Secure (biometric data never leaves device)
- Fast (sub-second authentication)

**Implementation:**
- iOS/macOS: Use LocalAuthentication framework
- Android: Use BiometricPrompt API
- Web: Falls back to WebAuthn (which can trigger biometrics)

---

## Authentication Flow

```
User visits / (dashboard)
  ↓
Is authenticated? (check localStorage for authToken)
  ↓ NO
Redirect to /login
  ↓
User chooses method:
  - OAuth (Google/Apple/Microsoft)
  - Email/Password
  - Passkey (future)
  - Biometrics (future)
  ↓
Authentication successful
  ↓
Store JWT token in localStorage
  ↓
Redirect to / (dashboard)
  ↓ YES (already authenticated)
Show dashboard content
```

### Navigation Guard Logic
```typescript
router.beforeEach((to, from, next) => {
  const authToken = localStorage.getItem('authToken')
  const isAuthenticated = !!authToken // TODO: Add token validation
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    // Protected route, not authenticated → login
    next('/login')
  } else if ((to.name === 'login' || to.name === 'signup') && isAuthenticated) {
    // Already authenticated, trying to access auth pages → dashboard
    next('/')
  } else {
    // All other cases → proceed
    next()
  }
})
```

---

## Design Principles

### 1. Security First
- OAuth over passwords when possible
- Passkeys for passwordless future
- HTTPS-only (no HTTP fallback)
- JWT tokens with expiration
- Refresh token rotation

### 2. User Experience
- Minimize clicks (no unnecessary landing page)
- Clear visual hierarchy (OAuth prominent, email/password secondary)
- Accessible (keyboard navigation, screen reader support)
- Responsive (mobile-first design)

### 3. Modern Standards
- WebAuthn for passkeys
- OAuth 2.0 / OIDC for social login
- JWT for session management
- CAPTCHA/Turnstile for bot protection

### 4. Progressive Enhancement
- Basic: Email/password (works everywhere)
- Enhanced: OAuth (most users)
- Future: Passkeys (best security)
- Future: Biometrics (best UX)

---

## Comparison with Cloudflare

| Feature | Cloudflare | TruLedgr | Status |
|---------|-----------|----------|--------|
| OAuth buttons first | ✅ | ✅ | Complete |
| Full-width OAuth buttons | ✅ | ✅ | Complete |
| Show/Hide password | ✅ | ✅ | Complete |
| "OR" divider | ✅ | ✅ | Complete |
| Terms agreement text | ✅ | ✅ | Complete |
| CAPTCHA ("Let us know you're human") | ✅ Turnstile | ⏳ TODO | Planned |
| Passkey support | ❌ | ⏳ TODO | Planned |
| Biometrics | ❌ | ⏳ TODO | Planned |

---

## Summary

**No Welcome Page Because:**
- Unnecessary for a dashboard tool (not a marketing site)
- Extra redirect step hurts UX
- Modern apps go directly to login

**Cloudflare-Style Layout Because:**
- OAuth first (most convenient)
- Email/password as fallback
- Clean, accessible design
- Industry best practices

**Future Enhancements:**
- Passkeys (WebAuthn) for passwordless login
- Biometric authentication on supported devices
- CAPTCHA for bot protection
- "Remember me" persistence beyond session
