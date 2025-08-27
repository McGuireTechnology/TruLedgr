<!-- Group Detail View -->
<template>
  <div class="space-y-6">
    <!-- Loading State -->
    <div v-if="groupsStore.isLoading" class="text-center py-8">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      <p class="mt-2 text-sm text-gray-500">Loading group details...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="groupsStore.error" class="bg-red-50 border border-red-200 rounded-md p-4">
      <p class="text-red-800">{{ groupsStore.error }}</p>
      <button
        @click="loadGroup"
        class="mt-2 text-red-600 hover:text-red-800 text-sm underline"
      >
        Try again
      </button>
    </div>

    <!-- Group Content -->
    <div v-else-if="group" class="space-y-6">
      <!-- Header -->
      <div class="bg-white shadow rounded-lg">
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
              <div
                class="w-12 h-12 rounded-full flex items-center justify-center"
                :class="`bg-${getGroupBadgeColor(group.group_type)}-100`"
              >
                <svg
                  class="w-6 h-6"
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
                <h1 class="text-2xl font-bold text-gray-900">{{ group.name }}</h1>
                <div class="flex items-center space-x-2 mt-1">
                  <span
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="`bg-${getGroupBadgeColor(group.group_type)}-100 text-${getGroupBadgeColor(group.group_type)}-800`"
                  >
                    {{ formatGroupType(group.group_type) }}
                  </span>
                  <span
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="group.is_public ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'"
                  >
                    {{ group.is_public ? 'Public' : 'Private' }}
                  </span>
                  <span
                    v-if="group.is_open"
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                  >
                    Open to Join
                  </span>
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex space-x-2">
              <button
                v-if="canJoinGroup"
                @click="joinGroup"
                class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Join Group
              </button>
              <button
                v-if="canLeaveGroup"
                @click="leaveGroup"
                class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Leave Group
              </button>
              <button
                v-if="canEditGroup"
                @click="editGroup"
                class="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Edit Group
              </button>
            </div>
          </div>
        </div>

        <!-- Description and Info -->
        <div class="px-6 py-4 space-y-4">
          <div v-if="group.description">
            <h3 class="text-sm font-medium text-gray-900 mb-2">Description</h3>
            <p class="text-gray-700">{{ group.description }}</p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <span class="font-medium text-gray-500">Created:</span>
              <span class="ml-2 text-gray-900">{{ formatDate(group.created_at) }}</span>
            </div>
            <div>
              <span class="font-medium text-gray-500">Members:</span>
              <span class="ml-2 text-gray-900">
                {{ group.member_count }}
                <span v-if="group.max_members">/ {{ group.max_members }}</span>
              </span>
            </div>
            <div v-if="group.owner">
              <span class="font-medium text-gray-500">Owner:</span>
              <span class="ml-2 text-gray-900">{{ group.owner.username }}</span>
            </div>
          </div>

          <div v-if="group.tags" class="flex flex-wrap gap-2">
            <span
              v-for="tag in group.tags.split(',')"
              :key="tag.trim()"
              class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
            >
              {{ tag.trim() }}
            </span>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="bg-white shadow rounded-lg">
        <div class="border-b border-gray-200">
          <nav class="-mb-px flex space-x-8 px-6">
            <button
              @click="activeTab = 'members'"
              :class="[
                'py-4 px-1 border-b-2 font-medium text-sm',
                activeTab === 'members'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              ]"
            >
              Members ({{ group.member_count }})
            </button>
            <button
              v-if="canViewSettings"
              @click="activeTab = 'settings'"
              :class="[
                'py-4 px-1 border-b-2 font-medium text-sm',
                activeTab === 'settings'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              ]"
            >
              Settings
            </button>
          </nav>
        </div>

        <!-- Tab Content -->
        <div class="p-6">
          <!-- Members Tab -->
          <div v-if="activeTab === 'members'" class="space-y-4">
            <!-- Add Members Button -->
            <div v-if="canAddMembers" class="flex justify-end">
              <button
                @click="showAddMembers = true"
                class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Add Members
              </button>
            </div>

            <!-- Members List -->
            <div v-if="group.members && group.members.length > 0" class="space-y-2">
              <div
                v-for="member in group.members"
                :key="member.user_id"
                class="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
              >
                <div class="flex items-center space-x-3">
                  <div class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                    <span class="text-sm font-medium text-gray-700">
                      {{ member.user?.username?.charAt(0).toUpperCase() || '?' }}
                    </span>
                  </div>
                  <div>
                    <p class="font-medium text-gray-900">{{ member.user?.username || 'Unknown' }}</p>
                    <p class="text-sm text-gray-500">{{ member.user?.email || '' }}</p>
                  </div>
                </div>

                <div class="flex items-center space-x-2">
                  <span
                    class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                    :class="`bg-${getRoleBadgeColor(member.role_in_group)}-100 text-${getRoleBadgeColor(member.role_in_group)}-800`"
                  >
                    {{ formatGroupRole(member.role_in_group) }}
                  </span>
                  
                  <div v-if="canManageMembers" class="flex space-x-1">
                    <button
                      @click="editMember(member)"
                      class="text-indigo-600 hover:text-indigo-900 text-sm"
                    >
                      Edit
                    </button>
                    <button
                      v-if="member.user_id !== group.owner_id"
                      @click="removeMember(member)"
                      class="text-red-600 hover:text-red-900 text-sm"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="text-center py-8 text-gray-500">
              <p>No members found.</p>
            </div>
          </div>

          <!-- Settings Tab -->
          <div v-if="activeTab === 'settings' && canViewSettings">
            <GroupSettings :group="group" @updated="handleGroupUpdated" />
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <AddMembersModal
      v-if="showAddMembers"
      :group="group"
      @close="showAddMembers = false"
      @added="handleMembersAdded"
    />

    <EditMemberModal
      v-if="showEditMember && selectedMember"
      :group="group"
      :member="selectedMember"
      @close="showEditMember = false"
      @updated="handleMemberUpdated"
    />

    <ConfirmModal
      v-if="showRemoveMember && selectedMember"
      title="Remove Member"
      :message="`Are you sure you want to remove ${selectedMember.user?.username} from this group?`"
      confirm-text="Remove"
      @confirm="confirmRemoveMember"
      @cancel="showRemoveMember = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGroupsStore } from '@/stores/groups'
