package technology.mcguire.truledgr.auth

import android.content.Context
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.outlined.Visibility
import androidx.compose.material.icons.outlined.VisibilityOff
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.fragment.app.FragmentActivity
import androidx.lifecycle.viewmodel.compose.viewModel
import technology.mcguire.truledgr.BuildConfig
import technology.mcguire.truledgr.MainActivity

@Composable
fun IdentifierFirstLoginScreen(
    modifier: Modifier = Modifier,
    viewModel: AuthViewModel = viewModel()
) {
    val context = LocalContext.current
    val activity = context as? FragmentActivity
    var showApiDialog by remember { mutableStateOf(false) }
    var apiUrlInput by remember { mutableStateOf("") }
    var currentApiUrl by remember { mutableStateOf(MainActivity.getApiUrl(context)) }
    
    val displayUrl = currentApiUrl.removePrefix("https://").removePrefix("http://")
    
    LaunchedEffect(Unit) {
        viewModel.checkBiometricAvailability(context)
        viewModel.checkHealth(context)
    }
    
    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
    ) {
        Column(
            modifier = Modifier
                .weight(1f)
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(24.dp)
        ) {
            Spacer(modifier = Modifier.height(40.dp))
            
            // Logo and title
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                Text(
                    text = "🎩",
                    style = MaterialTheme.typography.displayLarge
                )
                
                Text(
                    text = "Log in to TruLedgr",
                    style = MaterialTheme.typography.headlineMedium,
                    color = MaterialTheme.colorScheme.primary
                )
            }
            
            // Error message
            viewModel.error?.let { error ->
                Surface(
                    color = MaterialTheme.colorScheme.errorContainer,
                    shape = MaterialTheme.shapes.medium
                ) {
                    Text(
                        text = error,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onErrorContainer,
                        modifier = Modifier.padding(12.dp)
                    )
                }
            }
            
            // Step 1: Email identifier
            when (viewModel.step) {
                is AuthStep.Identifier -> {
                    IdentifierStep(viewModel, context)
                }
                is AuthStep.Password -> {
                    PasswordStep(viewModel, activity)
                }
            }
        }
        
        // Footer
        Footer(
            displayUrl = displayUrl,
            healthStatus = viewModel.healthStatus,
            onApiClick = { 
                apiUrlInput = MainActivity.getApiUrl(context) ?: ""
                showApiDialog = true 
            }
        )
    }
    
    // Debounced health check for API URL input
    LaunchedEffect(apiUrlInput) {
        if (apiUrlInput.isNotEmpty()) {
            kotlinx.coroutines.delay(500) // 500ms debounce
            var checkUrl = apiUrlInput.trim()
            if (!checkUrl.startsWith("http://") && !checkUrl.startsWith("https://")) {
                checkUrl = "https://$checkUrl"
            }
            val status = viewModel.checkHealthForUrl(checkUrl)
            viewModel.healthStatus = status
        }
    }
    
    // API Configuration Dialog
    if (showApiDialog) {
        ApiConfigurationDialog(
            currentUrl = displayUrl,
            healthStatus = viewModel.healthStatus,
            apiUrlInput = apiUrlInput,
            onApiUrlChange = { apiUrlInput = it },
            onDismiss = {
                showApiDialog = false
                apiUrlInput = ""
            },
            onSave = {
                var newUrl = apiUrlInput.trim()
                
                if (newUrl.isNotEmpty() &&
                    !newUrl.startsWith("http://") &&
                    !newUrl.startsWith("https://")
                ) {
                    newUrl = "https://$newUrl"
                }
                
                MainActivity.setApiUrl(
                    context,
                    if (newUrl.isEmpty()) null else newUrl
                )
                
                // Restart health check with new URL
                viewModel.checkHealth(context)
                
                currentApiUrl = MainActivity.getApiUrl(context)
                showApiDialog = false
                apiUrlInput = ""
            }
        )
    }
}

