<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// API Configuration
const getStoredApiUrl = (): string | null => {
  return localStorage.getItem('customApiUrl')
}

const setStoredApiUrl = (url: string | null) => {
  if (url) {
    localStorage.setItem('customApiUrl', url)
  } else {
    localStorage.removeItem('customApiUrl')
  }
}

const DEFAULT_API_URL = 'https://api.truledgr.app'
const customApiUrl = ref<string | null>(getStoredApiUrl())
const currentApiUrl = computed(() => customApiUrl.value || DEFAULT_API_URL)
const displayUrl = computed(() => 
  currentApiUrl.value.replace('https://', '').replace('http://', '')
)

const showApiDialog = ref(false)
const apiUrlInput = ref('')

// Health check state
type HealthStatus = 'healthy' | 'degraded' | 'unhealthy' | 'checking' | 'unknown'
const healthStatus = ref<HealthStatus>('unknown')
const healthCheckInterval = ref<number | null>(null)
const debounceTimeout = ref<number | null>(null)

// Version
const appVersion = '0.1.0'

// Form state - Identifier-first flow
const step = ref<'identifier' | 'password'>('identifier')
const email = ref('')
const password = ref('')
const showPassword = ref(false)
const error = ref('')
const loading = ref(false)

const handleIdentifierSubmit = async () => {
  error.value = ''
  
  if (!email.value.trim()) {
    error.value = 'Please enter your email address'
    return
  }
  
  // Basic email validation
  if (!email.value.includes('@')) {
    error.value = 'Please enter a valid email address'
    return
  }
  
  loading.value = true
  
  try {
    // Check if user exists in the system
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 5000)
    
    const response = await fetch(`${currentApiUrl.value}/auth/check-email`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email: email.value }),
      signal: controller.signal
    })
    
    clearTimeout(timeoutId)
    
    if (response.ok) {
      const data = await response.json()
      
      if (data.exists) {
        // User exists - proceed to login options
        // TODO: Use data.auth_methods to show only available providers
        step.value = 'password'
      } else {
        // User doesn't exist - JIT signup flow
        // Redirect to signup page with email pre-filled
        router.push({
          name: 'signup',
          query: { email: email.value }
        })
      }
    } else {
      // API error - default to login flow
      console.error('Email check failed, defaulting to login flow')
      step.value = 'password'
    }
  } catch (err) {
    // Network error or timeout - default to login flow
    console.error('Email check error:', err)
    step.value = 'password'
  } finally {
    loading.value = false
  }
}

const handlePasswordSubmit = async () => {
  error.value = ''
  loading.value = true
  
  try {
    // TODO: Implement actual login logic with currentApiUrl
    console.log('Login:', { email: email.value, password: password.value, api: currentApiUrl.value })
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Redirect to dashboard on success
    router.push('/')
  } catch (err) {
    error.value = 'Invalid email or password'
  } finally {
    loading.value = false
  }
}

const goBackToIdentifier = () => {
  step.value = 'identifier'
  password.value = ''
  error.value = ''
}

const handleGoogleLogin = () => {
  console.log('Google OAuth login')
  // TODO: Implement Google OAuth
}

const handleAppleLogin = () => {
  console.log('Apple OAuth login')
  // TODO: Implement Apple Sign In
}

const handleMicrosoftLogin = () => {
  console.log('Microsoft OAuth login')
  // TODO: Implement Microsoft OAuth
}

const handlePasskeyLogin = () => {
  console.log('Passkey/WebAuthn login')
  // TODO: Implement WebAuthn/Passkey authentication
}

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}

const checkHealth = async () => {
  healthStatus.value = 'checking'
  try {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 5000) // 5 second timeout
    
    const response = await fetch(`${currentApiUrl.value}/health`, {
      signal: controller.signal
    })
    
    clearTimeout(timeoutId)
    
    if (response.ok) {
      const data = await response.json()
      // Check if response indicates degraded service
      if (data.status === 'healthy' || response.status === 200) {
        healthStatus.value = 'healthy'
      } else if (data.status === 'degraded') {
        healthStatus.value = 'degraded'
      } else {
        healthStatus.value = 'unhealthy'
      }
    } else {
      healthStatus.value = 'unhealthy'
    }
  } catch (err) {
    healthStatus.value = 'unhealthy'
  }
}

