package technology.mcguire.truledgr

import android.content.Context
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.fragment.app.FragmentActivity
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.viewmodel.compose.viewModel
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import technology.mcguire.truledgr.auth.AuthViewModel
import technology.mcguire.truledgr.auth.IdentifierFirstLoginScreen
import technology.mcguire.truledgr.ui.theme.TruLedgrTheme
import java.net.HttpURLConnection
import java.net.URL

class MainActivity : FragmentActivity() {
    companion object {
        private const val PREFS_NAME = "truledgr_prefs"
        private const val KEY_API_URL = "api_url"
        const val DEFAULT_API_URL = "https://api.truledgr.app"
        
        fun getApiUrl(context: Context): String {
            val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            return prefs.getString(KEY_API_URL, DEFAULT_API_URL) ?: DEFAULT_API_URL
        }
        
        fun setApiUrl(context: Context, url: String?) {
            val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            prefs.edit().apply {
                if (url.isNullOrBlank()) {
                    remove(KEY_API_URL)
                } else {
                    putString(KEY_API_URL, url)
                }
                apply()
            }
        }
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        
        setContent {
            TruLedgrTheme {
                val viewModel: AuthViewModel = viewModel()
                
                Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                    IdentifierFirstLoginScreen(
                        viewModel = viewModel,
                        modifier = Modifier.padding(innerPadding)
                    )
                }
            }
        }
    }

    private fun checkApiHealth(onResult: (ApiStatus) -> Unit) {
        lifecycleScope.launch {
            val status = withContext(Dispatchers.IO) {
                val apiBaseUrl = getApiUrl(this@MainActivity)
                val endpoint = "$apiBaseUrl/health"
                
                try {
                        android.util.Log.d("TruLedgr", "Checking API health: $endpoint")
                        val url = URL(endpoint)
                        val connection = url.openConnection() as HttpURLConnection
                        
                        connection.requestMethod = "GET"
                        connection.connectTimeout = 5000
                        connection.readTimeout = 5000
                        connection.setRequestProperty("Accept", "application/json")
                        
                        val responseCode = connection.responseCode
                        android.util.Log.d("TruLedgr", "Response code: $responseCode")
                        
                        val message = if (responseCode == 200) {
                            connection.inputStream.bufferedReader().use { it.readText() }
                        } else {
                            connection.errorStream?.bufferedReader()?.use { it.readText() } ?: ""
                        }
                        connection.disconnect()
                        
                        if (responseCode == 200) {
                            android.util.Log.d("TruLedgr", "✅ Success: $message")
                            return@withContext ApiStatus.Up(message)
                        } else {
                            val errorMsg = "HTTP $responseCode: $message"
                            android.util.Log.w("TruLedgr", "HTTP error: $errorMsg")
                            return@withContext ApiStatus.Down(errorMsg)
                        }
                } catch (e: java.net.UnknownHostException) {
                    val errorMsg = "DNS lookup failed: ${e.message}"
                    android.util.Log.e("TruLedgr", "❌ DNS error on $endpoint: ${e.message}", e)
                    return@withContext ApiStatus.Down(errorMsg)
                } catch (e: javax.net.ssl.SSLHandshakeException) {
                    val errorMsg = "SSL certificate verification failed. This is common in Android emulators. The API may be working but the emulator can't verify the certificate."
                    android.util.Log.e("TruLedgr", "❌ SSL handshake error on $endpoint: ${e.message}", e)
                    android.util.Log.e("TruLedgr", "💡 SSL Error Details: ${e.cause?.message}")
                    android.util.Log.e("TruLedgr", "ℹ️  This typically happens in Android emulators. Try on a physical device or use HTTP for local testing.")
                    return@withContext ApiStatus.Down(errorMsg)
                } catch (e: java.security.cert.CertificateException) {
                    val errorMsg = "Certificate error: ${e.message}"
                    android.util.Log.e("TruLedgr", "❌ Certificate error on $endpoint: ${e.message}", e)
                    return@withContext ApiStatus.Down(errorMsg)
                } catch (e: Exception) {
                    val errorMsg = "${e.javaClass.simpleName}: ${e.message}"
                    android.util.Log.e("TruLedgr", "❌ Error on $endpoint: ${e.message}", e)
                    android.util.Log.e("TruLedgr", "Error type: ${e.javaClass.name}")
                    e.cause?.let { cause ->
                        android.util.Log.e("TruLedgr", "Caused by: ${cause.javaClass.simpleName}: ${cause.message}")
                    }
                    return@withContext ApiStatus.Down(errorMsg)
                }
            }
            onResult(status)
        }
    }
}