@Composable
private fun IdentifierStep(viewModel: AuthViewModel, context: Context) {
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        OutlinedTextField(
            value = viewModel.email,
            onValueChange = { viewModel.email = it },
            label = { Text("Email") },
            placeholder = { Text("name@example.com") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            keyboardOptions = KeyboardOptions(
                keyboardType = KeyboardType.Email,
                imeAction = ImeAction.Next
            ),
            keyboardActions = KeyboardActions(
                onNext = { viewModel.handleIdentifierSubmit(context) }
            ),
            enabled = !viewModel.loading
        )
        
        Button(
            onClick = { viewModel.handleIdentifierSubmit(context) },
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp),
            enabled = viewModel.email.trim().isNotEmpty() && !viewModel.loading
        ) {
            if (viewModel.loading) {
                CircularProgressIndicator(
                    modifier = Modifier.size(24.dp),
                    color = MaterialTheme.colorScheme.onPrimary
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text("Checking...")
            } else {
                Text("Next", style = MaterialTheme.typography.titleMedium)
            }
        }
        
        // Info message about JIT signup
        Surface(
            color = MaterialTheme.colorScheme.secondaryContainer.copy(alpha = 0.5f),
            shape = MaterialTheme.shapes.medium
        ) {
            Row(
                modifier = Modifier.padding(12.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = Icons.Default.Info,
                    contentDescription = null,
                    modifier = Modifier.size(16.dp),
                    tint = MaterialTheme.colorScheme.onSecondaryContainer
                )
                Text(
                    text = "New to TruLedgr? We'll create your account automatically.",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSecondaryContainer
                )
            }
        }
    }
}

@Composable
private fun PasswordStep(viewModel: AuthViewModel, activity: FragmentActivity?) {
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(20.dp)
    ) {
        // User identifier display
        Surface(
            color = MaterialTheme.colorScheme.secondaryContainer.copy(alpha = 0.5f),
            shape = MaterialTheme.shapes.medium
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = viewModel.email,
                    style = MaterialTheme.typography.bodyMedium,
                    modifier = Modifier.weight(1f)
                )
                
                TextButton(onClick = { viewModel.goBackToIdentifier() }) {
                    Text("Change")
                }
            }
        }
        
        // Biometric authentication (if available)
        if (viewModel.biometricAvailable && activity != null) {
            Button(
                onClick = {
                    viewModel.handleBiometricAuth(
                        activity = activity,
                        onSuccess = {
                            // TODO: Navigate to main app
                        },
                        onError = { error ->
                            viewModel.error = error
                        }
                    )
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp)
            ) {
                Text("Sign in with ${viewModel.biometricType.displayName()}")
            }
        }
        
        // OAuth buttons
        Column(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            OAuthButton(
                text = "Google",
                onClick = { viewModel.handleGoogleLogin() },
                enabled = !viewModel.loading
            )
            OAuthButton(
                text = "Apple",
                onClick = { viewModel.handleAppleLogin() },
                enabled = !viewModel.loading
            )
            OAuthButton(
                text = "Microsoft",
                onClick = { viewModel.handleMicrosoftLogin() },
                enabled = !viewModel.loading
            )
        }
        
        // OR divider
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            HorizontalDivider(modifier = Modifier.weight(1f))
            Text(
                text = "OR",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            HorizontalDivider(modifier = Modifier.weight(1f))
        }
        
        // Password form
        Column(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            OutlinedTextField(
                value = viewModel.password,
                onValueChange = { viewModel.password = it },
                label = { Text("Password") },
                placeholder = { Text("Enter your password") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                visualTransformation = if (viewModel.showPassword) {
                    VisualTransformation.None
                } else {
                    PasswordVisualTransformation()
                },
                trailingIcon = {
                    IconButton(onClick = { viewModel.showPassword = !viewModel.showPassword }) {
                        Icon(
                            imageVector = if (viewModel.showPassword) {
                                Icons.Outlined.VisibilityOff
                            } else {
                                Icons.Outlined.Visibility
                            },
                            contentDescription = if (viewModel.showPassword) "Hide password" else "Show password"
                        )
                    }
                },
                keyboardOptions = KeyboardOptions(
                    keyboardType = KeyboardType.Password,
                    imeAction = ImeAction.Go
                ),
                keyboardActions = KeyboardActions(
                    onGo = { viewModel.handlePasswordSubmit() }
                ),
                enabled = !viewModel.loading
            )
            
            TextButton(onClick = { /* TODO: Password reset */ }) {
                Text("Forgot your password?")
            }
            
            // Terms text
            Text(
                text = "By continuing, you acknowledge that you understand and agree to our terms, privacy policy, and cookie policy.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            
            Button(
                onClick = { viewModel.handlePasswordSubmit() },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp),
                enabled = !viewModel.loading
            ) {
                if (viewModel.loading) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(24.dp),
                        color = MaterialTheme.colorScheme.onPrimary
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Logging in...")
                } else {
                    Text("Log in", style = MaterialTheme.typography.titleMedium)
                }
            }
        }
    }
}