const startHealthCheck = () => {
  // Clear existing interval
  if (healthCheckInterval.value) {
    clearInterval(healthCheckInterval.value)
  }
  
  // Initial check
  checkHealth()
  
  // Check every 30 seconds
  healthCheckInterval.value = window.setInterval(() => {
    checkHealth()
  }, 30000)
}

const stopHealthCheck = () => {
  if (healthCheckInterval.value) {
    clearInterval(healthCheckInterval.value)
    healthCheckInterval.value = null
  }
}

// Start health check when component mounts
import { onMounted, onUnmounted } from 'vue'

onMounted(() => {
  startHealthCheck()
})

onUnmounted(() => {
  stopHealthCheck()
  
  // Clear debounce timeout
  if (debounceTimeout.value) {
    clearTimeout(debounceTimeout.value)
  }
})

const openApiDialog = () => {
  showApiDialog.value = true
  apiUrlInput.value = customApiUrl.value || ''
}

const closeApiDialog = () => {
  showApiDialog.value = false
  apiUrlInput.value = ''
}

const onApiUrlInput = () => {
  // Clear existing timeout
  if (debounceTimeout.value) {
    clearTimeout(debounceTimeout.value)
  }
  
  // Set new timeout to check health after 500ms pause
  debounceTimeout.value = window.setTimeout(() => {
    checkHealthForUrl(apiUrlInput.value)
  }, 500)
}

const checkHealthForUrl = async (urlToCheck: string) => {
  healthStatus.value = 'checking'
  
  let url = urlToCheck.trim()
  
  // If empty, use default
  if (!url) {
    url = DEFAULT_API_URL
  }
  
  // Add https:// if no protocol specified
  if (url && !url.startsWith('http://') && !url.startsWith('https://')) {
    url = `https://${url}`
  }
  
  try {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 5000)
    
    const response = await fetch(`${url}/health`, {
      signal: controller.signal
    })
    
    clearTimeout(timeoutId)
    
    if (response.ok) {
      const data = await response.json()
      healthStatus.value = data.status === 'healthy' ? 'healthy' : 
                           data.status === 'degraded' ? 'degraded' : 'unhealthy'
    } else {
      healthStatus.value = 'unhealthy'
    }
  } catch (err) {
    healthStatus.value = 'unhealthy'
  }
}

const saveApiUrl = () => {
  let newUrl = apiUrlInput.value.trim()
  
  // Add https:// if no protocol specified
  if (newUrl && !newUrl.startsWith('http://') && !newUrl.startsWith('https://')) {
    newUrl = `https://${newUrl}`
  }
  
  // Save to localStorage
  setStoredApiUrl(newUrl || null)
  customApiUrl.value = newUrl || null
  
  // Restart health check with new URL
  startHealthCheck()
  
  closeApiDialog()
}
</script>

