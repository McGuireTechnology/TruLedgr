# Mobile Integration Guide

This guide covers integrating iOS and Android mobile applications with the TruLedgr API.

## API Integration

### Base Configuration

**Production API URL**: `https://api.truledgr.app`
**Development API URL**: `http://localhost:8000` (when running locally)

### Authentication Flow

#### 1. User Registration
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe"
}
```

Response:
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true
}
```

#### 2. User Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 3. Authenticated Requests
Include the JWT token in the Authorization header:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Mobile App Configuration

Get mobile-specific configuration and feature flags:

```http
GET /mobile/config
Authorization: Bearer {token}
```

Response:
```json
{
  "api_version": "1.0.0",
  "min_app_version": "1.0.0",
  "force_update": false,
  "maintenance_mode": false,
  "features": {
    "biometric_auth": true,
    "push_notifications": true,
    "offline_mode": true
  }
}
```

## iOS Implementation

### Swift HTTP Client Example

```swift
import Foundation

class TruLedgrAPI {
    private let baseURL = "https://api.truledgr.app"
    private var authToken: String?
    
    func login(email: String, password: String) async throws -> TokenResponse {
        let url = URL(string: "\(baseURL)/auth/login")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = ["email": email, "password": password]
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        let response = try JSONDecoder().decode(TokenResponse.self, from: data)
        
        // Store token securely in Keychain
        storeToken(response.access_token)
        
        return response
    }
    
    func getCurrentUser() async throws -> User {
        guard let token = getStoredToken() else {
            throw APIError.notAuthenticated
        }
        
        let url = URL(string: "\(baseURL)/users/me")!
        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(User.self, from: data)
    }
    
    // Keychain helpers
    private func storeToken(_ token: String) {
        // Implementation using Keychain Services
    }
    
    private func getStoredToken() -> String? {
        // Implementation using Keychain Services
    }
}

struct TokenResponse: Codable {
    let access_token: String
    let token_type: String
}

struct User: Codable {
    let id: Int
    let email: String
    let full_name: String?
    let is_active: Bool
}
```

### Biometric Authentication
Enable biometric authentication using Face ID/Touch ID:

```swift
import LocalAuthentication

func authenticateWithBiometrics() async -> Bool {
    let context = LAContext()
    var error: NSError?
    
    guard context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) else {
        return false
    }
    
    do {
        let result = try await context.evaluatePolicy(
            .deviceOwnerAuthenticationWithBiometrics,
            localizedReason: "Authenticate to access TruLedgr"
        )
        return result
    } catch {
        return false
    }
}
```

## Android Implementation

### Kotlin HTTP Client Example

```kotlin
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import com.google.gson.Gson
import java.io.IOException

class TruLedgrAPI {
    private val baseUrl = "https://api.truledgr.app"
    private val client = OkHttpClient()
    private val gson = Gson()
    private val jsonMediaType = "application/json".toMediaType()
    
    suspend fun login(email: String, password: String): TokenResponse = withContext(Dispatchers.IO) {
        val loginData = LoginRequest(email, password)
        val json = gson.toJson(loginData)
        val body = json.toRequestBody(jsonMediaType)
        
        val request = Request.Builder()
            .url("$baseUrl/auth/login")
            .post(body)
            .build()
        
        val response = client.newCall(request).execute()
        val responseBody = response.body?.string()
        
        if (response.isSuccessful && responseBody != null) {
            val tokenResponse = gson.fromJson(responseBody, TokenResponse::class.java)
            // Store token securely
            storeToken(tokenResponse.access_token)
            tokenResponse
        } else {
            throw IOException("Login failed")
        }
    }
    
    suspend fun getCurrentUser(): User = withContext(Dispatchers.IO) {
        val token = getStoredToken() ?: throw IllegalStateException("Not authenticated")
        
        val request = Request.Builder()
            .url("$baseUrl/users/me")
            .header("Authorization", "Bearer $token")
            .build()
        
        val response = client.newCall(request).execute()
        val responseBody = response.body?.string()
        
        if (response.isSuccessful && responseBody != null) {
            gson.fromJson(responseBody, User::class.java)
        } else {
            throw IOException("Failed to get user")
        }
    }
    
    private fun storeToken(token: String) {
        // Use EncryptedSharedPreferences for secure storage
    }
    
    private fun getStoredToken(): String? {
        // Retrieve from EncryptedSharedPreferences
        return null
    }
}

data class LoginRequest(val email: String, val password: String)
data class TokenResponse(val access_token: String, val token_type: String)
data class User(val id: Int, val email: String, val full_name: String?, val is_active: Boolean)
```

