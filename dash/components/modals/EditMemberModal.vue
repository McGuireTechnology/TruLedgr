<!-- Edit Member Modal -->
<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
      <div class="mt-3">
        <!-- Header -->
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium text-gray-900">
            Edit Member: {{ member.user?.username || 'Unknown' }}
          </h3>
          <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Member Info -->
        <div class="mb-4 p-3 bg-gray-50 rounded-md">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center">
              <span class="text-sm font-medium text-gray-700">
                {{ member.user?.username?.charAt(0).toUpperCase() || '?' }}
              </span>
            </div>
            <div>
              <p class="font-medium text-gray-900">{{ member.user?.username || 'Unknown' }}</p>
              <p class="text-sm text-gray-500">{{ member.user?.email || '' }}</p>
              <p class="text-xs text-gray-400">
                Joined {{ formatDate(member.joined_at) }}
              </p>
            </div>
          </div>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <!-- Role Selection -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Role in Group</label>
            <select
              v-model="form.role_in_group"
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option v-for="role in availableRoles" :key="role.value" :value="role.value">
                {{ role.label }}
              </option>
            </select>
          </div>

          <!-- Membership Status -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Membership Status</label>
            <div class="space-y-2">
              <label class="flex items-center">
                <input
                  v-model="form.is_active"
                  type="radio"
                  :value="true"
                  class="form-radio text-indigo-600"
                />
                <span class="ml-2 text-sm text-gray-700">Active</span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="form.is_active"
                  type="radio"
                  :value="false"
                  class="form-radio text-indigo-600"
                />
                <span class="ml-2 text-sm text-gray-700">Inactive</span>
              </label>
            </div>
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
              :disabled="loading"
              class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="loading">Updating...</span>
              <span v-else>Update Member</span>
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
import { GROUP_ROLES } from '@/domains/groups'
import type { Group, UserInGroup, GroupMembershipUpdate } from '@/types'

// Props
const props = defineProps<{
  group: Group
  member: UserInGroup
}>()

// Emits
const emit = defineEmits<{
  close: []
  updated: []
}>()

// Store
const groupsStore = useGroupsStore()

// Form state
const form = ref<GroupMembershipUpdate>({
  role_in_group: props.member.role_in_group,
  is_active: props.member.is_active
})

// UI state
const loading = ref(false)
const error = ref<string | null>(null)

// Computed
const availableRoles = computed(() => {
  // Owner can assign any role except owner
  // Admin can assign member, moderator roles
  // For now, show all available roles
  const roles = [
    { value: GROUP_ROLES.MEMBER, label: 'Member' },
    { value: GROUP_ROLES.MODERATOR, label: 'Moderator' },
    { value: GROUP_ROLES.ADMIN, label: 'Admin' }
  ]

  // Don't allow changing owner role
  if (props.member.role_in_group === GROUP_ROLES.OWNER) {
    roles.unshift({ value: GROUP_ROLES.OWNER, label: 'Owner' })
  }

  return roles
})

// Methods
function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString()
}

async function handleSubmit() {
  loading.value = true
  error.value = null

  try {
    const result = await groupsStore.updateUserMembership(
      props.group.id,
      props.member.user_id,
      form.value
    )

    if (result) {
      emit('updated')
    } else {
      error.value = groupsStore.error || 'Failed to update member'
    }
  } catch (err: any) {
    error.value = err.message || 'An unexpected error occurred'
  } finally {
    loading.value = false
  }
}

// Initialize form with current member data
onMounted(() => {
  form.value = {
    role_in_group: props.member.role_in_group,
    is_active: props.member.is_active
  }
})
</script>

<style scoped>
.form-radio {
  @apply focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300;
}
</style>