<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <div class="logo">🎩</div>
        <h1>Log in to TruLedgr</h1>
      </div>

      <div class="auth-form">
        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <!-- Step 1: Identifier (Email) -->
        <form v-if="step === 'identifier'" @submit.prevent="handleIdentifierSubmit">
          <div class="form-group">
            <label for="email">Email</label>
            <input
              id="email"
              v-model="email"
              type="email"
              required
              autocomplete="email"
              :disabled="loading"
              autofocus
              placeholder="name@example.com"
            />
          </div>

          <button type="submit" class="btn-primary" :disabled="loading || !email.trim()">
            <span v-if="!loading">Next</span>
            <span v-else>Checking...</span>
          </button>

          <div class="info-text-section">
            <p class="info-text">
              <svg class="info-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 16v-4M12 8h.01"/>
              </svg>
              New to TruLedgr?<br />We'll create your account automatically.
            </p>
          </div>
        </form>

        <!-- Step 2: Login Options (After Email Entered) -->
        <div v-if="step === 'password'" class="password-step">
          <div class="user-identifier">
            <span class="user-email">{{ email }}</span>
            <button type="button" class="change-email-btn" @click="goBackToIdentifier">
              Change
            </button>
          </div>

          <!-- OAuth Buttons (Cloudflare-style: full width, prominent) -->
          <div class="oauth-buttons-primary">
            <button type="button" class="btn-oauth-primary" @click="handleGoogleLogin" :disabled="loading">
              <svg class="oauth-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              Google
            </button>

            <button type="button" class="btn-oauth-primary" @click="handleAppleLogin" :disabled="loading">
              <svg class="oauth-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" fill="currentColor">
                <path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.53 4.09l-.01-.01zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/>
              </svg>
              Apple
            </button>

            <button type="button" class="btn-oauth-primary" @click="handleMicrosoftLogin" :disabled="loading">
              <svg class="oauth-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path fill="#f25022" d="M1 1h10v10H1z"/>
                <path fill="#00a4ef" d="M13 1h10v10H13z"/>
                <path fill="#7fba00" d="M1 13h10v10H1z"/>
                <path fill="#ffb900" d="M13 13h10v10H13z"/>
              </svg>
              Microsoft
            </button>
          </div>

          <div class="auth-divider">
            <span>OR</span>
          </div>

          <!-- Password Form -->
          <form @submit.prevent="handlePasswordSubmit">
            <div class="form-group">
              <label for="password">
                Password
                <button 
                  type="button" 
                  class="show-password-btn" 
                  @click="showPassword = !showPassword"
                  :disabled="loading"
                >
                  {{ showPassword ? 'Hide' : 'Show' }}
                </button>
              </label>
              <input
                id="password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                required
                autocomplete="current-password"
                :disabled="loading"
                autofocus
                placeholder="Enter your password"
              />
            </div>

            <div class="forgot-links">
              <router-link to="/forgot-password" class="text-link">Forgot your password?</router-link>
            </div>

            <div class="form-footer">
              <p class="terms-text">
                By continuing, you acknowledge that you understand and agree to our 
                <a href="#" class="text-link">terms</a>, 
                <a href="#" class="text-link">privacy policy</a>, and 
                <a href="#" class="text-link">cookie policy</a>.
              </p>
            </div>

            <button type="submit" class="btn-login" :disabled="loading">
              <span v-if="!loading">Log in</span>
              <span v-else>Logging in...</span>
            </button>
          </form>
        </div>

        <!-- API Settings and Version -->
        <div class="footer-section">
          <button class="api-button" @click="openApiDialog">
            <span 
              class="status-indicator" 
              :class="`status-${healthStatus}`"
              :title="healthStatus === 'healthy' ? 'API is healthy' : 
                     healthStatus === 'degraded' ? 'API is degraded' : 
                     healthStatus === 'unhealthy' ? 'API is unhealthy' :
                     healthStatus === 'checking' ? 'Checking API status...' :
                     'API status unknown'"
            ></span>
            <span>{{ displayUrl }}</span>
          </button>
          
          <p class="version">v{{ appVersion }}</p>
        </div>
      </div>
    </div>

    <!-- API Configuration Dialog -->
    <div v-if="showApiDialog" class="dialog-overlay" @click="closeApiDialog">
      <div class="dialog-content" @click.stop>
        <div class="dialog-header">
          <h2>API Configuration</h2>
          <button class="dialog-close" @click="closeApiDialog">×</button>
        </div>
        
        <div class="dialog-body">
          <p class="dialog-info">
            <strong>Default:</strong> {{ DEFAULT_API_URL }}
          </p>
          <p class="dialog-info">
            <strong>Current:</strong> {{ displayUrl }}
          </p>
          
          <div class="input-group">
            <label for="apiUrl">Custom API URL</label>
            <input
              id="apiUrl"
              v-model="apiUrlInput"
              type="text"
              placeholder="https://api.example.com"
              class="input-field"
              @input="onApiUrlInput"
            />
            <p class="input-hint">Leave empty to reset to default</p>
            
            <div v-if="healthStatus !== 'unknown'" class="health-status-message">
              <span 
                class="status-indicator-inline" 
                :class="`status-${healthStatus}`"
              ></span>
              <span v-if="healthStatus === 'healthy'" class="status-text status-healthy-text">
                API is healthy
              </span>
              <span v-else-if="healthStatus === 'degraded'" class="status-text status-degraded-text">
                API is degraded
              </span>
              <span v-else-if="healthStatus === 'unhealthy'" class="status-text status-unhealthy-text">
                API is not responding
              </span>
              <span v-else-if="healthStatus === 'checking'" class="status-text">
                Checking...
              </span>
            </div>
          </div>
        </div>
        
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closeApiDialog">Cancel</button>
          <button class="btn-save" @click="saveApiUrl">Save</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
  background-color: #f5f5f5;
}

