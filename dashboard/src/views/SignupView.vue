<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

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

// Version
const appVersion = '0.1.0'

// Health check state
type HealthStatus = 'healthy' | 'degraded' | 'unhealthy' | 'checking' | 'unknown'
const healthStatus = ref<HealthStatus>('unknown')
const healthCheckInterval = ref<number | null>(null)
const debounceTimeout = ref<number | null>(null)

// Form state
const name = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const agreeToTerms = ref(false)
const error = ref('')
const loading = ref(false)

const handleSubmit = async () => {
  error.value = ''
  
  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }
  
  if (!agreeToTerms.value) {
    error.value = 'You must agree to the Terms of Service and Privacy Policy'
    return
  }
  
  loading.value = true
  
  try {
    // TODO: Implement actual signup logic
    console.log('Signup:', { name: name.value, email: email.value, password: password.value })
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Redirect to dashboard on success
    router.push('/')
  } catch (err) {
    error.value = 'Failed to create account. Please try again.'
  } finally {
    loading.value = false
  }
}

const handleGoogleSignup = () => {
  console.log('Google signup clicked')
  // TODO: Implement Google OAuth
}

const handleAppleSignup = () => {
  console.log('Apple signup clicked')
  // TODO: Implement Apple OAuth
}

const handleMicrosoftSignup = () => {
  console.log('Microsoft signup clicked')
  // TODO: Implement Microsoft OAuth
}

const openApiDialog = () => {
  showApiDialog.value = true
  apiUrlInput.value = customApiUrl.value || ''
}

const closeApiDialog = () => {
  showApiDialog.value = false
  apiUrlInput.value = ''
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
  
  closeApiDialog()
  
  // Restart health check with new URL
  stopHealthCheck()
  startHealthCheck()
}

