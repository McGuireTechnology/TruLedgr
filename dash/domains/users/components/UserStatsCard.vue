<template>
  <div class="bg-white shadow rounded-lg p-6">
    <h3 class="text-lg font-medium text-gray-900 mb-4">User Statistics</h3>
    
    <div v-if="loading" class="animate-pulse">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div v-for="i in 4" :key="i" class="h-16 bg-gray-200 rounded"></div>
      </div>
    </div>
    
    <div v-else-if="stats" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="text-center">
        <div class="text-2xl font-bold text-blue-600">{{ stats.total_users }}</div>
        <div class="text-sm text-gray-500">Total Users</div>
      </div>
      
      <div class="text-center">
        <div class="text-2xl font-bold text-green-600">{{ stats.active_users }}</div>
        <div class="text-sm text-gray-500">Active</div>
      </div>
      
      <div class="text-center">
        <div class="text-2xl font-bold text-yellow-600">{{ stats.verified_users }}</div>
        <div class="text-sm text-gray-500">Verified</div>
      </div>
      
      <div class="text-center">
        <div class="text-2xl font-bold text-purple-600">{{ Math.round(stats.activation_rate) }}%</div>
        <div class="text-sm text-gray-500">Activation Rate</div>
      </div>
    </div>
    
    <div v-else-if="error" class="text-red-600 text-center py-4">
      {{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { usersApi } from '../api'
import type { UserStats } from '../types'

const stats = ref<UserStats | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

const loadStats = async () => {
  loading.value = true
  error.value = null
  
  try {
    stats.value = await usersApi.getUserStats()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load statistics'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadStats()
})
</script>