@media (prefers-color-scheme: dark) {
  .auth-container {
    background-color: #121212;
  }
}

.auth-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 480px;
  padding: 3rem 2.5rem;
}

@media (prefers-color-scheme: dark) {
  .auth-card {
    background-color: #1a1a1a;
  }
}

.auth-header {
  text-align: center;
  margin-bottom: 2rem;
}

.logo {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.auth-header h1 {
  font-size: 1.75rem;
  font-weight: 600;
  margin: 0;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.error-message {
  padding: 0.75rem 1rem;
  background-color: #fee;
  color: #c00;
  border-radius: 4px;
  font-size: 0.875rem;
  border: 1px solid #fcc;
}

@media (prefers-color-scheme: dark) {
  .error-message {
    background-color: #300;
    color: #fcc;
    border-color: #600;
  }
}

/* OAuth Buttons (Cloudflare-style) */
.oauth-buttons-primary {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.btn-oauth-primary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  font-weight: 500;
  background-color: white;
  color: #000;
  border: 1px solid #d0d0d0;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-oauth-primary:hover:not(:disabled) {
  background-color: #f9f9f9;
  border-color: #b0b0b0;
}

.btn-oauth-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (prefers-color-scheme: dark) {
  .btn-oauth-primary {
    background-color: #2a2a2a;
    color: #fff;
    border-color: #444;
  }
  
  .btn-oauth-primary:hover:not(:disabled) {
    background-color: #333;
    border-color: #555;
  }
}

.oauth-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

/* Divider */
.auth-divider {
  text-align: center;
  position: relative;
  margin: 1rem 0;
}

.auth-divider::before,
.auth-divider::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 45%;
  height: 1px;
  background-color: #d0d0d0;
}

@media (prefers-color-scheme: dark) {
  .auth-divider::before,
  .auth-divider::after {
    background-color: #444;
  }
}

.auth-divider::before {
  left: 0;
}

.auth-divider::after {
  right: 0;
}

.auth-divider span {
  background-color: white;
  padding: 0 0.75rem;
  font-size: 0.875rem;
  color: #666;
  font-weight: 500;
}

@media (prefers-color-scheme: dark) {
  .auth-divider span {
    background-color: #1a1a1a;
    color: #999;
  }
}

/* Email/Password Form */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
  font-size: 0.9375rem;
  color: #333;
}

@media (prefers-color-scheme: dark) {
  .form-group label {
    color: #ddd;
  }
}

.show-password-btn {
  background: none;
  border: none;
  color: #1a73e8;
  font-size: 0.875rem;
  cursor: pointer;
  padding: 0;
  font-weight: 500;
}

.show-password-btn:hover:not(:disabled) {
  text-decoration: underline;
}

.show-password-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (prefers-color-scheme: dark) {
  .show-password-btn {
    color: #4a90e2;
  }
}

.form-group input {
  padding: 0.75rem;
  border: 1px solid #d0d0d0;
  border-radius: 4px;
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #1a73e8;
}

.form-group input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background-color: #f5f5f5;
}

@media (prefers-color-scheme: dark) {
  .form-group input {
    background-color: #2a2a2a;
    border-color: #444;
    color: white;
  }
  
  .form-group input:focus {
    border-color: #4a90e2;
  }
  
  .form-group input:disabled {
    background-color: #1a1a1a;
  }
}

.form-footer {
  margin: 0.5rem 0;
}

.terms-text {
  font-size: 0.8125rem;
  color: #666;
  line-height: 1.4;
  margin: 0;
}

@media (prefers-color-scheme: dark) {
  .terms-text {
    color: #999;
  }
}

