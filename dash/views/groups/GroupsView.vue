<!-- Groups List View -->
<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">Groups</h1>
        <p class="mt-1 text-sm text-gray-500">
          Manage and organize users into groups for better collaboration.
        </p>
      </div>
      <button
        @click="showCreateGroup = true"
        class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium"
      >
        Create Group
      </button>
    </div>

    <!-- Filters -->
    <div class="bg-white shadow rounded-lg p-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <!-- Search -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search groups..."
            class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
            @input="handleSearch"
          />
        </div>

        <!-- Group Type Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Type</label>
          <select
            v-model="selectedType"
            class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
            @change="handleTypeFilter"
          >
            <option value="">All Types</option>
            <option v-for="type in groupTypes" :key="type.value" :value="type.value">
              {{ type.label }}
            </option>
          </select>
        </div>

        <!-- Visibility Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Visibility</label>
          <select
            v-model="selectedVisibility"
            class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
            @change="handleVisibilityFilter"
          >
            <option value="">All Groups</option>
            <option value="public">Public</option>
            <option value="private">Private</option>
            <option value="my-groups">My Groups</option>
          </select>
        </div>

        <!-- Sort -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Sort By</label>
          <select
            v-model="sortBy"
            class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
            @change="handleSort"
          >
            <option value="created_at">Created Date</option>
            <option value="name">Name</option>
            <option value="member_count">Member Count</option>
            <option value="updated_at">Last Updated</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Groups Grid -->
    <div v-if="groupsStore.isLoading" class="text-center py-8">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      <p class="mt-2 text-sm text-gray-500">Loading groups...</p>
    </div>

    <div v-else-if="groupsStore.error" class="bg-red-50 border border-red-200 rounded-md p-4">
      <p class="text-red-800">{{ groupsStore.error }}</p>
      <button
        @click="loadGroups"
        class="mt-2 text-red-600 hover:text-red-800 text-sm underline"
      >
        Try again
      </button>
    </div>

    <div v-else-if="!groupsStore.hasGroups" class="text-center py-12">
      <svg
        class="mx-auto h-12 w-12 text-gray-400"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
        />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">No groups</h3>
      <p class="mt-1 text-sm text-gray-500">Get started by creating a new group.</p>
      <div class="mt-6">
        <button
          @click="showCreateGroup = true"
          class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium"
        >
          Create Group
        </button>
      </div>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="group in groupsStore.groups"
        :key="group.id"
        class="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow duration-200"
      >
        <div class="p-6">
          <!-- Group Header -->
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center space-x-3">
              <div
                class="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center"
                :class="`bg-${getGroupBadgeColor(group.group_type)}-100`"
              >
                <svg
                  class="w-5 h-5"
                  :class="`text-${getGroupBadgeColor(group.group_type)}-600`"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z"
                  />
                </svg>
              </div>
              <div>
                <h3 class="text-lg font-medium text-gray-900">{{ group.name }}</h3>
                <span
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  :class="`bg-${getGroupBadgeColor(group.group_type)}-100 text-${getGroupBadgeColor(group.group_type)}-800`"
                >
                  {{ formatGroupType(group.group_type) }}
                </span>
              </div>
            </div>
            
            <!-- Visibility Badge -->
            <span
              class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
              :class="group.is_public ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'"
            >
              {{ group.is_public ? 'Public' : 'Private' }}
            </span>
          </div>

          <!-- Description -->
          <p class="text-sm text-gray-600 mb-4 line-clamp-2">
            {{ group.description || 'No description provided.' }}
          </p>

          <!-- Stats -->
          <div class="flex items-center justify-between text-sm text-gray-500 mb-4">
            <span>{{ group.member_count }} members</span>
            <span>{{ formatDate(group.created_at) }}</span>
          </div>

          <!-- Actions -->
          <div class="flex space-x-2">
            <button
              @click="viewGroup(group)"
              class="flex-1 bg-indigo-50 text-indigo-700 hover:bg-indigo-100 px-3 py-2 rounded-md text-sm font-medium"
            >
              View
            </button>
            <button
              v-if="canEditGroup(group)"
              @click="editGroup(group)"
              class="flex-1 bg-gray-50 text-gray-700 hover:bg-gray-100 px-3 py-2 rounded-md text-sm font-medium"
            >
              Edit
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="groupsStore.pagination.totalPages > 1" class="flex justify-center">
      <nav class="flex items-center space-x-2">
        <button
          :disabled="groupsStore.pagination.page === 1"
          @click="changePage(groupsStore.pagination.page - 1)"
          class="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Previous
        </button>
        
        <span class="px-4 py-2 text-sm text-gray-700">
          Page {{ groupsStore.pagination.page }} of {{ groupsStore.pagination.totalPages }}
        </span>
        
        <button
          :disabled="groupsStore.pagination.page === groupsStore.pagination.totalPages"
          @click="changePage(groupsStore.pagination.page + 1)"
          class="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Next
        </button>
      </nav>
    </div>

    <!-- Create Group Modal -->
    <CreateGroupModal
      v-if="showCreateGroup"
      @close="showCreateGroup = false"
      @created="handleGroupCreated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useGroupsStore } from '@/stores/groups'
import { useAuthStore } from '@/stores/auth'
import { 
  GROUP_TYPES, 
  formatGroupType, 
  getGroupBadgeColor 
} from '@/domains/groups'
import CreateGroupModal from '@/components/modals/CreateGroupModal.vue'
import type { Group } from '@/types'

const router = useRouter()
const groupsStore = useGroupsStore()

// Reactive state
const showCreateGroup = ref(false)
const searchQuery = ref('')
const selectedType = ref('')
const selectedVisibility = ref('')
const sortBy = ref('created_at')

// Computed properties
const groupTypes = computed(() => [
  { value: GROUP_TYPES.GENERAL, label: 'General' },
  { value: GROUP_TYPES.DEPARTMENT, label: 'Department' },
  { value: GROUP_TYPES.PROJECT, label: 'Project' },
  { value: GROUP_TYPES.TEAM, label: 'Team' },
  { value: GROUP_TYPES.COMMUNITY, label: 'Community' }
])

// Methods
async function loadGroups() {
  await groupsStore.fetchGroups(true)
}

function handleSearch() {
  groupsStore.setSearch(searchQuery.value)
  loadGroups()
}

function handleTypeFilter() {
  groupsStore.setGroupType(selectedType.value || null)
  loadGroups()
}

function handleVisibilityFilter() {
  let isPublic = null
  if (selectedVisibility.value === 'public') isPublic = true
  if (selectedVisibility.value === 'private') isPublic = false
  
  groupsStore.setIsPublic(isPublic)
  loadGroups()
}

function handleSort() {
  groupsStore.setOrderBy(sortBy.value)
  loadGroups()
}

function changePage(page: number) {
  groupsStore.setPage(page)
  loadGroups()
}

function viewGroup(group: Group) {
  router.push(`/groups/${group.id}`)
}

function editGroup(group: Group) {
  router.push(`/groups/${group.id}/edit`)
}

function canEditGroup(group: Group): boolean {
  // TODO: Implement proper permission checking
  // For now, just check if user is owner
  return group.owner_id === getCurrentUserId()
}

function getCurrentUserId(): string | null {
  // Get from auth store
  const authStore = useAuthStore()
  return authStore.user?.id || null
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString()
}

async function handleGroupCreated(group: Group) {
  showCreateGroup.value = false
  await loadGroups()
  // Optionally navigate to the new group
  router.push(`/groups/${group.id}`)
}

// Lifecycle
onMounted(() => {
  loadGroups()
})
</script>

<style scoped>
.line-clamp-2 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}
</style>
