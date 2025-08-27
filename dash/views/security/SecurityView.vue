<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="border-b border-gray-200 pb-6">
      <h1 class="text-2xl font-bold text-gray-900">Security Dashboard</h1>
      <p class="mt-1 text-sm text-gray-600">
        Monitor security events, account lockouts, and active sessions in real-time.
      </p>
    </div>

    <!-- Security Metrics Cards -->
    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
      <div
        v-for="metric in securityMetricsCards"
        :key="metric.name"
        class="relative overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:px-6 sm:py-6"
      >
        <dt>
          <div :class="metric.iconBackground" class="absolute rounded-md p-3">
            <component :is="metric.icon" :class="metric.iconForeground" class="h-6 w-6" />
          </div>
          <p class="ml-16 truncate text-sm font-medium text-gray-500">{{ metric.name }}</p>
        </dt>
        <dd class="ml-16 flex items-baseline">
          <p class="text-2xl font-semibold text-gray-900">{{ metric.value }}</p>
          <p
            v-if="metric.trend"
            :class="[
              metric.trend > 0 ? 'text-red-600' : 'text-green-600',
              'ml-2 flex items-baseline text-sm font-semibold',
            ]"
          >
            <component
              :is="metric.trend > 0 ? ArrowUpIcon : ArrowDownIcon"
              class="h-4 w-4 flex-shrink-0 self-center"
            />
            {{ Math.abs(metric.trend) }}%
          </p>
        </dd>
      </div>
    </div>

    <!-- Security Events and Alerts -->
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <!-- Critical Security Events -->
      <div class="rounded-lg bg-white shadow">
        <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">Critical Security Events</h3>
          <button
            @click="refreshEvents"
            :disabled="securityStore.loading"
            class="text-sm text-primary-600 hover:text-primary-500 disabled:opacity-50"
          >
            <ArrowPathIcon class="h-4 w-4 inline mr-1" />
            Refresh
          </button>
        </div>
        <div class="divide-y divide-gray-200 max-h-96 overflow-y-auto">
          <div
            v-for="event in securityStore.criticalEvents"
            :key="event.id"
            class="px-6 py-4 hover:bg-gray-50"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <div
                  :class="getEventIconClasses(event.event_type)"
                  class="flex-shrink-0 w-2 h-2 rounded-full"
                ></div>
                <div>
                  <p class="text-sm font-medium text-gray-900">
                    {{ getEventTitle(event.event_type) }}
                  </p>
                  <p class="text-sm text-gray-500">
                    {{ event.username || 'Unknown user' }} • {{ event.ip_address }}
                  </p>
                </div>
              </div>
              <div class="text-right">
                <p class="text-sm text-gray-900">{{ formatDateTime(event.timestamp) }}</p>
                <span
                  :class="getSeverityClasses(event.severity)"
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                >
                  {{ event.severity.toUpperCase() }}
                </span>
              </div>
            </div>
          </div>
          <div v-if="securityStore.criticalEvents.length === 0" class="px-6 py-8 text-center">
            <ShieldCheckIcon class="mx-auto h-12 w-12 text-gray-400" />
            <p class="mt-2 text-sm text-gray-500">No critical security events</p>
          </div>
        </div>
      </div>

      <!-- Account Lockouts -->
      <div class="rounded-lg bg-white shadow">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">Active Account Lockouts</h3>
        </div>
        <div class="divide-y divide-gray-200 max-h-96 overflow-y-auto">
          <div
            v-for="lockout in securityStore.activeAccountLockouts"
            :key="lockout.id"
            class="px-6 py-4 hover:bg-gray-50"
          >
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-900">{{ lockout.username }}</p>
                <p class="text-sm text-gray-500">
                  {{ lockout.failed_attempts }} failed attempts • {{ lockout.ip_address }}
                </p>
                <p class="text-sm text-gray-500">
                  Locked {{ formatDateTime(lockout.locked_at) }}
                </p>
              </div>
              <button
                @click="unlockAccount(lockout.id)"
                :disabled="securityStore.loading"
                class="bg-red-100 text-red-800 hover:bg-red-200 px-3 py-1 rounded-full text-sm font-medium disabled:opacity-50"
              >
                Unlock
              </button>
            </div>
          </div>
          <div v-if="securityStore.activeAccountLockouts.length === 0" class="px-6 py-8 text-center">
            <LockOpenIcon class="mx-auto h-12 w-12 text-gray-400" />
            <p class="mt-2 text-sm text-gray-500">No active account lockouts</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Active Sessions and Recent Events -->
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <!-- Active Sessions -->
      <div class="rounded-lg bg-white shadow">
        <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">Active User Sessions</h3>
          <span class="text-sm text-gray-500">
            {{ securityStore.activeSessions.length }} active
          </span>
        </div>
        <div class="divide-y divide-gray-200 max-h-96 overflow-y-auto">
          <div
            v-for="session in securityStore.activeSessions.slice(0, 10)"
            :key="session.id"
            class="px-6 py-4 hover:bg-gray-50"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <div class="flex-shrink-0">
                  <div
                    :class="getDeviceIconClasses(session.device_type)"
                    class="w-8 h-8 rounded-full flex items-center justify-center"
                  >
                    <component :is="getDeviceIcon(session.device_type)" class="h-4 w-4" />
                  </div>
                </div>
                <div>
                  <p class="text-sm font-medium text-gray-900">{{ session.username }}</p>
                  <p class="text-sm text-gray-500">
                    {{ session.browser }} • {{ session.location || session.ip_address }}
                  </p>
                  <p class="text-sm text-gray-500">
                    Active for {{ getSessionDuration(session.login_time) }}
                  </p>
                </div>
              </div>
              <button
                @click="revokeSession(session.id)"
                :disabled="securityStore.loading"
                class="text-red-600 hover:text-red-500 text-sm font-medium disabled:opacity-50"
              >
                Revoke
              </button>
            </div>
          </div>
          <div v-if="securityStore.activeSessions.length === 0" class="px-6 py-8 text-center">
            <ComputerDesktopIcon class="mx-auto h-12 w-12 text-gray-400" />
            <p class="mt-2 text-sm text-gray-500">No active sessions</p>
          </div>
        </div>
      </div>

      <!-- Recent Security Events Chart -->
      <div class="rounded-lg bg-white shadow">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">Security Events (24h)</h3>
        </div>
        <div class="p-6">
          <div class="h-64">
            <Bar
              v-if="eventChartData.datasets.length > 0"
              :data="eventChartData"
              :options="chartOptions"
            />
            <div v-else class="flex items-center justify-center h-full text-gray-500">
              Loading chart data...
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Event Type Filter and Recent Events Table -->
    <div class="rounded-lg bg-white shadow">
      <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <h3 class="text-lg font-medium text-gray-900">Recent Security Events</h3>
        <div class="flex items-center space-x-4">
          <select
            v-model="selectedEventType"
            @change="filterEvents"
            class="rounded-md border-gray-300 text-sm"
          >
            <option value="">All Events</option>
            <option value="login_success">Login Success</option>
            <option value="login_failure">Login Failure</option>
            <option value="password_change">Password Change</option>
            <option value="account_lockout">Account Lockout</option>
            <option value="oauth_login">OAuth Login</option>
            <option value="suspicious_activity">Suspicious Activity</option>
          </select>
        </div>
      </div>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Event
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                User
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                IP Address
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Severity
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Timestamp
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="event in securityStore.recentEvents" :key="event.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div
                    :class="getEventIconClasses(event.event_type)"
                    class="flex-shrink-0 w-3 h-3 rounded-full mr-3"
                  ></div>
                  <span class="text-sm font-medium text-gray-900">
                    {{ getEventTitle(event.event_type) }}
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ event.username || 'Unknown' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ event.ip_address }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="getSeverityClasses(event.severity)"
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                >
                  {{ event.severity.toUpperCase() }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDateTime(event.timestamp) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="securityStore.recentEvents.length === 0" class="px-6 py-8 text-center">
        <p class="text-sm text-gray-500">No security events found</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js'
import {
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  LockClosedIcon,
  LockOpenIcon,
  ComputerDesktopIcon,
  DevicePhoneMobileIcon,
  DeviceTabletIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  ArrowPathIcon,
} from '@heroicons/vue/24/outline'
import { useSecurityStore } from '@/stores/security'
import { formatDistanceToNow, parseISO, format } from 'date-fns'
import { useToast } from 'vue-toastification'

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const securityStore = useSecurityStore()
const toast = useToast()
const selectedEventType = ref('')

const securityMetricsCards = computed(() => [
  {
    name: 'Failed Logins (24h)',
    value: securityStore.metrics?.failed_logins_24h ?? 0,
    icon: ExclamationTriangleIcon,
    trend: 5,
    iconForeground: 'text-red-600',
    iconBackground: 'bg-red-100',
  },
  {
    name: 'Successful Logins (24h)',
    value: securityStore.metrics?.successful_logins_24h ?? 0,
    icon: ShieldCheckIcon,
    trend: -2,
    iconForeground: 'text-green-600',
    iconBackground: 'bg-green-100',
  },
  {
    name: 'Account Lockouts',
    value: securityStore.activeAccountLockouts.length,
    icon: LockClosedIcon,
    trend: 0,
    iconForeground: 'text-yellow-600',
    iconBackground: 'bg-yellow-100',
  },
  {
    name: 'Active Sessions',
    value: securityStore.activeSessions.length,
    icon: ComputerDesktopIcon,
    trend: -8,
    iconForeground: 'text-blue-600',
    iconBackground: 'bg-blue-100',
  },
])

const eventChartData = computed(() => {
  if (!securityStore.metrics) {
    return { labels: [], datasets: [] }
  }

  return {
    labels: ['Login Success', 'Login Failure', 'Password Change', 'Account Lockout', 'OAuth Login', 'Suspicious'],
    datasets: [
      {
        label: 'Events (24h)',
        data: [
          securityStore.metrics.successful_logins_24h,
          securityStore.metrics.failed_logins_24h,
          securityStore.metrics.password_changes_24h,
          securityStore.metrics.account_lockouts_24h,
          securityStore.metrics.oauth_logins_24h,
          securityStore.metrics.suspicious_activities_24h,
        ],
        backgroundColor: ['#10B981', '#EF4444', '#3B82F6', '#F59E0B', '#8B5CF6', '#F97316'],
        borderWidth: 0,
      },
    ],
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      beginAtZero: true,
    },
  },
  plugins: {
    legend: {
      display: false,
    },
  },
}

const getEventTitle = (eventType: string): string => {
  const titles: Record<string, string> = {
    login_success: 'Login Success',
    login_failure: 'Login Failure',
    password_change: 'Password Change',
    account_lockout: 'Account Lockout',
    oauth_login: 'OAuth Login',
    suspicious_activity: 'Suspicious Activity',
  }
  return titles[eventType] || eventType
}

const getEventIconClasses = (eventType: string): string => {
  const classes: Record<string, string> = {
    login_success: 'bg-green-500',
    login_failure: 'bg-red-500',
    password_change: 'bg-blue-500',
    account_lockout: 'bg-yellow-500',
    oauth_login: 'bg-purple-500',
    suspicious_activity: 'bg-orange-500',
  }
  return classes[eventType] || 'bg-gray-500'
}

const getSeverityClasses = (severity: string): string => {
  const classes: Record<string, string> = {
    low: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-orange-100 text-orange-800',
    critical: 'bg-red-100 text-red-800',
  }
  return classes[severity] || 'bg-gray-100 text-gray-800'
}

const getDeviceIcon = (deviceType: string) => {
  const icons: Record<string, unknown> = {
    mobile: DevicePhoneMobileIcon,
    tablet: DeviceTabletIcon,
    desktop: ComputerDesktopIcon,
  }
  return icons[deviceType] || ComputerDesktopIcon
}

const getDeviceIconClasses = (deviceType: string): string => {
  const classes: Record<string, string> = {
    mobile: 'bg-blue-100 text-blue-600',
    tablet: 'bg-green-100 text-green-600',
    desktop: 'bg-gray-100 text-gray-600',
  }
  return classes[deviceType] || 'bg-gray-100 text-gray-600'
}

const getSessionDuration = (loginTime: string): string => {
  return formatDistanceToNow(parseISO(loginTime), { addSuffix: false })
}

const formatDateTime = (timestamp: string): string => {
  return format(parseISO(timestamp), 'MMM dd, HH:mm')
}

const refreshEvents = async () => {
  try {
    await securityStore.fetchSecurityEvents()
    toast.success('Security events refreshed')
  } catch (error) {
    toast.error('Failed to refresh security events')
  }
}

const filterEvents = async () => {
  try {
    await securityStore.fetchSecurityEvents(50, selectedEventType.value || undefined)
  } catch (error) {
    toast.error('Failed to filter events')
  }
}

const unlockAccount = async (lockoutId: string) => {
  try {
    await securityStore.unlockAccount(lockoutId)
    toast.success('Account unlocked successfully')
  } catch (error) {
    toast.error('Failed to unlock account')
  }
}

const revokeSession = async (sessionId: string) => {
  try {
    await securityStore.revokeSession(sessionId)
    toast.success('Session revoked successfully')
  } catch (error) {
    toast.error('Failed to revoke session')
  }
}

const loadDashboardData = async () => {
  try {
    await Promise.all([
      securityStore.fetchSecurityMetrics(),
      securityStore.fetchSecurityEvents(),
      securityStore.fetchAccountLockouts(),
      securityStore.fetchSessionAnalytics(),
    ])
  } catch (error) {
    console.error('Failed to load security dashboard data:', error)
  }
}

onMounted(() => {
  loadDashboardData()
})
</script>
