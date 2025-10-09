package technology.mcguire.truledgr

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import technology.mcguire.truledgr.ui.theme.TruLedgrTheme
import java.net.HttpURLConnection
import java.net.URL

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            TruLedgrTheme {
                Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                    BonjourScreen(
                        modifier = Modifier.padding(innerPadding),
                        onCheckApi = { checkApiHealth(it) }
                    )
                }
            }
        }
    }

    private fun checkApiHealth(onResult: (ApiStatus) -> Unit) {
        lifecycleScope.launch {
            val status = withContext(Dispatchers.IO) {
                // Try hostname first, then fallback to IP if DNS fails
                val endpoints = listOf(
                    "https://api.truledgr.app/health",
                    "https://162.159.140.98/health"  // Cloudflare IP fallback
                )
                
                var lastError = ""
                for ((index, endpoint) in endpoints.withIndex()) {
                    try {
                        android.util.Log.d("TruLedgr", "Trying endpoint ${index + 1}/${endpoints.size}: $endpoint")
                        val url = URL(endpoint)
                        val connection = url.openConnection() as HttpURLConnection
                        
                        // Add Host header for IP-based requests
                        if (endpoint.contains("162.159.140.98")) {
                            connection.setRequestProperty("Host", "api.truledgr.app")
                        }
                        
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
                            lastError = "HTTP $responseCode: $message"
                            android.util.Log.w("TruLedgr", "HTTP error: $lastError")
                        }
                    } catch (e: java.net.UnknownHostException) {
                        lastError = "DNS lookup failed: ${e.message}"
                        android.util.Log.e("TruLedgr", "❌ DNS error on $endpoint: ${e.message}", e)
                        // Continue to next endpoint if DNS fails
                        continue
                    } catch (e: javax.net.ssl.SSLHandshakeException) {
                        lastError = "SSL certificate verification failed. This is common in Android emulators. The API may be working but the emulator can't verify the certificate."
                        android.util.Log.e("TruLedgr", "❌ SSL handshake error on $endpoint: ${e.message}", e)
                        android.util.Log.e("TruLedgr", "💡 SSL Error Details: ${e.cause?.message}")
                        android.util.Log.e("TruLedgr", "ℹ️  This typically happens in Android emulators. Try on a physical device or use HTTP for local testing.")
                        // Continue to next endpoint
                        continue
                    } catch (e: java.security.cert.CertificateException) {
                        lastError = "Certificate error: ${e.message}"
                        android.util.Log.e("TruLedgr", "❌ Certificate error on $endpoint: ${e.message}", e)
                        // Continue to next endpoint
                        continue
                    } catch (e: Exception) {
                        lastError = "${e.javaClass.simpleName}: ${e.message}"
                        android.util.Log.e("TruLedgr", "❌ Error on $endpoint: ${e.message}", e)
                        android.util.Log.e("TruLedgr", "Error type: ${e.javaClass.name}")
                        e.cause?.let { cause ->
                            android.util.Log.e("TruLedgr", "Caused by: ${cause.javaClass.simpleName}: ${cause.message}")
                        }
                        // Continue to next endpoint
                        continue
                    }
                }
                
                // All endpoints failed
                ApiStatus.Down(lastError.ifEmpty { "All endpoints failed" })
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
    onCheckApi: ((ApiStatus) -> Unit) -> Unit = {}
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
            text = "API endpoint: https://api.truledgr.app/health",
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