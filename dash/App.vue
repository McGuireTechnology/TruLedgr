<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- Authentication Loading -->
    <div v-if="!authStore.initialized" class="flex items-center justify-center min-h-screen">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading...</p>
      </div>
    </div>
    
    <!-- Main App -->
    <template v-else>
      <!-- Navigation -->
      <Navbar v-if="!isLoginPage" />
      
      <!-- Main Content -->
      <div :class="{ 'ml-64': !isLoginPage && !isMobileMenuOpen, 'ml-0': isLoginPage || isMobileMenuOpen }">
        <router-view />
      </div>
      
      <!-- Mobile Menu Overlay -->
      <div 
        v-if="isMobileMenuOpen && !isLoginPage"
        class="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"
        @click="closeMobileMenu"
      ></div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUIStore } from '@/stores/ui'
import Navbar from '@/components/layout/Navbar.vue'

const route = useRoute()
const authStore = useAuthStore()
const uiStore = useUIStore()

const isLoginPage = computed(() => route.name === 'login')
const isMobileMenuOpen = computed(() => uiStore.isMobileMenuOpen)

const closeMobileMenu = () => {
  uiStore.closeMobileMenu()
}

onMounted(async () => {
  // Check if user is authenticated on app load
  await authStore.checkAuth()
})
</script>
