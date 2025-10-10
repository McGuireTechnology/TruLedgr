package technology.mcguire.truledgr.auth

import android.content.Context
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.core.content.ContextCompat
import androidx.fragment.app.FragmentActivity
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import technology.mcguire.truledgr.MainActivity
import java.net.HttpURLConnection
import java.net.URL

sealed class AuthStep {
    object Identifier : AuthStep()
    object Password : AuthStep()
}

sealed class BiometricType {
    object None : BiometricType()
    object Fingerprint : BiometricType()
    object Face : BiometricType()
    object Iris : BiometricType()
    
    fun displayName(): String = when (this) {
        is None -> "Biometric"
        is Fingerprint -> "Fingerprint"
        is Face -> "Face"
        is Iris -> "Iris"
    }
}

sealed class HealthStatus {
    object Healthy : HealthStatus()
    object Degraded : HealthStatus()
    object Unhealthy : HealthStatus()
    object Checking : HealthStatus()
    object Unknown : HealthStatus()
    
    fun displayText(): String = when (this) {
        is Healthy -> "Healthy"
        is Degraded -> "Degraded"
        is Unhealthy -> "Unhealthy"
        is Checking -> "Checking..."
        is Unknown -> "Unknown"
    }
}

class AuthViewModel : ViewModel() {
    var step by mutableStateOf<AuthStep>(AuthStep.Identifier)
    var email by mutableStateOf("")
    var password by mutableStateOf("")
    var showPassword by mutableStateOf(false)
    var error by mutableStateOf<String?>(null)
    var loading by mutableStateOf(false)
    var biometricAvailable by mutableStateOf(false)
    var biometricType by mutableStateOf<BiometricType>(BiometricType.None)
    var healthStatus by mutableStateOf<HealthStatus>(HealthStatus.Unknown)
    
    fun checkHealth(context: Context) {
        viewModelScope.launch {
            healthStatus = HealthStatus.Checking
            val apiUrl = MainActivity.getApiUrl(context)
            val status = performHealthCheck(apiUrl)
            healthStatus = status
        }
    }
    
    suspend fun checkHealthForUrl(url: String): HealthStatus {
        return performHealthCheck(url)
    }
    
    private suspend fun performHealthCheck(baseUrl: String): HealthStatus = withContext(Dispatchers.IO) {
        try {
            val url = URL("$baseUrl/health")
            val connection = url.openConnection() as HttpURLConnection
            
            connection.requestMethod = "GET"
            connection.connectTimeout = 5000
            connection.readTimeout = 5000
            connection.setRequestProperty("Accept", "application/json")
            
            val responseCode = connection.responseCode
            
            if (responseCode == 200) {
                val response = connection.inputStream.bufferedReader().use { it.readText() }
                connection.disconnect()
                
                try {
                    val json = JSONObject(response)
                    val status = json.optString("status", "unknown").lowercase()
                    return@withContext when (status) {
                        "healthy" -> HealthStatus.Healthy
                        "degraded" -> HealthStatus.Degraded
                        else -> HealthStatus.Unhealthy
                    }
                } catch (e: Exception) {
                    // If JSON parsing fails but we got 200, assume healthy
                    return@withContext HealthStatus.Healthy
                }
            } else {
                connection.disconnect()
                return@withContext HealthStatus.Unhealthy
            }
        } catch (e: Exception) {
            android.util.Log.e("AuthViewModel", "Health check failed", e)
            return@withContext HealthStatus.Unhealthy
        }
    }
    
    fun checkBiometricAvailability(context: Context) {
        val biometricManager = BiometricManager.from(context)
        
        when (biometricManager.canAuthenticate(
            BiometricManager.Authenticators.BIOMETRIC_STRONG or
            BiometricManager.Authenticators.BIOMETRIC_WEAK
        )) {
            BiometricManager.BIOMETRIC_SUCCESS -> {
                biometricAvailable = true
                // Determine type based on device capabilities
                biometricType = when {
                    // Android doesn't provide specific type info, default to fingerprint
                    else -> BiometricType.Fingerprint
                }
            }
            else -> {
                biometricAvailable = false
                biometricType = BiometricType.None
            }
        }
    }
    
