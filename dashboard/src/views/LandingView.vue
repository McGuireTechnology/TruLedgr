<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const showApiDialog = ref(false)
const apiUrlInput = ref('')

// Get API URL from localStorage or use default
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

// Get version from package.json or environment
const appVersion = '0.1.0'

const handleSignUp = () => {
  router.push('/signup')
}

const handleLogin = () => {
  router.push('/login')
}

const handleGoogleOAuth = () => {
  // TODO: Google OAuth
  console.log('Google OAuth clicked')
}

const handleAppleOAuth = () => {
  // TODO: Apple OAuth
  console.log('Apple OAuth clicked')
}

const handleMicrosoftOAuth = () => {
  // TODO: Microsoft OAuth
  console.log('Microsoft OAuth clicked')
}

const openApiDialog = () => {
  showApiDialog.value = true
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
}
</script>

<template>
  <div class="landing-container">
    <div class="landing-content">
      <!-- Top section with logo and title -->
      <div class="logo-section">
        <div class="logo">🎩</div>
        <h1 class="title">TruLedgr</h1>
        <p class="subtitle">Personal Finance Management</p>
      </div>

      <!-- Middle section with login buttons -->
      <div class="action-buttons">
        <button class="btn-primary" @click="handleSignUp">
          Sign Up
        </button>
        
        <button class="btn-secondary" @click="handleLogin">
          Log In
        </button>

        <div class="oauth-section">
          <p class="oauth-label">Or continue with</p>
          
          <div class="oauth-buttons">
            <button class="btn-oauth" @click="handleGoogleOAuth">
              Google
            </button>
            <button class="btn-oauth" @click="handleAppleOAuth">
              Apple
            </button>
            <button class="btn-oauth" @click="handleMicrosoftOAuth">
              Microsoft
            </button>
          </div>
        </div>
      </div>

      <!-- Bottom section with API settings and version -->
      <div class="footer-section">
        <div class="divider"></div>
        
        <button class="api-button" @click="openApiDialog">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
          </svg>
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
            />
            <p class="input-hint">Leave empty to reset to default</p>
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

<style scoped src="./LoginView.vue"></style>

<style scoped>
.landing-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  width: 100%;
  padding: 2rem;
}

.landing-content {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  width: 100%;
  max-width: 400px;
  min-height: 600px;
  padding: 2rem;
}

.logo-section {
  text-align: center;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.logo {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.title {
  font-size: 2.75rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #666;
  font-size: 1rem;
}

@media (prefers-color-scheme: dark) {
  .subtitle {
    color: #999;
  }
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.btn-primary {
  width: 100%;
  padding: 1rem;
  font-size: 1.125rem;
  font-weight: 600;
  background-color: #1a73e8;
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary:hover {
  background-color: #1557b0;
}

.btn-secondary {
  width: 100%;
  padding: 1rem;
  font-size: 1.125rem;
  font-weight: 600;
  background-color: transparent;
  color: #1a73e8;
  border: 2px solid #1a73e8;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background-color: rgba(26, 115, 232, 0.05);
}

@media (prefers-color-scheme: dark) {
  .btn-secondary {
    color: #4a90e2;
    border-color: #4a90e2;
  }
  
  .btn-secondary:hover {
    background-color: rgba(74, 144, 226, 0.1);
  }
}

.oauth-section {
  margin-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.oauth-label {
  text-align: center;
  font-size: 0.875rem;
  color: #666;
}

@media (prefers-color-scheme: dark) {
  .oauth-label {
    color: #999;
  }
}

.oauth-buttons {
  display: flex;
  gap: 0.75rem;
}

.btn-oauth {
  flex: 1;
  padding: 0.75rem;
  font-size: 0.9375rem;
  background-color: transparent;
  color: inherit;
  border: 1px solid #ddd;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-oauth:hover {
  background-color: rgba(0, 0, 0, 0.05);
  border-color: #999;
}

@media (prefers-color-scheme: dark) {
  .btn-oauth {
    border-color: #444;
  }
  
  .btn-oauth:hover {
    background-color: rgba(255, 255, 255, 0.05);
    border-color: #666;
  }
}

.footer-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  margin-top: 2rem;
}

.divider {
  width: 100%;
  height: 1px;
  background-color: #e0e0e0;
  margin-bottom: 0.5rem;
}

@media (prefers-color-scheme: dark) {
  .divider {
    background-color: #333;
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
}

.api-button:hover {
  color: #333;
}

@media (prefers-color-scheme: dark) {
  .api-button {
    color: #999;
  }
  
  .api-button:hover {
    color: #ccc;
  }
}

.version {
  font-size: 0.75rem;
  color: #666;
}

@media (prefers-color-scheme: dark) {
  .version {
    color: #999;
  }
}

/* Dialog styles */
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
}

.dialog-content {
  background-color: white;
  border-radius: 12px;
  width: 90%;
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
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  font-family: inherit;
  background-color: white;
  color: inherit;
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
  border-radius: 8px;
  font-size: 0.9375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background-color: transparent;
  border: 1px solid #ddd;
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
  background-color: #1a73e8;
  border: none;
  color: white;
}

.btn-save:hover {
  background-color: #1557b0;
}
</style>