@Composable
private fun OAuthButton(
    text: String,
    onClick: () -> Unit,
    enabled: Boolean
) {
    OutlinedButton(
        onClick = onClick,
        modifier = Modifier
            .fillMaxWidth()
            .height(56.dp),
        enabled = enabled
    ) {
        Text(text, style = MaterialTheme.typography.titleMedium)
    }
}

@Composable
private fun Footer(
    displayUrl: String,
    healthStatus: HealthStatus,
    onApiClick: () -> Unit
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 24.dp, vertical = 16.dp)
    ) {
        HorizontalDivider(modifier = Modifier.padding(vertical = 16.dp))
        
        Row(
            modifier = Modifier
                .clickable(onClick = onApiClick)
                .padding(vertical = 4.dp, horizontal = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.Center
        ) {
            // Health status dot
            Box(
                modifier = Modifier
                    .size(8.dp)
                    .background(
                        color = when (healthStatus) {
                            is HealthStatus.Healthy -> androidx.compose.ui.graphics.Color.Green
                            is HealthStatus.Degraded -> androidx.compose.ui.graphics.Color.Yellow
                            is HealthStatus.Unhealthy -> androidx.compose.ui.graphics.Color.Red
                            is HealthStatus.Checking -> androidx.compose.ui.graphics.Color.Gray
                            is HealthStatus.Unknown -> androidx.compose.ui.graphics.Color.Gray
                        },
                        shape = androidx.compose.foundation.shape.CircleShape
                    )
            )
            
            Spacer(modifier = Modifier.width(8.dp))
            
            Text(
                text = displayUrl,
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
        
        Text(
            text = "v${BuildConfig.VERSION_NAME}",
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.padding(vertical = 4.dp)
        )
    }
}

@Composable
private fun ApiConfigurationDialog(
    currentUrl: String,
    healthStatus: HealthStatus,
    apiUrlInput: String,
    onApiUrlChange: (String) -> Unit,
    onDismiss: () -> Unit,
    onSave: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("API Configuration") },
        text = {
            Column {
                Text(
                    text = "Default: ${MainActivity.DEFAULT_API_URL}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.padding(bottom = 8.dp)
                )
                
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(bottom = 16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Current Status:",
                        style = MaterialTheme.typography.bodyMedium
                    )
                    
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(6.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Box(
                            modifier = Modifier
                                .size(10.dp)
                                .background(
                                    color = when (healthStatus) {
                                        is HealthStatus.Healthy -> androidx.compose.ui.graphics.Color.Green
                                        is HealthStatus.Degraded -> androidx.compose.ui.graphics.Color.Yellow
                                        is HealthStatus.Unhealthy -> androidx.compose.ui.graphics.Color.Red
                                        is HealthStatus.Checking -> androidx.compose.ui.graphics.Color.Gray
                                        is HealthStatus.Unknown -> androidx.compose.ui.graphics.Color.Gray
                                    },
                                    shape = androidx.compose.foundation.shape.CircleShape
                                )
                        )
                        
                        Text(
                            text = healthStatus.displayText(),
                            style = MaterialTheme.typography.bodyMedium,
                            color = when (healthStatus) {
                                is HealthStatus.Healthy -> androidx.compose.ui.graphics.Color.Green
                                is HealthStatus.Degraded -> androidx.compose.ui.graphics.Color(0xFFCCAA00)
                                is HealthStatus.Unhealthy -> androidx.compose.ui.graphics.Color.Red
                                is HealthStatus.Checking -> MaterialTheme.colorScheme.onSurfaceVariant
                                is HealthStatus.Unknown -> MaterialTheme.colorScheme.onSurfaceVariant
                            }
                        )
                    }
                }
                
                OutlinedTextField(
                    value = apiUrlInput,
                    onValueChange = onApiUrlChange,
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
            TextButton(onClick = onSave) {
                Text("Save")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancel")
            }
        }
    )
}
