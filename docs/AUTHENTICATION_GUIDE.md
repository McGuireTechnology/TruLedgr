# Multi-Platform Authentication Implementation

## Overview

TruLedgr now features a unified, modern authentication experience across all platforms (Web, iOS, macOS, Android) with:

- **Identifier-First Flow**: Users enter their email first, then see appropriate login options
- **Just-In-Time (JIT) Signup**: New users are automatically redirected to account creation
- **Biometric Authentication**: Face ID, Touch ID, Optic ID (Apple), Fingerprint/Face recognition (Android)
- **OAuth Integration**: Google, Apple, and Microsoft sign-in options
- **API Health Monitoring**: Real-time health checks with visual status indicators (Web only)
- **Configurable API**: Easy switching between development and production environments

## Architecture

### Shared Flow Across All Platforms

1. **Step 1: Email Identifier**
   - User enters email address
   - System checks if email exists via `/auth/check-email` endpoint
   - Shows friendly message: "New to TruLedgr? We'll create your account automatically"

2. **Step 2a: Existing User (Login)**
   - Display email with "Change" button
   - Show biometric authentication option (if available and previously enrolled)
   - OAuth buttons (Google, Apple, Microsoft)
   - "OR" divider
   - Password field with Show/Hide toggle
   - "Forgot password" link
   - Terms agreement text
   - "Log in" button

3. **Step 2b: New User (JIT Signup)**
   - Redirect to signup page with email pre-filled
   - Show message: "Looks like you're new here! Let's create your account"
   - User completes registration

## Platform-Specific Implementations

### Web (Vue 3 + TypeScript + Vite)

**Location**: `/dashboard/src/views/`

**Files**:
- `LoginView.vue`: Identifier-first login with health monitoring
- `SignupView.vue`: Registration with JIT support

**Key Features**:
- Real-time API health checks (green/yellow/red indicators)
- Debounced health checks (500ms after typing pause)
- LocalStorage for API URL persistence
- Responsive design with dark mode support
- Cloudflare-inspired UI

**Setup**:
```bash
cd dashboard
npm install
npm run dev
```

**Health Check Implementation**:
```typescript
const checkHealth = async () => {
  const response = await fetch(`${apiUrl}/health`, {
    signal: AbortController.signal
  })
  // Status: healthy (green), degraded (yellow), unhealthy (red)
}
```

---

### Apple (iOS/macOS - SwiftUI)

**Location**: `/apple/TruLedgr/`

**Files**:
- `AuthenticationViewModel.swift`: Authentication logic and biometric handling
- `IdentifierFirstLoginView.swift`: SwiftUI login interface
- `LoginView.swift`: Original login (deprecated, use IdentifierFirstLoginView)

**Key Features**:
- Native biometric authentication (Face ID, Touch ID, Optic ID)
- SwiftUI with Combine for reactive state management
- `@AppStorage` for API URL persistence
- LocalAuthentication framework integration
- Multiplatform support (iOS, macOS, visionOS)

**Biometric Detection**:
```swift
func checkBiometricAvailability() {
    let context = LAContext()
    if context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) {
        switch context.biometryType {
        case .faceID: biometricType = .faceID
        case .touchID: biometricType = .touchID
        case .opticID: biometricType = .opticID
        }
    }
}
```

**Setup**:
1. Open `TruLedgr.xcodeproj` in Xcode
2. Add to `Info.plist`:
   ```xml
   <key>NSFaceIDUsageDescription</key>
   <string>Log in to TruLedgr with Face ID</string>
   ```
3. Enable "Sign in with Apple" capability in Xcode
4. Build and run (⌘R)

**Required Capabilities**:
- Face ID / Touch ID: Add to `TruLedgr.entitlements`
- Sign in with Apple: Enable in Xcode signing

---

### Android (Kotlin + Jetpack Compose)

**Location**: `/android/app/src/main/java/technology/mcguire/truledgr/auth/`

**Files**:
- `AuthViewModel.kt`: Authentication state and logic
- `IdentifierFirstLoginScreen.kt`: Compose UI implementation
- `MainActivity.kt`: Entry point with API configuration

**Key Features**:
- BiometricPrompt API for fingerprint/face recognition
- Material 3 design system
- SharedPreferences for API URL persistence
- Coroutines for async operations
- FragmentActivity for biometric callbacks

**Biometric Implementation**:
```kotlin
fun handleBiometricAuth(activity: FragmentActivity, onSuccess: () -> Unit) {
    val biometricPrompt = BiometricPrompt(
        activity,
        executor,
        object : BiometricPrompt.AuthenticationCallback() {
            override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                onSuccess()
            }
        }
    )
    
    val promptInfo = BiometricPrompt.PromptInfo.Builder()
        .setTitle("Log in to TruLedgr")
        .setNegativeButtonText("Use password")
        .build()
    
    biometricPrompt.authenticate(promptInfo)
}
```