sealed class ApiStatus {
    data class Up(val message: String) : ApiStatus()
    data class Down(val error: String) : ApiStatus()
    object Checking : ApiStatus()
    object NotChecked : ApiStatus()
}

@Composable
fun BonjourScreen(
    modifier: Modifier = Modifier,
    onCheckApi: ((ApiStatus) -> Unit) -> Unit = {},
    apiMode: String = "Production"
) {
    var apiStatus by remember { mutableStateOf<ApiStatus>(ApiStatus.NotChecked) }

    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "🎩 Bonjour!",
            style = MaterialTheme.typography.displayLarge,
            textAlign = TextAlign.Center
        )
        
        Spacer(modifier = Modifier.height(8.dp))
        
        // API Mode indicator
        Surface(
            color = if (apiMode == "Local Development") 
                MaterialTheme.colorScheme.secondaryContainer 
            else 
                MaterialTheme.colorScheme.primaryContainer,
            shape = MaterialTheme.shapes.small
        ) {
            Text(
                text = "API: $apiMode",
                style = MaterialTheme.typography.labelSmall,
                modifier = Modifier.padding(horizontal = 12.dp, vertical = 4.dp),
                color = if (apiMode == "Local Development")
                    MaterialTheme.colorScheme.onSecondaryContainer
                else
                    MaterialTheme.colorScheme.onPrimaryContainer
            )
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Text(
            text = "TruLedgr Android",
            style = MaterialTheme.typography.headlineSmall,
            color = MaterialTheme.colorScheme.secondary
        )
        
        Spacer(modifier = Modifier.height(48.dp))
        
        when (val status = apiStatus) {
            is ApiStatus.NotChecked -> {
                Text(
                    text = "API Status: Not checked",
                    style = MaterialTheme.typography.bodyLarge
                )
            }
            is ApiStatus.Checking -> {
                CircularProgressIndicator()
                Spacer(modifier = Modifier.height(8.dp))
                Text(text = "Checking API...")
            }
            is ApiStatus.Up -> {
                Text(
                    text = "✅ API is UP",
                    style = MaterialTheme.typography.titleLarge,
                    color = MaterialTheme.colorScheme.primary
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = status.message,
                    style = MaterialTheme.typography.bodyMedium,
                    textAlign = TextAlign.Center
                )
            }
            is ApiStatus.Down -> {
                Text(
                    text = "❌ API is DOWN",
                    style = MaterialTheme.typography.titleLarge,
                    color = MaterialTheme.colorScheme.error
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = status.error,
                    style = MaterialTheme.typography.bodyMedium,
                    textAlign = TextAlign.Center
                )
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        Button(
            onClick = {
                apiStatus = ApiStatus.Checking
                onCheckApi { status ->
                    apiStatus = status
                }
            },
            enabled = apiStatus !is ApiStatus.Checking
        ) {
            Text("Check API Status")
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Text(
            text = if (apiMode == "Local Development") {
                "API endpoint: http://10.0.2.2:8000/health\n(Android emulator localhost)"
            } else {
                "API endpoint: https://api.truledgr.app/health"
            },
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            textAlign = TextAlign.Center
        )
    }
}

@Preview(showBackground = true)
@Composable
fun BonjourScreenPreview() {
    TruLedgrTheme {
        BonjourScreen()
    }
}

@Composable
fun LoginScreen(
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    var showApiDialog by remember { mutableStateOf(false) }
    var apiUrlInput by remember { mutableStateOf("") }
    var currentApiUrl by remember { mutableStateOf(MainActivity.getApiUrl(context)) }
    
    // Display URL without the protocol
    val displayUrl = currentApiUrl.removePrefix("https://").removePrefix("http://")
    
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.SpaceBetween
    ) {
        // Top section with logo and title
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.Center
        ) {
            Text(
                text = "🎩",
                style = MaterialTheme.typography.displayLarge
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Text(
                text = "TruLedgr",
                style = MaterialTheme.typography.displayMedium,
                color = MaterialTheme.colorScheme.primary
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = "Personal Finance Management",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
        
        // Middle section with login buttons
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier.fillMaxWidth()
        ) {
            // Sign Up button (primary)
            Button(
                onClick = { /* TODO: Navigate to signup */ },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp)
            ) {
                Text(
                    text = "Sign Up",
                    style = MaterialTheme.typography.titleMedium
                )
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Login button (secondary)
            OutlinedButton(
                onClick = { /* TODO: Navigate to login */ },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp)
            ) {
                Text(
                    text = "Log In",
                    style = MaterialTheme.typography.titleMedium
                )
            }
            
            Spacer(modifier = Modifier.height(32.dp))
            
            // OAuth buttons
            Text(
                text = "Or continue with",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                // Google OAuth
                OutlinedButton(
                    onClick = { /* TODO: Google OAuth */ },
                    modifier = Modifier.weight(1f)
                ) {
                    Text("Google")
                }
                
                Spacer(modifier = Modifier.width(8.dp))
                
                // Apple OAuth
                OutlinedButton(
                    onClick = { /* TODO: Apple OAuth */ },
                    modifier = Modifier.weight(1f)
                ) {
                    Text("Apple")
                }
                
                Spacer(modifier = Modifier.width(8.dp))
                
                // Microsoft OAuth
                OutlinedButton(
                    onClick = { /* TODO: Microsoft OAuth */ },
                    modifier = Modifier.weight(1f)
                ) {
                    Text("Microsoft")
                }
            }
        }
        
        // Bottom section with API settings
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier.fillMaxWidth()
        ) {
            HorizontalDivider(modifier = Modifier.padding(vertical = 16.dp))
            
            // Inconspicuous API URL button
            Row(
                modifier = Modifier
                    .clickable { showApiDialog = true }
                    .padding(vertical = 4.dp, horizontal = 8.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.Center
            ) {
                Icon(
                    imageVector = Icons.Default.Settings,
                    contentDescription = "API Settings",
                    modifier = Modifier.size(16.dp),
                    tint = MaterialTheme.colorScheme.onSurfaceVariant
                )
                
                Spacer(modifier = Modifier.width(4.dp))
                
                Text(
                    text = displayUrl,
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            // Version number (separate, non-clickable)
            Text(
                text = "v${BuildConfig.VERSION_NAME}",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(vertical = 4.dp)
            )
        }
    }
    
    // API URL Configuration Dialog
    if (showApiDialog) {
        AlertDialog(
            onDismissRequest = { showApiDialog = false },
            title = { Text("API Configuration") },
            text = {
                Column {
                    Text(
                        text = "Default: ${MainActivity.DEFAULT_API_URL}",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.padding(bottom = 8.dp)
                    )
                    
                    Text(
                        text = "Current: $displayUrl",
                        style = MaterialTheme.typography.bodyMedium,
                        modifier = Modifier.padding(bottom = 16.dp)
                    )
                    
                    OutlinedTextField(
                        value = apiUrlInput,
                        onValueChange = { apiUrlInput = it },
                        label = { Text("Custom API URL") },
                        placeholder = { Text("https://api.example.com") },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true
                    )
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    Text(
                        text = "Leave empty to reset to default",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        var newUrl = apiUrlInput.trim()
                        
                        // Add https:// if no protocol specified
                        if (newUrl.isNotEmpty() && 
                            !newUrl.startsWith("http://") && 
                            !newUrl.startsWith("https://")) {
                            newUrl = "https://$newUrl"
                        }
                        
                        // Save to SharedPreferences
                        MainActivity.setApiUrl(
                            context, 
                            if (newUrl.isEmpty()) null else newUrl
                        )
                        
                        // Update the displayed URL
                        currentApiUrl = MainActivity.getApiUrl(context)
                        
                        showApiDialog = false
                        apiUrlInput = ""
                    }
                ) {
                    Text("Save")
                }
            },
            dismissButton = {
                TextButton(onClick = { 
                    showApiDialog = false
                    apiUrlInput = ""
                }) {
                    Text("Cancel")
                }
            }
        )
    }
}

@Preview(showBackground = true)
@Composable
fun LoginScreenPreview() {
    TruLedgrTheme {
        LoginScreen()
    }
}