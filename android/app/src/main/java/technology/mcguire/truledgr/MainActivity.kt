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
                try {
                    val url = URL("https://api.truledgr.app/health")
                    val connection = url.openConnection() as HttpURLConnection
                    connection.requestMethod = "GET"
                    connection.connectTimeout = 3000
                    connection.readTimeout = 3000
                    
                    val responseCode = connection.responseCode
                    val message = if (responseCode == 200) {
                        connection.inputStream.bufferedReader().use { it.readText() }
                    } else {
                        ""
                    }
                    connection.disconnect()
                    
                    if (responseCode == 200) {
                        ApiStatus.Up(message)
                    } else {
                        ApiStatus.Down("HTTP $responseCode")
                    }
                } catch (e: Exception) {
                    ApiStatus.Down(e.message ?: "Connection failed")
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