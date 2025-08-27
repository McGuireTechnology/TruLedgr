<!-- Group Settings Component -->
<template>
  <div class="space-y-6">
    <!-- Basic Information -->
    <div class="bg-white border border-gray-200 rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Basic Information</h3>
      
      <form @submit.prevent="handleSave" class="space-y-4">
        <!-- Group Name -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Group Name</label>
          <input
            v-model="form.name"
            type="text"
            required
            class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            :class="{ 'border-red-500': errors.name }"
          />
          <p v-if="errors.name" class="mt-1 text-sm text-red-600">{{ errors.name }}</p>
        </div>

        <!-- Description -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea
            v-model="form.description"
            rows="3"
            class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            :class="{ 'border-red-500': errors.description }"
          />
          <p v-if="errors.description" class="mt-1 text-sm text-red-600">{{ errors.description }}</p>
        </div>

        <!-- Group Type -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Group Type</label>
          <select
            v-model="form.group_type"
            class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          >
            <option v-for="type in groupTypes" :key="type.value" :value="type.value">
              {{ type.label }}
            </option>
          </select>
        </div>

        <!-- Tags -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Tags</label>
          <input
            v-model="form.tags"
            type="text"
            placeholder="Enter tags separated by commas"
            class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
          <p class="mt-1 text-xs text-gray-500">Separate tags with commas</p>
        </div>

        <!-- Save Button -->
        <div class="flex justify-end">
          <button
            type="submit"
            :disabled="loading"
            class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="loading">Saving...</span>
            <span v-else>Save Changes</span>
          </button>
        </div>
      </form>
    </div>

    <!-- Privacy & Access -->
    <div class="bg-white border border-gray-200 rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Privacy & Access</h3>
      
      <form @submit.prevent="handleSave" class="space-y-4">
        <!-- Visibility -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Group Visibility</label>
          <div class="space-y-2">
            <label class="flex items-center">
              <input
                v-model="form.is_public"
                type="radio"
                :value="true"
                class="form-radio text-indigo-600"
              />
              <span class="ml-2 text-sm text-gray-700">Public - Anyone can see this group</span>
            </label>
            <label class="flex items-center">
              <input
                v-model="form.is_public"
                type="radio"
                :value="false"
                class="form-radio text-indigo-600"
              />
              <span class="ml-2 text-sm text-gray-700">Private - Only members can see this group</span>
            </label>
          </div>
        </div>

        <!-- Join Policy -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Join Policy</label>
          <div class="space-y-2">
            <label class="flex items-center">
              <input
                v-model="form.is_open"
                type="radio"
                :value="true"
                class="form-radio text-indigo-600"
              />
              <span class="ml-2 text-sm text-gray-700">Open - Anyone can join</span>
            </label>
            <label class="flex items-center">
              <input
                v-model="form.is_open"
                type="radio"
                :value="false"
                class="form-radio text-indigo-600"
              />
              <span class="ml-2 text-sm text-gray-700">Invite Only - Members must be invited</span>
            </label>
          </div>
        </div>

        <!-- Max Members -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Maximum Members</label>
          <input
            v-model.number="form.max_members"
            type="number"
            min="1"
            max="10000"
            placeholder="Leave empty for unlimited"
            class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
          <p class="mt-1 text-xs text-gray-500">
            Current members: {{ group.member_count }}
          </p>
        </div>
      </form>
    </div>

    <!-- Danger Zone -->
    <div class="bg-white border border-red-200 rounded-lg p-6">
      <h3 class="text-lg font-medium text-red-900 mb-4">Danger Zone</h3>
      
      <div class="space-y-4">
        <div class="flex items-center justify-between p-4 border border-red-200 rounded-md">
          <div>
            <h4 class="text-sm font-medium text-gray-900">Delete Group</h4>
            <p class="text-sm text-gray-500">
              Permanently delete this group and all its data. This action cannot be undone.
            </p>
          </div>
          <button
            @click="showDeleteConfirm = true"
            class="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
          >
            Delete Group
          </button>
        </div>
      </div>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="successMessage" class="bg-green-50 border border-green-200 rounded-md p-4">
      <p class="text-green-800">{{ successMessage }}</p>
    </div>

    <div v-if="errorMessage" class="bg-red-50 border border-red-200 rounded-md p-4">
      <p class="text-red-800">{{ errorMessage }}</p>
    </div>

    <!-- Delete Confirmation Modal -->
    <ConfirmModal
      v-if="showDeleteConfirm"
      title="Delete Group"
      :message="`Are you sure you want to delete ${group.name}? This action cannot be undone.`"
      confirm-text="Delete"
      confirm-color="red"
      @confirm="handleDelete"
      @cancel="showDeleteConfirm = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGroupsStore } from '@/stores/groups'
import { GROUP_TYPES, validateGroupName, validateGroupDescription } from '@/domains/groups'
import ConfirmModal from '@/components/ConfirmModal.vue'
import type { Group, GroupUpdate } from '@/types'

// Props
const props = defineProps<{
  group: Group
}>()

// Emits
const emit = defineEmits<{
  updated: [group: Group]
}>()

// Router and store
const router = useRouter()
const groupsStore = useGroupsStore()

// Form state
const form = ref<GroupUpdate>({
  name: props.group.name,
  description: props.group.description,
  group_type: props.group.group_type,
  is_public: props.group.is_public,
  is_open: props.group.is_open,
  max_members: props.group.max_members,
  tags: props.group.tags
})

// UI state
const loading = ref(false)
const showDeleteConfirm = ref(false)
const successMessage = ref<string | null>(null)
const errorMessage = ref<string | null>(null)
const errors = ref<Record<string, string>>({})

// Computed
const groupTypes = computed(() => [
  { value: GROUP_TYPES.GENERAL, label: 'General' },
  { value: GROUP_TYPES.DEPARTMENT, label: 'Department' },
  { value: GROUP_TYPES.PROJECT, label: 'Project' },
  { value: GROUP_TYPES.TEAM, label: 'Team' },
  { value: GROUP_TYPES.COMMUNITY, label: 'Community' }
])

// Methods
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

async function handleSave() {
  if (!validateForm()) {
    return
  }

  loading.value = true
  successMessage.value = null
  errorMessage.value = null

  try {
    const updatedGroup = await groupsStore.updateGroup(props.group.id, form.value)

    if (updatedGroup) {
      successMessage.value = 'Group settings updated successfully'
      emit('updated', updatedGroup)
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        successMessage.value = null
      }, 3000)
    } else {
      errorMessage.value = groupsStore.error || 'Failed to update group'
    }
  } catch (error: any) {
    errorMessage.value = error.message || 'An unexpected error occurred'
  } finally {
    loading.value = false
  }
}

async function handleDelete() {
  loading.value = true
  errorMessage.value = null

  try {
    const success = await groupsStore.deleteGroup(props.group.id)

    if (success) {
      // Navigate back to groups list
      router.push('/groups')
    } else {
      errorMessage.value = groupsStore.error || 'Failed to delete group'
      showDeleteConfirm.value = false
    }
  } catch (error: any) {
    errorMessage.value = error.message || 'An unexpected error occurred'
    showDeleteConfirm.value = false
  } finally {
    loading.value = false
  }
}

// Initialize form with group data
onMounted(() => {
  form.value = {
    name: props.group.name,
    description: props.group.description,
    group_type: props.group.group_type,
    is_public: props.group.is_public,
    is_open: props.group.is_open,
    max_members: props.group.max_members,
    tags: props.group.tags
  }
})
</script>

<style scoped>
.form-radio {
  @apply focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300;
}
</style>