### Biometric Authentication
Enable biometric authentication using BiometricPrompt:

```kotlin
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.core.content.ContextCompat
import androidx.fragment.app.FragmentActivity

class BiometricAuthenticator(private val activity: FragmentActivity) {
    
    fun authenticateWithBiometrics(
        onSuccess: () -> Unit,
        onError: (String) -> Unit
    ) {
        val biometricManager = BiometricManager.from(activity)
        
        when (biometricManager.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_WEAK)) {
            BiometricManager.BIOMETRIC_SUCCESS -> {
                showBiometricPrompt(onSuccess, onError)
            }
            BiometricManager.BIOMETRIC_ERROR_NO_HARDWARE -> {
                onError("Biometric hardware not available")
            }
            BiometricManager.BIOMETRIC_ERROR_HW_UNAVAILABLE -> {
                onError("Biometric hardware unavailable")
            }
            BiometricManager.BIOMETRIC_ERROR_NONE_ENROLLED -> {
                onError("No biometric credentials enrolled")
            }
        }
    }
    
    private fun showBiometricPrompt(onSuccess: () -> Unit, onError: (String) -> Unit) {
        val executor = ContextCompat.getMainExecutor(activity)
        val biometricPrompt = BiometricPrompt(activity, executor, object : BiometricPrompt.AuthenticationCallback() {
            override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                super.onAuthenticationSucceeded(result)
                onSuccess()
            }
            
            override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                super.onAuthenticationError(errorCode, errString)
                onError(errString.toString())
            }
        })
        
        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle("Authenticate with TruLedgr")
            .setSubtitle("Use your biometric credential to authenticate")
            .setNegativeButtonText("Cancel")
            .build()
        
        biometricPrompt.authenticate(promptInfo)
    }
}
```

## Push Notifications

### iOS Push Notifications
1. Configure APNs in Apple Developer Console
2. Implement push notification handling in your app
3. Send device token to backend for registration

### Android Push Notifications
1. Configure Firebase Cloud Messaging (FCM)
2. Implement FCM in your Android app
3. Send FCM token to backend for registration

## Error Handling

### Common HTTP Status Codes
- `200`: Success
- `400`: Bad Request - Invalid input data
- `401`: Unauthorized - Invalid or missing authentication token
- `403`: Forbidden - Access denied
- `404`: Not Found - Resource doesn't exist
- `422`: Unprocessable Entity - Validation errors
- `500`: Internal Server Error

### Example Error Response
```json
{
  "detail": "Could not validate credentials"
}
```

## Best Practices

1. **Secure Token Storage**: Always use secure storage mechanisms (Keychain on iOS, EncryptedSharedPreferences on Android)
2. **Token Refresh**: Implement automatic token refresh when tokens expire
3. **Network Error Handling**: Implement retry logic for network failures
4. **Offline Support**: Cache critical data locally for offline access
5. **Biometric Authentication**: Implement biometric authentication for enhanced security
6. **Certificate Pinning**: Implement SSL certificate pinning for additional security

## Testing

### Mock API for Development
For development and testing, you can run a local version of the API:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Then point your mobile app to `http://localhost:8000` (or your computer's IP address on the same network).

## Troubleshooting

### Common Issues
1. **CORS Errors**: Ensure your mobile app's requests include proper headers
2. **Token Expiration**: Implement automatic token refresh
3. **Network Timeouts**: Implement appropriate timeout handling
4. **SSL Certificate Issues**: Ensure proper SSL configuration for production

For additional support, refer to the main project documentation or contact the development team.