.text-link {
  color: #1a73e8;
  text-decoration: none;
}

.text-link:hover {
  text-decoration: underline;
}

@media (prefers-color-scheme: dark) {
  .text-link {
    color: #4a90e2;
  }
}

/* Primary Button (Next) */
.btn-primary {
  width: 100%;
  padding: 0.75rem;
  font-size: 1rem;
  font-weight: 600;
  background-color: #5865f2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-top: 1rem;
}

.btn-primary:hover:not(:disabled) {
  background-color: #4752c4;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Login Button */
.btn-login {
  width: 100%;
  padding: 0.75rem;
  font-size: 1rem;
  font-weight: 600;
  background-color: #5865f2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-top: 1rem;
}

.btn-login:hover:not(:disabled) {
  background-color: #4752c4;
}

.btn-login:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* User Identifier Display */
.user-identifier {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  margin-bottom: 1.5rem;
  background-color: #f5f5f5;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

@media (prefers-color-scheme: dark) {
  .user-identifier {
    background-color: #2a2a2a;
    border-color: #444;
  }
}

.user-email {
  font-size: 0.9375rem;
  font-weight: 500;
  color: #333;
  word-break: break-all;
}

@media (prefers-color-scheme: dark) {
  .user-email {
    color: #e0e0e0;
  }
}

.change-email-btn {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #1a73e8;
  background-color: transparent;
  border: 1px solid #1a73e8;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
  margin-left: 1rem;
}

.change-email-btn:hover {
  background-color: #e8f0fe;
}

@media (prefers-color-scheme: dark) {
  .change-email-btn {
    color: #4a90e2;
    border-color: #4a90e2;
  }
  
  .change-email-btn:hover {
    background-color: #1a2332;
  }
}

/* Password Step Container */
.password-step {
  display: flex;
  flex-direction: column;
}

/* Info Text Section */
.info-text-section {
  margin-top: 1.5rem;
  text-align: center;
}

.info-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #666;
  padding: 0.75rem;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.info-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
  color: #1a73e8;
}

@media (prefers-color-scheme: dark) {
  .info-text {
    color: #999;
    background-color: #2a2a2a;
  }
  
  .info-icon {
    color: #4a90e2;
  }
}

/* Forgot Password/Email Links */
.forgot-links {
  display: flex;
  justify-content: flex-start;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.75rem;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
}

.forgot-links .text-link {
  font-weight: 500;
}

/* Sign Up Button */
.btn-signup {
  display: block;
  width: 100%;
  padding: 0.75rem;
  font-size: 1rem;
  font-weight: 600;
  background-color: transparent;
  color: #1a73e8;
  border: 2px solid #1a73e8;
  border-radius: 4px;
  cursor: pointer;
  text-align: center;
  text-decoration: none;
  transition: all 0.2s;
}

.btn-signup:hover {
  background-color: rgba(26, 115, 232, 0.05);
}

@media (prefers-color-scheme: dark) {
  .btn-signup {
    color: #4a90e2;
    border-color: #4a90e2;
  }
  
  .btn-signup:hover {
    background-color: rgba(74, 144, 226, 0.1);
  }
}

/* API Settings Footer */
.footer-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
}

@media (prefers-color-scheme: dark) {
  .footer-section {
    border-top-color: #333;
  }
}

.api-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: transparent;
  border: none;
  color: #666;
  font-size: 0.75rem;
  cursor: pointer;
  transition: color 0.2s;
  border-radius: 4px;
}

.api-button:hover {
  color: #333;
  background-color: rgba(0, 0, 0, 0.05);
}

@media (prefers-color-scheme: dark) {
  .api-button {
    color: #999;
  }
  
  .api-button:hover {
    color: #ccc;
    background-color: rgba(255, 255, 255, 0.05);
  }
}

