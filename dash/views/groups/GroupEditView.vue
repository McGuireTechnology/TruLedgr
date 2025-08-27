<!-- Group Edit View -->
<template>
  <div class="space-y-6">
    <!-- Loading State -->
    <div v-if="groupsStore.isLoading" class="text-center py-8">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      <p class="mt-2 text-sm text-gray-500">Loading group...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="groupsStore.error" class="bg-red-50 border border-red-200 rounded-md p-4">
      <p class="text-red-800">{{ groupsStore.error }}</p>
      <button @click="loadGroup" class="mt-2 text-red-600 hover:text-red-800 text-sm underline">
        Try again
      </button>
    </div>

    <!-- Group Edit Content -->
    <div v-else-if="group">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-semibold text-gray-900">Edit Group</h1>
          <p class="mt-1 text-sm text-gray-500">
            Update settings and configuration for {{ group.name }}
          </p>
        </div>
        <div class="flex space-x-3">
          <router-link
            :to="`/groups/${group.id}`"
            class="bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-2 rounded-md text-sm font-medium"
          >
            Cancel
          </router-link>
        </div>
      </div>

      <!-- Group Settings Component -->
      <GroupSettings :group="group" @updated="handleGroupUpdated" />
    </div>

    <!-- Not Found State -->
    <div v-else class="text-center py-12">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">Group not found</h3>
      <p class="mt-1 text-sm text-gray-500">The group you're looking for doesn't exist or you don't have permission to view it.</p>
      <div class="mt-6">
        <router-link
          to="/groups"
          class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium"
        >
          Back to Groups
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGroupsStore } from '@/stores/groups'
import GroupSettings from '@/components/groups/GroupSettings.vue'
import type { Group } from '@/types'

const route = useRoute()
const router = useRouter()
const groupsStore = useGroupsStore()

// Computed properties
const group = computed(() => groupsStore.currentGroup)

// Methods
async function loadGroup() {
  const groupId = route.params.id as string
  await groupsStore.fetchGroup(groupId, false)
}

function handleGroupUpdated(updatedGroup: Group) {
  // Group has been updated, we could show a success message or redirect
  // For now, just update the current group in the store
  groupsStore.currentGroup = { ...groupsStore.currentGroup!, ...updatedGroup }
}

// Lifecycle
onMounted(() => {
  loadGroup()
})
</script>
