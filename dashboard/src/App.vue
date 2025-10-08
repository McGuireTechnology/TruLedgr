<template>
  <div class="app">
    <header>
      <h1>{{ title }}</h1>
    </header>
    <main>
      <div class="greeting">
        <h2>{{ greeting }}</h2>
        <p>{{ description }}</p>
      </div>
      <div class="api-status">
        <button
          :disabled="loading"
          @click="testApi"
        >
          {{ loading ? 'Testing...' : 'Test API Connection' }}
        </button>
        <p
          v-if="apiMessage"
          :class="{ success: apiSuccess, error: !apiSuccess }"
        >
          {{ apiMessage }}
        </p>
      </div>
    </main>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      title: 'TruLedgr',
      greeting: 'Bonjour!',
      description: 'Personal Finance Application Suite',
      loading: false,
      apiMessage: '',
      apiSuccess: false
    }
  },
  methods: {
    async testApi() {
      this.loading = true
      // define apiBase in the outer scope so the catch block can reference it
      let apiBase = 'http://localhost:8000'
      try {
        // Resolve API URL in this order:
        // 1. build-time Vite env: import.meta.env.VITE_API_URL
        // 2. runtime global (injected by platform) window.__API_URL__
        // 3. fallback to current origin (useful when dashboard and api are same host)
        // 4. final fallback to localhost:8000 for local development.
        const viteApi = typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_URL
          ? import.meta.env.VITE_API_URL
          : undefined
        const runtimeApi = typeof window !== 'undefined' && window.__API_URL__
          ? window.__API_URL__
          : undefined
        const defaultOrigin = (typeof window !== 'undefined' && window.location && window.location.origin) ? window.location.origin : ''
        apiBase = viteApi || runtimeApi || defaultOrigin || apiBase
        const response = await fetch(apiBase + '/')
        if (response.ok) {
          const data = await response.json()
          this.apiMessage = data.message
          this.apiSuccess = true
        } else {
          throw new Error('API not responding')
        }
      } catch (error) {
        this.apiMessage = `Cannot connect to API at ${apiBase} — check the API URL and CORS settings.`
        this.apiSuccess = false
      }
      this.loading = false
    }
  }
}
</script>

<style>
.app {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

header {
  text-align: center;
  margin-bottom: 2rem;
}

h1 {
  color: #2c3e50;
  font-size: 3rem;
  margin: 0;
}

.greeting {
  text-align: center;
  margin-bottom: 2rem;
}

h2 {
  color: #3498db;
  font-size: 2rem;
  margin: 0 0 1rem 0;
}

.api-status {
  text-align: center;
  margin-top: 2rem;
}

button {
  background: #3498db;
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

button:hover:not(:disabled) {
  background: #2980b9;
}

button:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.success {
  color: #27ae60;
  font-weight: bold;
}

.error {
  color: #e74c3c;
  font-weight: bold;
}
</style>