/* Status Indicator */
.status-indicator {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-indicator.status-healthy {
  background-color: #10b981;
  box-shadow: 0 0 4px rgba(16, 185, 129, 0.5);
}

.status-indicator.status-degraded {
  background-color: #f59e0b;
  box-shadow: 0 0 4px rgba(245, 158, 11, 0.5);
}

.status-indicator.status-unhealthy {
  background-color: #ef4444;
  box-shadow: 0 0 4px rgba(239, 68, 68, 0.5);
}

.status-indicator.status-checking {
  background-color: #6b7280;
  animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.status-indicator.status-unknown {
  background-color: #9ca3af;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.version {
  font-size: 0.75rem;
  color: #666;
  margin: 0;
}

@media (prefers-color-scheme: dark) {
  .version {
    color: #999;
  }
}

/* Dialog Styles */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.dialog-content {
  background-color: white;
  border-radius: 8px;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

@media (prefers-color-scheme: dark) {
  .dialog-content {
    background-color: #2a2a2a;
  }
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
}

@media (prefers-color-scheme: dark) {
  .dialog-header {
    border-bottom-color: #444;
  }
}

.dialog-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
}

.dialog-close {
  background: none;
  border: none;
  font-size: 2rem;
  line-height: 1;
  color: #666;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
}

.dialog-close:hover {
  color: #333;
}

@media (prefers-color-scheme: dark) {
  .dialog-close {
    color: #999;
  }
  
  .dialog-close:hover {
    color: #ccc;
  }
}

.dialog-body {
  padding: 1.5rem;
}

.dialog-info {
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
  color: #666;
}

@media (prefers-color-scheme: dark) {
  .dialog-info {
    color: #999;
  }
}

.input-group {
  margin-top: 1.5rem;
}

.input-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.input-field {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d0d0d0;
  border-radius: 4px;
  font-size: 1rem;
  font-family: inherit;
  background-color: white;
  color: inherit;
  box-sizing: border-box;
}

.input-field:focus {
  outline: none;
  border-color: #1a73e8;
}

@media (prefers-color-scheme: dark) {
  .input-field {
    background-color: #1a1a1a;
    border-color: #444;
  }
  
  .input-field:focus {
    border-color: #4a90e2;
  }
}

.input-hint {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: #666;
}

@media (prefers-color-scheme: dark) {
  .input-hint {
    color: #999;
  }
}

.health-status-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.75rem;
  padding: 0.5rem;
  border-radius: 4px;
  background-color: #f9fafb;
}

@media (prefers-color-scheme: dark) {
  .health-status-message {
    background-color: #1f2937;
  }
}

.status-indicator-inline {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-indicator-inline.status-healthy {
  background-color: #10b981;
}

.status-indicator-inline.status-degraded {
  background-color: #f59e0b;
}

.status-indicator-inline.status-unhealthy {
  background-color: #ef4444;
}

.status-indicator-inline.status-checking {
  background-color: #6b7280;
  animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.status-text {
  font-size: 0.875rem;
  font-weight: 500;
}

.status-healthy-text {
  color: #059669;
}

.status-degraded-text {
  color: #d97706;
}

.status-unhealthy-text {
  color: #dc2626;
}

@media (prefers-color-scheme: dark) {
  .status-healthy-text {
    color: #34d399;
  }
  
  .status-degraded-text {
    color: #fbbf24;
  }
  
  .status-unhealthy-text {
    color: #f87171;
  }
}

.dialog-footer {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  padding: 1.5rem;
  border-top: 1px solid #e0e0e0;
}

@media (prefers-color-scheme: dark) {
  .dialog-footer {
    border-top-color: #444;
  }
}

.btn-cancel,
.btn-save {
  padding: 0.625rem 1.5rem;
  border-radius: 4px;
  font-size: 0.9375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background-color: transparent;
  border: 1px solid #d0d0d0;
  color: inherit;
}

.btn-cancel:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

@media (prefers-color-scheme: dark) {
  .btn-cancel {
    border-color: #444;
  }
  
  .btn-cancel:hover {
    background-color: rgba(255, 255, 255, 0.05);
  }
}

.btn-save {
  background-color: #5865f2;
  border: none;
  color: white;
}

.btn-save:hover {
  background-color: #4752c4;
}

@media (max-width: 640px) {
  .auth-card {
    padding: 2rem 1.5rem;
  }
  
  .forgot-links {
    flex-direction: column;
    align-items: center;
  }
}
</style>
