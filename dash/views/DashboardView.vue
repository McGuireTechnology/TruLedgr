<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="border-b border-gray-200 pb-6">
      <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
      <p class="mt-1 text-sm text-gray-600">
        Welcome back, {{ user?.username }}! Here's what's happening with your security system.
      </p>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
      <div
        v-for="stat in stats"
        :key="stat.name"
        class="relative overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:px-6 sm:py-6"
      >
        <dt>
          <div :class="stat.iconBackground" class="absolute rounded-md p-3">
            <component :is="stat.icon" :class="stat.iconForeground" class="h-6 w-6" />
          </div>
          <p class="ml-16 truncate text-sm font-medium text-gray-500">{{ stat.name }}</p>
        </dt>
        <dd class="ml-16 flex items-baseline pb-6 sm:pb-7">
          <p class="text-2xl font-semibold text-gray-900">{{ stat.value }}</p>
          <p
            v-if="stat.change"
            :class="[
              stat.changeType === 'increase' ? 'text-green-600' : 'text-red-600',
              'ml-2 flex items-baseline text-sm font-semibold'
            ]"
          >
            <component
              :is="stat.changeType === 'increase' ? ArrowUpIcon : ArrowDownIcon"
              class="h-5 w-5 flex-shrink-0 self-center"
            />
            <span class="sr-only">{{ stat.changeType === 'increase' ? 'Increased' : 'Decreased' }} by</span>
            {{ stat.change }}
          </p>
        </dd>
      </div>
    </div>

    <!-- Charts Grid -->
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <!-- User Growth Chart -->
      <div class="rounded-lg bg-white p-6 shadow">
        <h3 class="text-lg font-medium text-gray-900 mb-4">User Growth</h3>
        <div class="h-64">
          <Line
            v-if="userGrowthData.datasets.length > 0"
            :data="userGrowthData"
            :options="chartOptions"
          />
          <div v-else class="flex items-center justify-center h-full text-gray-500">
            Loading chart data...
          </div>
        </div>
      </div>

      <!-- User Activity Chart -->
      <div class="rounded-lg bg-white p-6 shadow">
        <h3 class="text-lg font-medium text-gray-900 mb-4">User Activity</h3>
        <div class="h-64">
          <Doughnut
            v-if="userActivityData.datasets.length > 0"
            :data="userActivityData"
            :options="doughnutOptions"
          />
          <div v-else class="flex items-center justify-center h-full text-gray-500">
            Loading chart data...
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Activity Tables -->
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <!-- Recent Users -->
      <div class="rounded-lg bg-white shadow">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">Recent Users</h3>
        </div>
        <div class="overflow-hidden">
          <ul role="list" class="divide-y divide-gray-200">
            <li v-for="user in recentUsers" :key="user.id" class="px-6 py-4">
              <div class="flex items-center justify-between">
                <div class="flex items-center">
                  <div class="flex-shrink-0">
                    <div class="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                      <span class="text-sm font-medium text-gray-700">
                        {{ user.username.charAt(0).toUpperCase() }}
                      </span>
                    </div>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">{{ user.username }}</div>
                    <div class="text-sm text-gray-500">{{ user.email }}</div>
                  </div>
                </div>
                <div class="flex items-center space-x-2">
                  <span
                    :class="[
                      user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800',
                      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium'
                    ]"
                  >
                    {{ user.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </div>
              </div>
            </li>
          </ul>
        </div>
        <div class="px-6 py-3 bg-gray-50">
          <router-link
            to="/users"
            class="text-sm font-medium text-primary-600 hover:text-primary-500"
          >
            View all users →
          </router-link>
        </div>
      </div>

      <!-- System Health -->
      <div class="rounded-lg bg-white shadow">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">System Health</h3>
        </div>
        <div class="p-6 space-y-4">
          <div v-for="metric in systemHealth" :key="metric.name" class="flex items-center justify-between">
            <div class="flex items-center">
              <div class="text-sm font-medium text-gray-900">{{ metric.name }}</div>
            </div>
            <div class="flex items-center space-x-2">
              <div class="w-32 bg-gray-200 rounded-full h-2">
                <div
                  :class="[
                    metric.value < 70 ? 'bg-green-500' :
                    metric.value < 85 ? 'bg-yellow-500' : 'bg-red-500',
                    'h-2 rounded-full transition-all duration-300'
                  ]"
                  :style="{ width: `${metric.value}%` }"
                ></div>
              </div>
              <span class="text-sm font-medium text-gray-900">{{ metric.value }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Line, Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import {
  UsersIcon,
  CheckIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  ArrowUpIcon,
  ArrowDownIcon,
} from '@heroicons/vue/24/outline'
import { useAuthStore } from '@/stores/auth'
import { apiClient } from '@/services/api'
import type { User, UserStats } from '@/types'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
)

const authStore = useAuthStore()
const user = computed(() => authStore.user)

const loading = ref(true)
const userStats = ref<UserStats | null>(null)
const recentUsers = ref<User[]>([])

const stats = computed(() => [
  {
    name: 'Total Users',
    value: userStats.value?.total_users ?? 0,
    icon: UsersIcon,
    change: '+12%',
    changeType: 'increase',
    iconForeground: 'text-blue-600',
    iconBackground: 'bg-blue-100',
  },
  {
    name: 'Active Users',
    value: userStats.value?.active_users ?? 0,
    icon: CheckIcon,
    change: '+8%',
    changeType: 'increase',
    iconForeground: 'text-green-600',
    iconBackground: 'bg-green-100',
  },
  {
    name: 'Verified Users',
    value: userStats.value?.verified_users ?? 0,
    icon: ShieldCheckIcon,
    change: '+2%',
    changeType: 'increase',
    iconForeground: 'text-indigo-600',
    iconBackground: 'bg-indigo-100',
  },
  {
    name: 'OAuth Users',
    value: userStats.value?.oauth_users ?? 0,
    icon: ExclamationTriangleIcon,
    change: '+15%',
    changeType: 'increase',
    iconForeground: 'text-purple-600',
    iconBackground: 'bg-purple-100',
  },
])

const userGrowthData = ref({
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
  datasets: []
})

const userActivityData = ref({
  labels: ['Active', 'Inactive', 'Verified', 'Unverified'],
  datasets: []
})

const systemHealth = ref([
  { name: 'CPU Usage', value: 45 },
  { name: 'Memory Usage', value: 62 },
  { name: 'Disk Usage', value: 38 },
  { name: 'Network I/O', value: 28 },
])

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

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom' as const,
    },
  },
}

const fetchDashboardData = async () => {
  try {
    loading.value = true
    
    // Fetch user statistics
    const statsResponse = await apiClient.get('/users/stats')
    userStats.value = statsResponse.data
    
    // Fetch recent users
    const usersResponse = await apiClient.get('/users?limit=5')
    recentUsers.value = usersResponse.data.users || usersResponse.data
    
    // Update chart data
    userActivityData.value = {
      labels: ['Active', 'Inactive', 'Verified', 'Unverified'],
      datasets: [{
        data: [
          userStats.value?.active_users ?? 0,
          userStats.value?.inactive_users ?? 0,
          userStats.value?.verified_users ?? 0,
          userStats.value?.unverified_users ?? 0,
        ],
        backgroundColor: [
          '#10B981',
          '#EF4444',
          '#3B82F6',
          '#F59E0B',
        ],
        borderWidth: 0,
      }]
    }
    
    userGrowthData.value = {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      datasets: [{
        label: 'Users',
        data: [12, 19, 25, 32, 45, userStats.value?.total_users ?? 0],
        borderColor: '#3B82F6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.1,
      }]
    }
    
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchDashboardData()
})
</script>
