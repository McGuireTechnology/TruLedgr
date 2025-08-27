<template>
  <div class="bg-white shadow-sm border-b border-gray-200">
    <!-- Desktop Sidebar -->
    <div class="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
      <div class="flex min-h-0 flex-1 flex-col border-r border-gray-200 bg-white">
        <div class="flex flex-1 flex-col overflow-y-auto pt-5 pb-4">
          <!-- Logo -->
          <div class="flex flex-shrink-0 items-center px-4">
            <h1 class="text-xl font-bold text-gray-900">Security Dashboard</h1>
          </div>
          
          <!-- Navigation -->
          <nav class="mt-8 flex-1 space-y-1 px-2">
            <router-link
              v-for="item in navigation"
              :key="item.name"
              :to="item.href"
              class="group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors"
              :class="[
                $route.name === item.name
                  ? 'bg-primary-100 text-primary-900'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              ]"
            >
              <component
                :is="item.icon"
                class="mr-3 h-5 w-5 flex-shrink-0"
                :class="[
                  $route.name === item.name
                    ? 'text-primary-500'
                    : 'text-gray-400 group-hover:text-gray-500'
                ]"
              />
              {{ item.displayName }}
            </router-link>
          </nav>
        </div>
        
        <!-- User Profile -->
        <div class="flex flex-shrink-0 border-t border-gray-200 p-4">
          <div class="group block w-full flex-shrink-0">
            <div class="flex items-center">
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-700">{{ user?.username }}</p>
                <button
                  @click="logout"
                  class="text-xs font-medium text-gray-500 hover:text-gray-700"
                >
                  Sign out
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile menu button -->
    <div class="flex items-center justify-between p-4 lg:hidden">
      <h1 class="text-lg font-bold text-gray-900">Security Dashboard</h1>
      <button
        type="button"
        class="inline-flex items-center justify-center rounded-md p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-500"
        @click="uiStore.toggleMobileMenu()"
      >
        <Bars3Icon class="h-6 w-6" />
      </button>
    </div>

    <!-- Mobile sidebar -->
    <div
      v-show="uiStore.isMobileMenuOpen"
      class="relative z-50 lg:hidden"
    >
      <div class="fixed inset-0 bg-gray-600 bg-opacity-75" @click="uiStore.closeMobileMenu()"></div>
      
      <div class="fixed inset-y-0 left-0 flex w-full max-w-xs flex-col bg-white">
        <div class="flex min-h-0 flex-1 flex-col pt-5 pb-4">
          <div class="flex flex-shrink-0 items-center px-4">
            <h1 class="text-lg font-bold text-gray-900">Security Dashboard</h1>
          </div>
          
          <nav class="mt-8 flex-1 space-y-1 px-2">
            <router-link
              v-for="item in navigation"
              :key="item.name"
              :to="item.href"
              @click="uiStore.closeMobileMenu()"
              class="group flex items-center px-2 py-2 text-base font-medium rounded-md"
              :class="[
                $route.name === item.name
                  ? 'bg-primary-100 text-primary-900'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              ]"
            >
              <component
                :is="item.icon"
                class="mr-4 h-6 w-6 flex-shrink-0"
                :class="[
                  $route.name === item.name
                    ? 'text-primary-500'
                    : 'text-gray-400 group-hover:text-gray-500'
                ]"
              />
              {{ item.displayName }}
            </router-link>
          </nav>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUIStore } from '@/stores/ui'
import {
  HomeIcon,
  UsersIcon,
  ShieldCheckIcon,
  KeyIcon,
  CogIcon,
  Bars3Icon,
  UserGroupIcon,
  CubeIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()
const uiStore = useUIStore()

const user = computed(() => authStore.user)

const navigation = [
  { name: 'dashboard', displayName: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'users', displayName: 'Users', href: '/users', icon: UsersIcon },
  { name: 'groups', displayName: 'Groups', href: '/groups', icon: UserGroupIcon },
  { name: 'items', displayName: 'Items', href: '/items', icon: CubeIcon },
  { name: 'roles', displayName: 'Roles', href: '/roles', icon: UserGroupIcon },
  { name: 'permissions', displayName: 'Permissions', href: '/permissions', icon: KeyIcon },
  { name: 'security', displayName: 'Security', href: '/security', icon: ShieldCheckIcon },
  { name: 'settings', displayName: 'Settings', href: '/settings', icon: CogIcon },
]

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>