    fun handleIdentifierSubmit(context: Context) {
        error = null
        
        if (email.trim().isEmpty()) {
            error = "Please enter your email address"
            return
        }
        
        if (!email.contains("@")) {
            error = "Please enter a valid email address"
            return
        }
        
        loading = true
        
        viewModelScope.launch {
            try {
                val exists = checkEmailExists(context, email)
                
                if (exists) {
                    // User exists - proceed to login options
                    step = AuthStep.Password
                } else {
                    // JIT signup - user doesn't exist
                    android.util.Log.d("TruLedgr", "JIT Signup: Redirect to signup with email: $email")
                    // TODO: Navigate to signup screen
                    // For now, proceed to password step
                    step = AuthStep.Password
                }
            } catch (e: Exception) {
                android.util.Log.e("TruLedgr", "Email check failed: ${e.message}", e)
                // On error, default to login flow
                step = AuthStep.Password
            } finally {
                loading = false
            }
        }
    }
    
    fun handlePasswordSubmit() {
        error = null
        
        if (password.isEmpty()) {
            error = "Please enter your password"
            return
        }
        
        loading = true
        
        viewModelScope.launch {
            try {
                // TODO: Implement actual login API call
                kotlinx.coroutines.delay(1000)
                android.util.Log.d("TruLedgr", "Login successful for: $email")
                // Navigate to main app
            } catch (e: Exception) {
                error = "Invalid email or password"
            } finally {
                loading = false
            }
        }
    }
    
    fun handleBiometricAuth(
        activity: FragmentActivity,
        onSuccess: () -> Unit,
        onError: (String) -> Unit
    ) {
        val executor = ContextCompat.getMainExecutor(activity)
        val biometricPrompt = BiometricPrompt(
            activity,
            executor,
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                    super.onAuthenticationSucceeded(result)
                    android.util.Log.d("TruLedgr", "Biometric authentication successful")
                    onSuccess()
                }
                
                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    super.onAuthenticationError(errorCode, errString)
                    onError(errString.toString())
                }
                
                override fun onAuthenticationFailed() {
                    super.onAuthenticationFailed()
                    onError("Biometric authentication failed")
                }
            }
        )
        
        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle("Log in to TruLedgr")
            .setSubtitle("Authenticate using your ${biometricType.displayName().lowercase()}")
            .setNegativeButtonText("Use password")
            .build()
        
        biometricPrompt.authenticate(promptInfo)
    }
    
    fun handleGoogleLogin() {
        android.util.Log.d("TruLedgr", "Google OAuth login")
        // TODO: Implement Google OAuth
    }
    
    fun handleAppleLogin() {
        android.util.Log.d("TruLedgr", "Apple OAuth login")
        // TODO: Implement Apple OAuth (if available on Android)
    }
    
    fun handleMicrosoftLogin() {
        android.util.Log.d("TruLedgr", "Microsoft OAuth login")
        // TODO: Implement Microsoft OAuth
    }
    
    fun goBackToIdentifier() {
        step = AuthStep.Identifier
        password = ""
        error = null
    }
    
    // MARK: - API Methods
    
    private suspend fun checkEmailExists(context: Context, email: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val apiUrl = MainActivity.getApiUrl(context)
                val url = URL("$apiUrl/auth/check-email")
                val connection = url.openConnection() as HttpURLConnection
                
                connection.requestMethod = "POST"
                connection.setRequestProperty("Content-Type", "application/json")
                connection.connectTimeout = 5000
                connection.readTimeout = 5000
                connection.doOutput = true
                
                val jsonBody = JSONObject().apply {
                    put("email", email)
                }
                
                connection.outputStream.use { os ->
                    os.write(jsonBody.toString().toByteArray())
                }
                
                val responseCode = connection.responseCode
                
                if (responseCode == 200) {
                    val response = connection.inputStream.bufferedReader().use { it.readText() }
                    val jsonResponse = JSONObject(response)
                    jsonResponse.getBoolean("exists")
                } else {
                    throw Exception("HTTP $responseCode")
                }
            } catch (e: Exception) {
                android.util.Log.e("TruLedgr", "Failed to check email: ${e.message}", e)
                throw e
            }
        }
    }
}
