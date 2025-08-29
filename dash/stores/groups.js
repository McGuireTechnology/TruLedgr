/**
 * Groups store for managing group data and operations.
 *
 * This store provides state management for groups including:
 * - Group listing and filtering
 * - Group creation, updating, and deletion
 * - Group membership management
 * - User group associations
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { apiClient } from '@/services/api';
import { useAuthStore } from '@/stores/auth';
export const useGroupsStore = defineStore('groups', () => {
    // State
    const groups = ref([]);
    const currentGroup = ref(null);
    const loading = ref(false);
    const error = ref(null);
    const pagination = ref({
        page: 1,
        size: 20,
        total: 0,
        totalPages: 0
    });
    const filters = ref({
        search: '',
        groupType: null,
        isPublic: null,
        ownerId: null,
        orderBy: 'created_at',
        orderDirection: 'desc'
    });
    // Getters
    const publicGroups = computed(() => groups.value?.filter(group => group.is_public) || []);
    const userGroups = computed(() => groups.value?.filter(group => group.owner_id === getCurrentUserId()) || []);
    const memberGroups = computed(() => groups.value?.filter(group => group.members?.some(member => member.user_id === getCurrentUserId())) || []);
    const hasGroups = computed(() => groups.value?.length > 0);
    const isLoading = computed(() => loading.value);
    // Helper to get current user ID (would come from auth store)
    function getCurrentUserId() {
        // Get from auth store
        const authStore = useAuthStore();
        return authStore.user?.id || null;
    }
    // Actions
    async function fetchGroups(resetPagination = false) {
        try {
            loading.value = true;
            error.value = null;
            if (resetPagination) {
                pagination.value.page = 1;
            }
            const params = new URLSearchParams({
                page: pagination.value.page.toString(),
                size: pagination.value.size.toString(),
                order_by: filters.value.orderBy,
                order_direction: filters.value.orderDirection,
                ...(filters.value.search && { search: filters.value.search }),
                ...(filters.value.groupType && { group_type: filters.value.groupType }),
                ...(filters.value.isPublic !== null && { is_public: filters.value.isPublic.toString() }),
                ...(filters.value.ownerId && { owner_id: filters.value.ownerId })
            });
            const response = await apiClient.get(`/groups?${params}`);
            groups.value = response.items;
            pagination.value.total = response.total;
            pagination.value.totalPages = response.total_pages;
        }
        catch (err) {
            error.value = err.response?.data?.detail || 'Failed to fetch groups';
            console.error('Error fetching groups:', err);
        }
        finally {
            loading.value = false;
        }
    }
    async function fetchGroup(groupId, includeMembers = false) {
        try {
            loading.value = true;
            error.value = null;
            const params = includeMembers ? '?include_members=true' : '';
            const response = await apiClient.get(`/groups/${groupId}${params}`);
            currentGroup.value = response;
            // Update the group in the list if it exists
            const index = groups.value.findIndex(g => g.id === groupId);
            if (index !== -1) {
                groups.value[index] = { ...groups.value[index], ...response };
            }
        }
        catch (err) {
            error.value = err.response?.data?.detail || 'Failed to fetch group';
            console.error('Error fetching group:', err);
        }
        finally {
            loading.value = false;
        }
    }
    async function fetchGroupBySlug(slug, includeMembers = false) {
        try {
            loading.value = true;
            error.value = null;
            const params = includeMembers ? '?include_members=true' : '';
            const response = await apiClient.get(`/groups/slug/${slug}${params}`);
            currentGroup.value = response;
        }
        catch (err) {
            error.value = err.response?.data?.detail || 'Failed to fetch group by slug';
            console.error('Error fetching group by slug:', err);
        }
        finally {
            loading.value = false;
        }
    }
    async function createGroup(groupData) {
        try {
            loading.value = true;
            error.value = null;
            const response = await apiClient.post('/groups', groupData);
            // Add to the beginning of the list
            groups.value.unshift(response);
            return response;
        }
        catch (err) {
            error.value = err.response?.data?.detail || 'Failed to create group';
            console.error('Error creating group:', err);
            return null;
        }
        finally {
            loading.value = false;
        }
    }
    async function updateGroup(groupId, groupData) {
        try {
            loading.value = true;
            error.value = null;
            const response = await apiClient.put(`/groups/${groupId}`, groupData);
            // Update in the list
            const index = groups.value.findIndex(g => g.id === groupId);
            if (index !== -1) {
                groups.value[index] = response;
            }
            // Update current group if it's the same
            if (currentGroup.value?.id === groupId) {
                currentGroup.value = { ...currentGroup.value, ...response };
            }
            return response;
        }
        catch (err) {
            error.value = err.response?.data?.detail || 'Failed to update group';
            console.error('Error updating group:', err);
            return null;
        }
        finally {
            loading.value = false;
        }
    }
    async function deleteGroup(groupId) {
        try {
            loading.value = true;
            error.value = null;
            await apiClient.delete(`/groups/${groupId}`);
            // Remove from the list
            groups.value = groups.value.filter(g => g.id !== groupId);
            // Clear current group if it's the deleted one
            if (currentGroup.value?.id === groupId) {
                currentGroup.value = null;
            }
            return true;
        }
        catch (err) {
            error.value = err.response?.data?.detail || 'Failed to delete group';
            console.error('Error deleting group:', err);
            return false;
        }
        finally {
            loading.value = false;
        }
    }
    async function addUsersToGroup(groupId, membershipRequest) {
        try {
            loading.value = true;
            error.value = null;
            const response = await apiClient.post(`/groups/${groupId}/members`, membershipRequest);
            // Update current group members if it's the same group
            if (currentGroup.value?.id === groupId && currentGroup.value.members) {
                currentGroup.value.members.push(...response);
            }
            return response;
        }
        catch (err) {
            error.value = err.response?.data?.detail || 'Failed to add users to group';
            console.error('Error adding users to group:', err);
            return null;
        }
        finally {
            loading.value = false;
        }
    }
    async function removeUserFromGroup(groupId, userId) {
        try {
            loading.value = true;
            error.value = null;
            await apiClient.delete(`/groups/${groupId}/members/${userId}`);
            // Update current group members if it's the same group
            if (currentGroup.value?.id === groupId && currentGroup.value.members) {
                currentGroup.value.members = currentGroup.value.members.filter(m => m.user_id !== userId);
            }
            return true;
        }
        catch (err) {
            error.value = err.response?.data?.detail || 'Failed to remove user from group';
            console.error('Error removing user from group:', err);
            return false;
        }
        finally {
            loading.value = false;
        }
    }
    async function updateUserMembership(groupId, userId, membershipData) {
        try {
            loading.value = true;
            error.value = null;
            const response = await apiClient.put(`/groups/${groupId}/members/${userId}`, membershipData);
            // Update current group member if it's the same group
            if (currentGroup.value?.id === groupId && currentGroup.value.members) {
                const index = currentGroup.value.members.findIndex(m => m.user_id === userId);
                if (index !== -1) {
                    currentGroup.value.members[index] = response;
                }
            }
            return response;
        }
        catch (err) {
            error.value = err.response?.data?.detail || 'Failed to update user membership';
            console.error('Error updating user membership:', err);
            return null;
        }
        finally {
            loading.value = false;
        }
    }
    // Filter and pagination actions
    function setSearch(search) {
        filters.value.search = search;
    }
    function setGroupType(groupType) {
        filters.value.groupType = groupType;
    }
    function setIsPublic(isPublic) {
        filters.value.isPublic = isPublic;
    }
    function setOwnerId(ownerId) {
        filters.value.ownerId = ownerId;
    }
    function setOrderBy(orderBy, orderDirection = 'desc') {
        filters.value.orderBy = orderBy;
        filters.value.orderDirection = orderDirection;
    }
    function setPage(page) {
        pagination.value.page = page;
    }
    function setPageSize(size) {
        pagination.value.size = size;
        pagination.value.page = 1; // Reset to first page
    }
    function resetFilters() {
        filters.value = {
            search: '',
            groupType: null,
            isPublic: null,
            ownerId: null,
            orderBy: 'created_at',
            orderDirection: 'desc'
        };
        pagination.value.page = 1;
    }
    function clearError() {
        error.value = null;
    }
    function clearCurrentGroup() {
        currentGroup.value = null;
    }
    return {
        // State
        groups,
        currentGroup,
        loading,
        error,
        pagination,
        filters,
        // Getters
        publicGroups,
        userGroups,
        memberGroups,
        hasGroups,
        isLoading,
        // Actions
        fetchGroups,
        fetchGroup,
        fetchGroupBySlug,
        createGroup,
        updateGroup,
        deleteGroup,
        addUsersToGroup,
        removeUserFromGroup,
        updateUserMembership,
        // Filter and pagination
        setSearch,
        setGroupType,
        setIsPublic,
        setOwnerId,
        setOrderBy,
        setPage,
        setPageSize,
        resetFilters,
        // Utilities
        clearError,
        clearCurrentGroup
    };
});