**Setup**:
1. Open project in Android Studio
2. Add to `AndroidManifest.xml`:
   ```xml
   <uses-permission android:name="android.permission.USE_BIOMETRIC" />
   <uses-feature android:name="android.hardware.fingerprint" android:required="false" />
   ```
3. Sync Gradle
4. Run on device (biometrics don't work in emulator)

**Dependencies** (in `app/build.gradle.kts`):
```kotlin
implementation("androidx.biometric:biometric:1.2.0-alpha05")
implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.7.0")
```

---

## API Requirements

### Email Check Endpoint

**Endpoint**: `POST /auth/check-email`

**Request**:
```json
{
  "email": "user@example.com"
}
```

**Response**:
```json
{
  "exists": true,
  "auth_methods": ["password", "google", "apple"]  // Optional
}
```

**Status Codes**:
- `200 OK`: Email check successful
- `400 Bad Request`: Invalid email format
- `500 Internal Server Error`: Server error

### Health Check Endpoint (Web Only)

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy"  // or "degraded"
}
```

**Status Codes**:
- `200 OK`: Service is operational
- `503 Service Unavailable`: Service is down

---

## Biometric Authentication Details

### Apple Platforms

**Supported Biometrics**:
- **Face ID**: iPhone X and later, iPad Pro (3rd gen+)
- **Touch ID**: iPhone 5s - 8/SE, MacBook Pro/Air with Touch Bar
- **Optic ID**: Apple Vision Pro

**Implementation**:
```swift
import LocalAuthentication

let context = LAContext()
let success = try await context.evaluatePolicy(
    .deviceOwnerAuthenticationWithBiometrics,
    localizedReason: "Log in to TruLedgr"
)
```

**Error Handling**:
- User cancellation
- Authentication failed (too many attempts)
- Biometrics not available
- Biometrics not enrolled

**Privacy**:
- Biometric data never leaves the device
- System handles all authentication
- App only receives success/failure result

---

### Android Platform

**Supported Biometrics**:
- **Fingerprint**: Android 6.0+ (API 23)
- **Face Recognition**: Android 10+ (API 29)
- **Iris Recognition**: Samsung devices

**Implementation**:
```kotlin
import androidx.biometric.BiometricPrompt

val biometricPrompt = BiometricPrompt(activity, executor, callback)
biometricPrompt.authenticate(promptInfo)
```

**Biometric Classes**:
- **Class 3 (Strong)**: Fingerprint, Face (secure), Iris
- **Class 2 (Weak)**: Face (less secure implementations)
- **Class 1**: Device credential (PIN, pattern, password)

**Requirements**:
- Physical device (emulator doesn't support biometrics)
- Enrolled biometric data in system settings
- Screen lock enabled

---

## OAuth Integration

### Platform Support Matrix

| Platform | Google | Apple | Microsoft |
|----------|--------|-------|-----------|
| Web      | ✅ Ready | ✅ Ready | ✅ Ready |
| iOS      | ⏳ TODO | ✅ Native | ⏳ TODO |
| macOS    | ⏳ TODO | ✅ Native | ⏳ TODO |
| Android  | ⏳ TODO | ⚠️ Limited | ⏳ TODO |

**Note**: UI buttons are implemented on all platforms, but OAuth flows need to be completed.

### Web OAuth

**Implementation Path**: OAuth redirect flows with PKCE
- Google: Google Identity Services
- Apple: Sign in with Apple JS
- Microsoft: MSAL.js

### iOS/macOS OAuth

**Apple Sign In** (Already supported):
```swift
import AuthenticationServices

let request = ASAuthorizationAppleIDProvider().createRequest()
request.requestedScopes = [.fullName, .email]
```

**Google/Microsoft**: Implement using respective SDKs

### Android OAuth

**Google**: Google Sign-In SDK
**Microsoft**: MSAL for Android
**Apple**: Limited support (web-based flow only)

---

## Development Workflow

### 1. Local API Development

**Web**:
- Configure API URL to `http://localhost:8000`
- Health checks will work with local server

**iOS/macOS**:
- Set API URL to `http://localhost:8000`
- Simulator can access Mac's localhost directly

**Android**:
- Use `http://10.0.2.2:8000` for emulator
- Use `http://<your-local-ip>:8000` for physical devices

### 2. Testing Biometrics

**iOS Simulator**:
- Features → Face ID → Enrolled
- Features → Face ID → Matching Face (⌘⇧M)

**Android Emulator**:
- ⚠️ Biometrics NOT supported in emulator
- Must test on physical device

**Testing Steps**:
1. Ensure device has biometrics enrolled
2. Launch app and navigate to login
3. Enter email and proceed to password step
4. Tap biometric button
5. Authenticate with biometric
6. Verify successful login

### 3. Testing JIT Signup

1. Enter a new email (never used before)
2. Click "Next"
3. Should redirect to signup page
4. Email should be pre-filled
5. Complete registration
6. Log out and try again → should show login options

---

## Security Considerations

