# TruLedgr Dashboard

Vue.js + Vite web ## Routing Structure

- `/` - Dashboard (protected, redirects to `/login` if not authenticated)
- `/login` - Cloudflare-style login page with OAuth (Google, Apple, Microsoft) + email/password
- `/signup` - Cloudflare-style signup page with OAuth + registration form

**Authentication Flow:**
- Unauthenticated users visiting `/` are redirected to `/login`
- After successful login, users are redirected to `/` (dashboard)
- Authenticated users visiting `/login` or `/signup` are redirected to `/`

## Project Structure

```text
dashboard/
├── src/
│   ├── views/
│   │   ├── DashboardView.vue    # Main dashboard (protected)
│   │   ├── LoginView.vue        # Cloudflare-style login page
│   │   └── SignupView.vue       # Cloudflare-style signup page
│   ├── router/
│   │   └── index.ts             # Router with auth guards
│   ├── App.vue                  # Root component
│   ├── main.ts                  # Application entry point
│   └── style.css                # Global styles
├── index.html                   # HTML template
├── vite.config.ts              # Vite configuration
├── tsconfig.json               # TypeScript configuration
└── package.json                # Dependencies and scripts
```Ledgr personal finance management.

## Setup

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Features

## Key Features

- **Cloudflare-Style Authentication**: Login and signup pages match Cloudflare's UX
  - OAuth buttons first (Google, Apple, Microsoft) with full-width prominent styling
  - Email/password form below with "Show/Hide" password toggle
  - Clean, minimal design with proper spacing
- **Protected Dashboard**: Main dashboard at `/` requires authentication
- **Navigation Guards**: Automatic redirects based on auth state
- **API URL Configuration**: Persists custom API URLs in localStorage
- **Dark Mode Support**: Automatic theme detection with CSS media queries
- **Responsive Design**: Mobile-first approach, works on all screen sizes
- **Version Display**: Shows app version (v0.1.0)
- **Future**: Passkey/WebAuthn and biometric authentication support planned

## Development

The app runs on `http://localhost:5173` by default.

API requests to `/api/*` are proxied to `http://localhost:8000` during development.

## Project Structure

```
dashboard/
├── src/
│   ├── views/
│   │   └── LoginView.vue    # Login page component
│   ├── router/
│   │   └── index.ts          # Vue Router configuration
│   ├── App.vue               # Root component
│   ├── main.ts               # Application entry point
│   └── style.css             # Global styles
├── index.html                # HTML template
├── vite.config.ts            # Vite configuration
├── tsconfig.json             # TypeScript configuration
└── package.json              # Dependencies and scripts
```

## Version Management

The dashboard version is managed by the root `version.py` script. The version number is currently hardcoded in `LoginView.vue` but can be dynamically loaded from the API or environment variables.

## Configuration

### API URL

Users can configure a custom API URL through the settings button in the login page footer. The URL is persisted in `localStorage`:

- Default: `https://api.truledgr.app`
- Custom URLs are automatically prefixed with `https://` if no protocol is specified
- Display shows URL without protocol for cleaner UI

## TODO

## Implementation TODO

**Authentication & Security:**
- [ ] Implement actual authentication logic in LoginView and SignupView
- [ ] Connect OAuth providers (Google OAuth 2.0, Apple Sign In, Microsoft Identity Platform)
- [ ] Add CAPTCHA/Turnstile for "Let us know you're human" section
- [ ] Implement WebAuthn/Passkey authentication for passwordless login
- [ ] Add biometric authentication support (Face ID, Touch ID, Windows Hello)
- [ ] Connect to real API endpoints (`/auth/register`, `/auth/login`, `/auth/token`, `/auth/refresh`)
- [ ] Implement JWT token storage and refresh logic
- [ ] Add logout functionality with token invalidation
- [ ] Implement "Forgot password" and "Forgot email" flows

**UI & UX:**
- [ ] Add form validation with visual feedback (real-time email validation, password strength indicator)
- [ ] Improve loading states and error messaging
- [ ] Add success notifications after registration
- [ ] Implement remember me functionality

**Dashboard & Features:**
- [ ] Build out dashboard content (accounts, transactions, reports, settings cards)
- [ ] Implement state management with Pinia stores (auth, user, accounts, transactions)
- [ ] Add API client service with axios/fetch and request/response interceptors
- [ ] Create account settings page
- [ ] Build transaction management screens
- [ ] Implement monthly reporting views

**Code Quality:**
- [ ] Replace hardcoded auth check (`isAuthenticated = false`) with real token validation
- [ ] Add unit tests for authentication flows
- [ ] Add E2E tests for login/signup/logout flows
