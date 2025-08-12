<template>
  <div class="dashboard-view">
    <header class="dashboard-header">
      <h1>{{ appTitle }}</h1>
      <div class="user-info" v-if="currentUser">
        Welcome, {{ currentUser.full_name || currentUser.email }}
      </div>
    </header>

    <main class="dashboard-content">
      <div class="status-card">
        <h2>System Status</h2>
        <div v-if="apiHealth" class="status-indicator" :class="apiHealth.status">
          <span class="status-dot"></span>
          {{ apiHealth.status }}: {{ apiHealth.message }}
        </div>
      </div>

      <div class="features-grid">
        <div class="feature-card" v-if="mobileConfig">
          <h3>Mobile App Features</h3>
          <ul>
            <li v-if="mobileConfig.features.biometric_auth">✅ Biometric Authentication</li>
            <li v-if="mobileConfig.features.push_notifications">✅ Push Notifications</li>
            <li v-if="mobileConfig.features.offline_mode">✅ Offline Mode</li>
          </ul>
          <p>
            <small>Min App Version: {{ mobileConfig.min_app_version }}</small>
          </p>
        </div>

        <div class="feature-card">
          <h3>Quick Actions</h3>
          <button class="action-btn" @click="refreshData">Refresh Data</button>
          <button class="action-btn danger" @click="logout">Logout</button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { api, type User, type HealthCheck, type MobileConfig } from '../services/api'

const router = useRouter()
const currentUser = ref<User | null>(null)
const apiHealth = ref<HealthCheck | null>(null)
const mobileConfig = ref<MobileConfig | null>(null)

const appTitle = computed(() => import.meta.env.VITE_APP_TITLE || 'TruLedgr Dashboard')

const loadUserData = async () => {
  try {
    currentUser.value = await api.getCurrentUser()
  } catch (error) {
    console.error('Failed to load user data:', error)
    // Redirect to login if not authenticated
    await router.push('/login')
  }
}

const loadApiHealth = async () => {
  try {
    apiHealth.value = await api.healthCheck()
  } catch (error) {
    console.error('Failed to check API health:', error)
    apiHealth.value = {
      status: 'error',
      message: 'API unavailable',
      version: 'unknown',
    }
  }
}

const loadMobileConfig = async () => {
  try {
    mobileConfig.value = await api.getMobileConfig()
  } catch (error) {
    console.error('Failed to load mobile config:', error)
  }
}

const refreshData = async () => {
  await Promise.all([loadUserData(), loadApiHealth(), loadMobileConfig()])
}

const logout = async () => {
  await api.logout()
  await router.push('/login')
}

onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.dashboard-view {
  min-height: 100vh;
  background: #f5f5f5;
}

.dashboard-header {
  background: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dashboard-header h1 {
  color: #2c3e50;
  margin: 0;
}

.user-info {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.dashboard-content {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.status-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
}

.status-indicator.healthy {
  color: #27ae60;
}

.status-indicator.error {
  color: #e74c3c;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: currentColor;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.feature-card h3 {
  margin-top: 0;
  color: #2c3e50;
}

.feature-card ul {
  list-style: none;
  padding: 0;
}

.feature-card li {
  padding: 0.25rem 0;
}

.action-btn {
  background: #3498db;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  margin-right: 1rem;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  transition: background-color 0.2s;
}

.action-btn:hover {
  background: #2980b9;
}

.action-btn.danger {
  background: #e74c3c;
}

.action-btn.danger:hover {
  background: #c0392b;
}

@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .dashboard-content {
    padding: 1rem;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }
}
</style>
