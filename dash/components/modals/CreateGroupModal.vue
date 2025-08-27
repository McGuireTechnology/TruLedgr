<!-- Create Group Modal -->
<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
      <div class="mt-3">
        <!-- Header -->
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium text-gray-900">Create New Group</h3>
          <button
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <!-- Group Name -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Group Name *
            </label>
            <input
              v-model="form.name"
              type="text"
              required
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Enter group name"
              :class="{ 'border-red-500': errors.name }"
            />
            <p v-if="errors.name" class="mt-1 text-sm text-red-600">{{ errors.name }}</p>
          </div>

          <!-- Description -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              v-model="form.description"
              rows="3"
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Describe the purpose of this group"
              :class="{ 'border-red-500': errors.description }"
            />
            <p v-if="errors.description" class="mt-1 text-sm text-red-600">{{ errors.description }}</p>
          </div>

          <!-- Group Type -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Group Type
            </label>
            <select
              v-model="form.group_type"
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option v-for="type in groupTypes" :key="type.value" :value="type.value">
                {{ type.label }}
              </option>
            </select>
          </div>

          <!-- Settings Row -->
          <div class="grid grid-cols-2 gap-4">
            <!-- Visibility -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Visibility
              </label>
              <div class="space-y-2">
                <label class="flex items-center">
                  <input
                    v-model="form.is_public"
                    type="radio"
                    :value="true"
                    class="form-radio text-indigo-600"
                  />
                  <span class="ml-2 text-sm text-gray-700">Public</span>
                </label>
                <label class="flex items-center">
                  <input
                    v-model="form.is_public"
                    type="radio"
                    :value="false"
                    class="form-radio text-indigo-600"
                  />
                  <span class="ml-2 text-sm text-gray-700">Private</span>
                </label>
              </div>
            </div>

            <!-- Join Settings -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Join Settings
              </label>
              <div class="space-y-2">
                <label class="flex items-center">
                  <input
                    v-model="form.is_open"
                    type="radio"
                    :value="true"
                    class="form-radio text-indigo-600"
                  />
                  <span class="ml-2 text-sm text-gray-700">Open</span>
                </label>
                <label class="flex items-center">
                  <input
                    v-model="form.is_open"
                    type="radio"
                    :value="false"
                    class="form-radio text-indigo-600"
                  />
                  <span class="ml-2 text-sm text-gray-700">Invite Only</span>
                </label>
              </div>
            </div>
          </div>

          <!-- Max Members -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Maximum Members (optional)
            </label>
            <input
              v-model.number="form.max_members"
              type="number"
              min="1"
              max="10000"
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Leave empty for unlimited"
            />
          </div>

          <!-- Tags -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Tags (comma-separated)
            </label>
            <input
              v-model="form.tags"
              type="text"
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="e.g., development, team, project"
            />
          </div>

          <!-- Error Message -->
          <div v-if="submitError" class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md p-3">
            {{ submitError }}
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
              <span v-if="loading">Creating...</span>
              <span v-else>Create Group</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useGroupsStore } from '@/stores/groups'
import { GROUP_TYPES, validateGroupName, validateGroupDescription } from '@/domains/groups'
import type { GroupCreate, Group } from '@/types'

// Emits
const emit = defineEmits<{
  close: []
  created: [group: Group]
}>()

// Store
const groupsStore = useGroupsStore()

// Form state
const form = ref<GroupCreate & { max_members?: number | null }>({
  name: '',
  description: '',
  is_public: true,
  is_open: false,
  group_type: GROUP_TYPES.GENERAL,
  tags: '',
  max_members: null
})

// UI state
const loading = ref(false)
const submitError = ref<string | null>(null)
const errors = ref<Record<string, string>>({})

// Computed
const groupTypes = computed(() => [
  { value: GROUP_TYPES.GENERAL, label: 'General' },
  { value: GROUP_TYPES.DEPARTMENT, label: 'Department' },
  { value: GROUP_TYPES.PROJECT, label: 'Project' },
  { value: GROUP_TYPES.TEAM, label: 'Team' },
  { value: GROUP_TYPES.COMMUNITY, label: 'Community' }
])

// Validation
function validateForm(): boolean {
  errors.value = {}

  if (!form.value.name?.trim()) {
    errors.value.name = 'Group name is required'
    return false
  }

  if (!validateGroupName(form.value.name)) {
    errors.value.name = 'Group name must be 3-100 characters and contain only letters, numbers, spaces, hyphens, and underscores'
    return false
  }

  if (form.value.description && !validateGroupDescription(form.value.description)) {
    errors.value.description = 'Description must be 500 characters or less'
    return false
  }

  return true
}

// Form submission
async function handleSubmit() {
  if (!validateForm()) {
    return
  }

  loading.value = true
  submitError.value = null

  try {
    // Prepare form data
    const groupData: GroupCreate = {
      name: form.value.name.trim(),
      description: form.value.description?.trim() || undefined,
      is_public: form.value.is_public,
      is_open: form.value.is_open,
      group_type: form.value.group_type,
      tags: form.value.tags?.trim() || undefined,
      max_members: form.value.max_members || undefined
    }

    // Create group
    const createdGroup = await groupsStore.createGroup(groupData)

    if (createdGroup) {
      emit('created', createdGroup)
    } else {
      submitError.value = groupsStore.error || 'Failed to create group'
    }
  } catch (error: any) {
    submitError.value = error.message || 'An unexpected error occurred'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.form-radio {
  @apply focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300;
}
</style>
