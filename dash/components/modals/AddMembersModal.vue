<!-- Add Members Modal -->
<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
      <div class="mt-3">
        <!-- Header -->
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium text-gray-900">Add Members to {{ group?.name }}</h3>
          <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <!-- User Search -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Search Users</label>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search by username or email..."
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              @input="handleSearch"
            />
          </div>

          <!-- Available Users -->
          <div v-if="searchResults.length > 0" class="max-h-48 overflow-y-auto border border-gray-200 rounded-md">
            <div
              v-for="user in searchResults"
              :key="user.id"
              class="flex items-center justify-between p-3 hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
            >
              <div class="flex items-center space-x-3">
                <div class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                  <span class="text-sm font-medium text-gray-700">
                    {{ user.username?.charAt(0).toUpperCase() || '?' }}
                  </span>
                </div>
                <div>
                  <p class="font-medium text-gray-900">{{ user.username }}</p>
                  <p class="text-sm text-gray-500">{{ user.email }}</p>
                </div>
              </div>
              <button
                type="button"
                @click="toggleUser(user)"
                :class="[
                  'px-3 py-1 rounded-md text-sm font-medium',
                  selectedUsers.some(u => u.id === user.id)
                    ? 'bg-indigo-100 text-indigo-800'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                ]"
              >
                {{ selectedUsers.some(u => u.id === user.id) ? 'Remove' : 'Add' }}
              </button>
            </div>
          </div>

          <!-- Selected Users -->
          <div v-if="selectedUsers.length > 0" class="space-y-2">
            <label class="block text-sm font-medium text-gray-700">Selected Users ({{ selectedUsers.length }})</label>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="user in selectedUsers"
                :key="user.id"
                class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-indigo-100 text-indigo-800"
              >
                {{ user.username }}
                <button
                  type="button"
                  @click="removeUser(user)"
                  class="ml-2 text-indigo-600 hover:text-indigo-800"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </span>
            </div>
          </div>

          <!-- Role Selection -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Default Role</label>
            <select
              v-model="selectedRole"
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option v-for="role in availableRoles" :key="role.value" :value="role.value">
                {{ role.label }}
              </option>
            </select>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md p-3">
            {{ error }}
          </div>

          <!-- Action Buttons -->
          <div class="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              @click="$emit('close')"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="loading || selectedUsers.length === 0"
              class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="loading">Adding...</span>
              <span v-else>Add {{ selectedUsers.length }} Member{{ selectedUsers.length !== 1 ? 's' : '' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useGroupsStore } from '@/stores/groups'
import { useUsersStore } from '@/stores/users'
import { GROUP_ROLES } from '@/domains/groups'
import type { Group, User, GroupMembershipRequest } from '@/types'

// Props
const props = defineProps<{
  group: Group
}>()

// Emits
const emit = defineEmits<{
  close: []
  added: []
}>()

// Stores
const groupsStore = useGroupsStore()
const usersStore = useUsersStore()

// State
const searchQuery = ref('')
const selectedUsers = ref<User[]>([])
const selectedRole = ref(GROUP_ROLES.MEMBER)
const loading = ref(false)
const error = ref<string | null>(null)

// Computed
const searchResults = computed(() => {
  if (!searchQuery.value.trim()) return []
  
  // Filter out users who are already members of the group
  const currentMemberIds = props.group.members?.map(m => m.user_id) || []
  
  return usersStore.users.filter(user => 
    !currentMemberIds.includes(user.id) &&
    (user.username.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
     user.email.toLowerCase().includes(searchQuery.value.toLowerCase()))
  ).slice(0, 10) // Limit to 10 results
})

const availableRoles = computed(() => [
  { value: GROUP_ROLES.MEMBER, label: 'Member' },
  { value: GROUP_ROLES.MODERATOR, label: 'Moderator' },
  { value: GROUP_ROLES.ADMIN, label: 'Admin' }
])

// Methods
async function handleSearch() {
  if (searchQuery.value.trim().length >= 2) {
    // Fetch users if needed
    if (usersStore.users.length === 0) {
      await usersStore.fetchUsers()
    }
  }
}

function toggleUser(user: User) {
  const index = selectedUsers.value.findIndex(u => u.id === user.id)
  if (index >= 0) {
    selectedUsers.value.splice(index, 1)
  } else {
    selectedUsers.value.push(user)
  }
}

function removeUser(user: User) {
  const index = selectedUsers.value.findIndex(u => u.id === user.id)
  if (index >= 0) {
    selectedUsers.value.splice(index, 1)
  }
}

async function handleSubmit() {
  if (selectedUsers.value.length === 0) {
    error.value = 'Please select at least one user'
    return
  }

  loading.value = true
  error.value = null

  try {
    const membershipRequest: GroupMembershipRequest = {
      user_ids: selectedUsers.value.map(u => u.id),
      role_in_group: selectedRole.value
    }

    const result = await groupsStore.addUsersToGroup(props.group.id, membershipRequest)

    if (result) {
      emit('added')
    } else {
      error.value = groupsStore.error || 'Failed to add members'
    }
  } catch (err: any) {
    error.value = err.message || 'An unexpected error occurred'
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(async () => {
  // Load users for search
  if (usersStore.users.length === 0) {
    await usersStore.fetchUsers()
  }
})
</script>