// Health check functions
const checkHealth = async () => {
  healthStatus.value = 'checking'
  
  try {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 5000)
    
    const response = await fetch(`${currentApiUrl.value}/health`, {
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

const startHealthCheck = () => {
  if (healthCheckInterval.value) {
    clearInterval(healthCheckInterval.value)
  }
  
  checkHealth()
  healthCheckInterval.value = window.setInterval(() => {
    checkHealth()
  }, 30000) // Check every 30 seconds
}

const stopHealthCheck = () => {
  if (healthCheckInterval.value) {
    clearInterval(healthCheckInterval.value)
    healthCheckInterval.value = null
  }
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

// Lifecycle hooks
onMounted(() => {
  startHealthCheck()
  
  // Pre-fill email from query parameter (JIT signup)
  const queryEmail = route.query.email as string
  if (queryEmail) {
    email.value = queryEmail
  }
})

onUnmounted(() => {
  stopHealthCheck()
  
  // Clear debounce timeout
  if (debounceTimeout.value) {
    clearTimeout(debounceTimeout.value)
  }
})
</script>

<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <div class="logo">🎩</div>
        <h1>Create Account</h1>
        <p v-if="route.query.email">Looks like you're new here! Let's create your account.</p>
        <p v-else>Join TruLedgr to manage your finances</p>
      </div>

      <form @submit.prevent="handleSubmit" class="auth-form">
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        
        <div v-if="route.query.email" class="info-message">
          Creating account for <strong>{{ route.query.email }}</strong>
        </div>

        <div class="form-group">
          <label for="name">Full Name</label>
          <input
            id="name"
            v-model="name"
            type="text"
            required
            placeholder="John Doe"
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label for="email">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            required
            placeholder="you@example.com"
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            required
            placeholder="••••••••"
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label for="confirmPassword">Confirm Password</label>
          <input
            id="confirmPassword"
            v-model="confirmPassword"
            type="password"
            required
            placeholder="••••••••"
            :disabled="loading"
          />
        </div>

        <div class="form-options">
          <label class="checkbox-label">
            <input type="checkbox" v-model="agreeToTerms" :disabled="loading" required />
            <span>I agree to the <a href="#" class="text-link">Terms</a> and <a href="#" class="text-link">Privacy Policy</a></span>
          </label>
        </div>

        <button type="submit" class="btn-primary" :disabled="loading">
          <span v-if="!loading">Sign Up</span>
          <span v-else>Creating account...</span>
        </button>

        <div class="auth-divider">
          <span>Or continue with</span>
        </div>

                <!-- OAuth Buttons (Cloudflare-style: full width first) -->
        <div class="oauth-buttons-primary">
          <button type="button" class="btn-oauth-primary" @click="handleGoogleSignup" :disabled="loading">
            <svg class="oauth-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
            </svg>
            Continue with Google
          </button>

          <button type="button" class="btn-oauth-primary" @click="handleAppleSignup" :disabled="loading">
            <svg class="oauth-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" fill="currentColor">
              <path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.53 4.09l-.01-.01zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/>
            </svg>
            Continue with Apple
          </button>

          <button type="button" class="btn-oauth-primary" @click="handleMicrosoftSignup" :disabled="loading">
            <svg class="oauth-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path fill="#f25022" d="M1 1h10v10H1z"/>
              <path fill="#00a4ef" d="M13 1h10v10H13z"/>
              <path fill="#7fba00" d="M1 13h10v10H1z"/>
              <path fill="#ffb900" d="M13 13h10v10H13z"/>
            </svg>
            Continue with Microsoft
          </button>
        </div>

        <div class="auth-divider">
          <span>OR</span>
        </div>
      </form>

      <router-link to="/login" class="btn-login-link">
        Log in
      </router-link>

      <!-- API Settings and Version -->
      <div class="footer-section">
        <button class="api-button" @click="openApiDialog">
          <span 
            class="status-indicator" 
            :class="`status-${healthStatus}`"
            :title="healthStatus === 'healthy' ? 'API is healthy' : 
                    healthStatus === 'degraded' ? 'API is degraded' : 
                    healthStatus === 'unhealthy' ? 'Cannot reach API' : 
                    healthStatus === 'checking' ? 'Checking API health...' : 
                    'API health unknown'"
          ></span>
          <span>{{ displayUrl }}</span>
        </button>
        
        <p class="version">v{{ appVersion }}</p>
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
                Cannot reach API
              </span>
              <span v-else-if="healthStatus === 'checking'" class="status-text">
                Checking API health...
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
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 450px;
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
  font-size: 3rem;
  margin-bottom: 1rem;
}

.auth-header h1 {
  font-size: 1.75rem;
  margin-bottom: 0.5rem;
}

.auth-header p {
  color: #666;
  font-size: 0.9375rem;
}

@media (prefers-color-scheme: dark) {
  .auth-header p {
    color: #999;
  }
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.error-message {
  padding: 0.75rem;
  background-color: #fee;
  color: #c00;
  border-radius: 8px;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

@media (prefers-color-scheme: dark) {
  .error-message {
    background-color: #300;
    color: #fcc;
  }
}

.info-message {
  padding: 0.75rem;
  background-color: #e8f4fd;
  color: #0c5fa8;
  border-radius: 8px;
  font-size: 0.875rem;
  margin-bottom: 1rem;
  border-left: 3px solid #1a73e8;
}

@media (prefers-color-scheme: dark) {
  .info-message {
    background-color: #1a2a3a;
    color: #4a90e2;
    border-left-color: #4a90e2;
  }
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 500;
  font-size: 0.9375rem;
}

.form-group input {
  padding: 0.875rem;
  border: 1px solid #ddd;
  border-radius: 8px;
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
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-label input {
  cursor: pointer;
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

.btn-primary {
  width: 100%;
  padding: 1rem;
  font-size: 1rem;
  font-weight: 600;
  background-color: #1a73e8;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background-color: #1557b0;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

/* Log In Button */
.btn-login-link {
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

.btn-login-link:hover {
  background-color: rgba(26, 115, 232, 0.05);
}

@media (prefers-color-scheme: dark) {
  .btn-login-link {
    color: #4a90e2;
    border-color: #4a90e2;
  }
  
  .btn-login-link:hover {
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
</style>