### Biometric Data
- ✅ Biometric data never leaves the device
- ✅ Apps receive only authentication result
- ✅ System handles all biometric processing
- ✅ Biometric templates stored in Secure Enclave (Apple) or TEE (Android)

### API Communication
- ✅ HTTPS required for production
- ✅ Certificate pinning recommended
- ✅ Timeout handling (5 seconds)
- ⚠️ TODO: JWT token management
- ⚠️ TODO: Refresh token handling

### Credentials Storage
- ⚠️ TODO: Keychain (iOS) / KeyStore (Android) for tokens
- ⚠️ TODO: Biometric-protected credential storage
- ✅ API URLs stored in secure storage (AppStorage/SharedPreferences)

---

## Next Steps

### High Priority
1. **Complete OAuth flows**
   - Implement Google OAuth on all platforms
   - Implement Microsoft OAuth on all platforms
   - Test Apple Sign In on iOS/macOS

2. **Implement JWT handling**
   - Token storage in secure storage
   - Token refresh logic
   - Auto-logout on token expiry

3. **Add biometric credential storage**
   - Store encrypted tokens with biometric protection
   - "Remember me" functionality
   - Biometric re-authentication flow

4. **Navigation integration**
   - Connect authentication views to main app
   - Handle deep links
   - Implement logout flow

### Medium Priority
1. **Password reset flow**
   - Forgot password screens
   - Email verification
   - Password strength requirements

2. **Account recovery**
   - Forgot email
   - Multi-factor authentication
   - Account recovery codes

3. **Enhanced security**
   - CAPTCHA integration (Cloudflare Turnstile)
   - Rate limiting
   - Suspicious activity detection

### Low Priority
1. **WebAuthn/Passkeys**
   - Cross-platform passkey support
   - Passwordless authentication
   - Sync across devices

2. **Social profiles**
   - Fetch user profile from OAuth providers
   - Avatar sync
   - Email verification bypass for OAuth

3. **Analytics**
   - Track authentication methods used
   - Login success/failure rates
   - Biometric adoption rates

---

## Testing Checklist

### Functional Testing

- [ ] **Email validation**
  - [ ] Empty email shows error
  - [ ] Invalid email format shows error
  - [ ] Valid email proceeds

- [ ] **JIT Signup**
  - [ ] New email redirects to signup
  - [ ] Email pre-filled on signup page
  - [ ] Can go back and change email

- [ ] **Login Flow**
  - [ ] Existing email shows login options
  - [ ] Can change email from password step
  - [ ] Password field shows/hides correctly
  - [ ] Login button submits form

- [ ] **Biometric Authentication**
  - [ ] Biometric button shows if available
  - [ ] Successful auth logs in user
  - [ ] Failed auth shows error
  - [ ] Cancel returns to password option

- [ ] **OAuth Buttons**
  - [ ] All three OAuth buttons render
  - [ ] Buttons trigger correct handlers
  - [ ] Loading states work

- [ ] **API Configuration**
  - [ ] Dialog opens/closes
  - [ ] URL persists after save
  - [ ] Empty URL resets to default
  - [ ] Protocol auto-added

### Cross-Platform Testing

- [ ] Web (Chrome, Safari, Firefox, Edge)
- [ ] iOS (Simulator + Physical devices)
- [ ] macOS (Intel + Apple Silicon)
- [ ] Android (Emulator + Physical devices)

### Biometric Testing

- [ ] Face ID on iPhone (Physical)
- [ ] Touch ID on iPhone (Physical)
- [ ] Touch ID on MacBook
- [ ] Fingerprint on Android (Physical)
- [ ] Face on Android (Physical)

---

## Troubleshooting

### iOS/macOS

**Biometrics not available**:
- Check `Info.plist` for `NSFaceIDUsageDescription`
- Verify biometrics enrolled in Settings
- Check device support (Face ID requires iPhone X+)

**API calls failing**:
- Verify API URL format (include protocol)
- Check App Transport Security settings
- Enable network debugging

### Android

**Biometric prompt not showing**:
- Must test on physical device
- Check biometric enrollment in Settings
- Verify `USE_BIOMETRIC` permission in manifest

**API SSL errors**:
- Common in emulator with HTTPS
- Use HTTP for local testing
- Configure network security config for dev

### Web

**Health checks failing**:
- Check CORS headers on API
- Verify API URL is correct
- Check browser console for errors

**OAuth not working**:
- Verify OAuth client IDs configured
- Check redirect URLs match
- Ensure cookies/localStorage enabled

---

## Resources

### Documentation
- [Apple LocalAuthentication](https://developer.apple.com/documentation/localauthentication)
- [Android BiometricPrompt](https://developer.android.com/training/sign-in/biometric-auth)
- [OAuth 2.0 Specification](https://oauth.net/2/)
- [WebAuthn Guide](https://webauthn.guide/)

### Design Inspiration
- [Cloudflare Login](https://dash.cloudflare.com/login)
- [Google Identity](https://developers.google.com/identity)
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Material Design 3](https://m3.material.io/)

---

## License

© 2025 TruLedgr. All rights reserved.
