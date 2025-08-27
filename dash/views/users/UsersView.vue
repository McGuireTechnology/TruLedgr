<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="sm:flex sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Users Management</h1>
        <p class="mt-2 text-sm text-gray-700">
          Manage user accounts, permissions, and access control.
        </p>
      </div>
      <div class="mt-4 sm:mt-0 flex space-x-3">
        <button
          @click="loadUsers(true)"
          type="button"
          class="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          :disabled="loading"
        >
          <ArrowPathIcon class="-ml-1 mr-2 h-4 w-4" :class="{ 'animate-spin': loading }" aria-hidden="true" />
          Refresh
        </button>
        <button
          @click="showCreateModal = true"
          type="button"
          class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          <PlusIcon class="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
          New User
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div v-if="userStats" class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <UsersIcon class="h-6 w-6 text-gray-400" aria-hidden="true" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Total Users</dt>
                <dd class="text-lg font-medium text-gray-900">{{ userStats.total_users }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <CheckCircleIcon class="h-6 w-6 text-green-400" aria-hidden="true" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Active Users</dt>
                <dd class="text-lg font-medium text-gray-900">{{ userStats.active_users }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <ShieldCheckIcon class="h-6 w-6 text-blue-400" aria-hidden="true" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Verified Users</dt>
                <dd class="text-lg font-medium text-gray-900">{{ userStats.verified_users }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <ChartBarIcon class="h-6 w-6 text-indigo-400" aria-hidden="true" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Activation Rate</dt>
                <dd class="text-lg font-medium text-gray-900">{{ Math.round(userStats.activation_rate * 100) }}%</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters and Search -->
    <div class="bg-white shadow rounded-lg p-6">
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <div class="lg:col-span-2">
          <label for="search" class="block text-sm font-medium text-gray-700">Search</label>
          <input
            id="search"
            v-model="searchQuery"
            type="text"
            placeholder="Search users by name, email, or username..."
            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
            @input="debouncedSearch"
          />
        </div>
        <div>
          <label for="status-filter" class="block text-sm font-medium text-gray-700">Status</label>
          <select
            id="status-filter"
            v-model="statusFilter"
            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
            @change="applyFilters"
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
        <div>
          <label for="verification-filter" class="block text-sm font-medium text-gray-700">Verification</label>
          <select
            id="verification-filter"
            v-model="verificationFilter"
            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
            @change="applyFilters"
          >
            <option value="">All</option>
            <option value="verified">Verified</option>
            <option value="unverified">Unverified</option>
          </select>
        </div>
        <div>
          <label for="deleted-filter" class="block text-sm font-medium text-gray-700">Deleted</label>
          <select
            id="deleted-filter"
            v-model="deletedFilter"
            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
            @change="applyFilters"
          >
            <option value="false">Active Only</option>
            <option value="true">Include Deleted</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Users Table -->
    <div class="bg-white shadow overflow-hidden sm:rounded-md">
      <div v-if="loading" class="p-6 text-center">
        <div class="inline-flex items-center">
          <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Loading users...
        </div>
      </div>

      <ul v-else-if="filteredUsers.length > 0" role="list" class="divide-y divide-gray-200">
        <li v-for="user in filteredUsers" :key="user.id" class="px-6 py-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                  <span class="text-sm font-medium text-gray-700">
                    {{ getUserInitials(user) }}
                  </span>
                </div>
              </div>
              <div class="ml-4">
                <div class="flex items-center space-x-2">
                  <h3 class="text-sm font-medium text-gray-900">
                    {{ getUserDisplayName(user) }}
                  </h3>
                  <div
                    :class="[
                      'flex-shrink-0 w-2.5 h-2.5 rounded-full',
                      user.is_active ? 'bg-green-400' : 'bg-red-400'
                    ]"
                  ></div>
                </div>
                <p class="text-sm text-gray-500">{{ user.email }}</p>
                <p v-if="user.username !== user.email" class="text-sm text-gray-500">@{{ user.username }}</p>
              </div>
            </div>
            <div class="flex items-center space-x-4">
              <div class="flex flex-col items-end space-y-1">
                <span
                  :class="[
                    'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                    user.is_active 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  ]"
                >
                  {{ user.is_active ? 'Active' : 'Inactive' }}
                </span>
                <span
                  v-if="user.is_verified"
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                >
                  Verified
                </span>
              </div>
              <div class="flex items-center space-x-2">
                <button
                  @click="viewUser(user)"
                  class="p-1 text-gray-400 hover:text-gray-600"
                  title="View user details"
                >
                  <EyeIcon class="h-4 w-4" />
                </button>
                <button
                  @click="editUser(user)"
                  class="p-1 text-gray-400 hover:text-gray-600"
                  title="Edit user"
                >
                  <PencilIcon class="h-4 w-4" />
                </button>
                <button
                  v-if="user.is_active"
                  @click="toggleUserStatus(user)"
                  class="p-1 text-gray-400 hover:text-yellow-600"
                  title="Deactivate user"
                >
                  <EyeSlashIcon class="h-4 w-4" />
                </button>
                <button
                  v-else
                  @click="toggleUserStatus(user)"
                  class="p-1 text-gray-400 hover:text-green-600"
                  title="Activate user"
                >
                  <EyeIcon class="h-4 w-4" />
                </button>
                <button
                  @click="confirmDelete(user)"
                  class="p-1 text-gray-400 hover:text-red-600"
                  title="Delete user"
                >
                  <TrashIcon class="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        </li>
      </ul>

      <!-- Empty State -->
      <div v-else class="text-center py-12">
        <UsersIcon class="mx-auto h-12 w-12 text-gray-400" />
        <h3 class="mt-2 text-sm font-medium text-gray-900">No users found</h3>
        <p class="mt-1 text-sm text-gray-500">
          {{ searchQuery || statusFilter !== '' ? 'Try adjusting your filters.' : 'Get started by creating a new user.' }}
        </p>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
      <div class="flex-1 flex justify-between sm:hidden">
        <button
          @click="setPage(currentPage - 1)"
          :disabled="currentPage <= 1"
          class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
        >
          Previous
        </button>
        <button
          @click="setPage(currentPage + 1)"
          :disabled="currentPage >= totalPages"
          class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
        >
          Next
        </button>
      </div>
      <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
        <div>
          <p class="text-sm text-gray-700">
            Showing
            <span class="font-medium">{{ ((currentPage - 1) * pageSize) + 1 }}</span>
            to
            <span class="font-medium">{{ Math.min(currentPage * pageSize, totalUsers) }}</span>
            of
            <span class="font-medium">{{ totalUsers }}</span>
            results
          </p>
        </div>
        <div>
          <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
            <button
              @click="setPage(currentPage - 1)"
              :disabled="currentPage <= 1"
              class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
            >
              <ChevronLeftIcon class="h-5 w-5" />
            </button>
            <button
              @click="setPage(currentPage + 1)"
              :disabled="currentPage >= totalPages"
              class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
            >
              <ChevronRightIcon class="h-5 w-5" />
            </button>
          </nav>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <UserModal 
      v-if="showCreateModal || editingUser"
      :user="editingUser"
      @close="closeModal"
      @save="handleSave"
    />

    <!-- Delete Confirmation Modal -->
    <ConfirmModal
      v-if="userToDelete"
      title="Delete User"
      :message="`Are you sure you want to delete user '${getUserDisplayName(userToDelete)}'? This action cannot be undone.`"
      confirm-text="Delete"
      confirm-class="bg-red-600 hover:bg-red-700 focus:ring-red-500"
      @confirm="handleDelete"
      @cancel="userToDelete = null"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUsersStore } from '@/stores/users'
import { useToast } from 'vue-toastification'
import { useDebounceFn } from '@vueuse/core'
import type { User, UserCreate, UserUpdate } from '@/types'
import {
  PlusIcon,
  ArrowPathIcon,
  UsersIcon,
  CheckCircleIcon,
  ShieldCheckIcon,
  ChartBarIcon,
  PencilIcon,
  TrashIcon,
  EyeIcon,
  EyeSlashIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
} from '@heroicons/vue/24/outline'
import UserModal from './UserModal.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'

const router = useRouter()
const usersStore = useUsersStore()
const toast = useToast()

// Reactive data
const showCreateModal = ref(false)
const editingUser = ref<User | null>(null)
const userToDelete = ref<User | null>(null)
const searchQuery = ref('')
const statusFilter = ref('')
const verificationFilter = ref('')
const deletedFilter = ref('false')

// Computed properties from store
const users = computed(() => usersStore.users)
const userStats = computed(() => usersStore.userStats)
const loading = computed(() => usersStore.loading)
const currentPage = computed(() => usersStore.currentPage)
const pageSize = computed(() => usersStore.pageSize)
const totalUsers = computed(() => usersStore.totalUsers)
const totalPages = computed(() => usersStore.totalPages)

// Filtered users for display
const filteredUsers = computed(() => {
  let filtered = users.value || []

  // Apply status filter
  if (statusFilter.value === 'active') {
    filtered = filtered.filter((user) => user.is_active)
  } else if (statusFilter.value === 'inactive') {
    filtered = filtered.filter((user) => !user.is_active)
  }

  // Apply verification filter
  if (verificationFilter.value === 'verified') {
    filtered = filtered.filter((user) => user.is_verified)
  } else if (verificationFilter.value === 'unverified') {
    filtered = filtered.filter((user) => !user.is_verified)
  }

  return filtered
})

// Helper functions
const getUserInitials = (user: User) => {
  if (user.first_name && user.last_name) {
    return `${user.first_name.charAt(0)}${user.last_name.charAt(0)}`.toUpperCase()
  }
  return user.username.charAt(0).toUpperCase()
}

const getUserDisplayName = (user: User) => {
  if (user.first_name && user.last_name) {
    return `${user.first_name} ${user.last_name}`
  }
  return user.username
}

// Methods
const loadUsers = async (force = false) => {
  try {
    await usersStore.fetchUsers(force)
    await usersStore.fetchUserStats()
  } catch (error) {
    toast.error('Failed to load users')
  }
}

const debouncedSearch = useDebounceFn(async () => {
  await usersStore.searchUsers(searchQuery.value)
}, 300)

const applyFilters = async () => {
  const filters = {
    is_active: statusFilter.value === 'active' ? true : statusFilter.value === 'inactive' ? false : undefined,
    is_verified: verificationFilter.value === 'verified' ? true : verificationFilter.value === 'unverified' ? false : undefined,
    include_deleted: deletedFilter.value === 'true',
  }
  await usersStore.setFilters(filters)
}

const setPage = async (page: number) => {
  await usersStore.setPage(page)
}

const viewUser = (user: User) => {
  router.push(`/users/${user.id}`)
}

const editUser = (user: User) => {
  editingUser.value = { ...user }
}

const closeModal = () => {
  showCreateModal.value = false
  editingUser.value = null
}

const handleSave = async (userData: UserCreate | UserUpdate) => {
  try {
    if (editingUser.value) {
      // Update existing user
      await usersStore.updateUser(editingUser.value.id, userData as UserUpdate)
      toast.success('User updated successfully!')
    } else {
      // Create new user
      await usersStore.createUser(userData as UserCreate)
      toast.success('User created successfully!')
    }
    closeModal()
  } catch (error) {
    toast.error('Failed to save user')
  }
}

const toggleUserStatus = async (user: User) => {
  try {
    if (user.is_active) {
      await usersStore.deactivateUser(user.id)
      toast.success('User deactivated successfully!')
    } else {
      await usersStore.activateUser(user.id)
      toast.success('User activated successfully!')
    }
  } catch (error) {
    toast.error('Failed to update user status')
  }
}

const confirmDelete = (user: User) => {
  userToDelete.value = user
}

const handleDelete = async () => {
  if (!userToDelete.value) return
  
  try {
    await usersStore.deleteUser(userToDelete.value.id, false) // Soft delete
    toast.success('User deleted successfully!')
    userToDelete.value = null
  } catch (error) {
    toast.error('Failed to delete user')
  }
}

// Initialize
onMounted(async () => {
  await loadUsers(true)
})
</script>