import { 
  formatGroupType, 
  formatGroupRole,
  getGroupBadgeColor,
  getRoleBadgeColor,
  getUserRoleInGroup,
  isUserMemberOfGroup,
  canUserJoinGroup,
  getRolePermissions,
  GROUP_ROLES
} from '@/domains/groups'
import GroupSettings from '@/components/groups/GroupSettings.vue'
import AddMembersModal from '@/components/modals/AddMembersModal.vue'
import EditMemberModal from '@/components/modals/EditMemberModal.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'
import type { Group, GroupWithMembers, UserInGroup } from '@/types'

const route = useRoute()
const router = useRouter()
const groupsStore = useGroupsStore()

// Reactive state
const activeTab = ref('members')
const showAddMembers = ref(false)
const showEditMember = ref(false)
const showRemoveMember = ref(false)
const selectedMember = ref<UserInGroup | null>(null)

// Computed properties
const group = computed(() => groupsStore.currentGroup)

const currentUserId = computed(() => getCurrentUserId())

const userRole = computed(() => {
  if (!group.value || !currentUserId.value) return null
  return getUserRoleInGroup(group.value, currentUserId.value)
})

const rolePermissions = computed(() => {
  if (!userRole.value) return getRolePermissions('')
  return getRolePermissions(userRole.value)
})

const canEditGroup = computed(() => rolePermissions.value.canEditGroup)
const canAddMembers = computed(() => rolePermissions.value.canAddMembers)
const canManageMembers = computed(() => rolePermissions.value.canManageRoles || rolePermissions.value.canRemoveMembers)
const canViewSettings = computed(() => canEditGroup.value)

const canJoinGroup = computed(() => {
  if (!group.value || !currentUserId.value) return false
  if (isUserMemberOfGroup(group.value, currentUserId.value)) return false
  return canUserJoinGroup(group.value, currentUserId.value)
})

const canLeaveGroup = computed(() => {
  if (!group.value || !currentUserId.value) return false
  if (group.value.owner_id === currentUserId.value) return false // Owner cannot leave
  return isUserMemberOfGroup(group.value, currentUserId.value)
})

// Methods
async function loadGroup() {
  const groupId = route.params.id as string
  await groupsStore.fetchGroup(groupId, true)
}

function getCurrentUserId(): string | null {
  // TODO: Get from auth store
  return null
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString()
}

function editGroup() {
  router.push(`/groups/${group.value?.id}/edit`)
}

async function joinGroup() {
  if (!group.value || !currentUserId.value) return
  
  // TODO: Implement join group functionality
  console.log('Joining group:', group.value.id)
}

async function leaveGroup() {
  if (!group.value || !currentUserId.value) return
  
  const success = await groupsStore.removeUserFromGroup(group.value.id, currentUserId.value)
  if (success) {
    router.push('/groups')
  }
}

function editMember(member: UserInGroup) {
  selectedMember.value = member
  showEditMember.value = true
}

function removeMember(member: UserInGroup) {
  selectedMember.value = member
  showRemoveMember.value = true
}

async function confirmRemoveMember() {
  if (!group.value || !selectedMember.value) return
  
  const success = await groupsStore.removeUserFromGroup(
    group.value.id, 
    selectedMember.value.user_id
  )
  
  if (success) {
    showRemoveMember.value = false
    selectedMember.value = null
    await loadGroup() // Reload to get updated member list
  }
}

function handleGroupUpdated(updatedGroup: Group) {
  // Update the current group in store
  groupsStore.currentGroup = { ...groupsStore.currentGroup!, ...updatedGroup }
}

function handleMembersAdded() {
  showAddMembers.value = false
  loadGroup() // Reload to get updated member list
}

function handleMemberUpdated() {
  showEditMember.value = false
  selectedMember.value = null
  loadGroup() // Reload to get updated member list
}

// Lifecycle
onMounted(() => {
  loadGroup()
})
</script>
