import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { apiClient } from '@/services/api';
export const useRolesStore = defineStore('roles', () => {
    const roles = ref([]);
    const permissions = ref([]);
    const loading = ref(false);
    const error = ref(null);
    // Computed
    const activeRoles = computed(() => roles.value.filter((role) => role.is_active));
    const systemRoles = computed(() => roles.value.filter((role) => role.is_system));
    const customRoles = computed(() => roles.value.filter((role) => !role.is_system));
    // Actions
    const fetchRoles = async () => {
        loading.value = true;
        error.value = null;
        try {
            const response = await apiClient.get('/authorization/roles');
            roles.value = response.data;
        }
        catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to fetch roles';
            throw err;
        }
        finally {
            loading.value = false;
        }
    };
    const fetchPermissions = async () => {
        loading.value = true;
        error.value = null;
        try {
            const response = await apiClient.get('/authorization/permissions');
            permissions.value = response.data;
        }
        catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to fetch permissions';
            throw err;
        }
        finally {
            loading.value = false;
        }
    };
    const createRole = async (roleData) => {
        loading.value = true;
        error.value = null;
        try {
            const response = await apiClient.post('/authorization/roles', roleData);
            const newRole = response.data;
            roles.value.push(newRole);
            return newRole;
        }
        catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to create role';
            throw err;
        }
        finally {
            loading.value = false;
        }
    };
    const updateRole = async (roleId, roleData) => {
        loading.value = true;
        error.value = null;
        try {
            const response = await apiClient.put(`/authorization/roles/${roleId}`, roleData);
            const updatedRole = response.data;
            const index = roles.value.findIndex((role) => role.id === roleId);
            if (index !== -1) {
                roles.value[index] = updatedRole;
            }
            return updatedRole;
        }
        catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to update role';
            throw err;
        }
        finally {
            loading.value = false;
        }
    };
    const deleteRole = async (roleId) => {
        loading.value = true;
        error.value = null;
        try {
            await apiClient.delete(`/authorization/roles/${roleId}`);
            roles.value = roles.value.filter((role) => role.id !== roleId);
        }
        catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to delete role';
            throw err;
        }
        finally {
            loading.value = false;
        }
    };
    const assignPermissions = async (roleId, permissionIds) => {
        loading.value = true;
        error.value = null;
        try {
            await apiClient.post(`/authorization/roles/${roleId}/permissions`, {
                permission_ids: permissionIds,
            });
            await fetchRoles(); // Refresh to get updated permissions
        }
        catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to assign permissions';
            throw err;
        }
        finally {
            loading.value = false;
        }
    };
    const removePermissions = async (roleId, permissionIds) => {
        loading.value = true;
        error.value = null;
        try {
            await apiClient.delete(`/authorization/roles/${roleId}/permissions`, {
                data: { permission_ids: permissionIds },
            });
            await fetchRoles(); // Refresh to get updated permissions
        }
        catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to remove permissions';
            throw err;
        }
        finally {
            loading.value = false;
        }
    };
    const getRoleById = (roleId) => {
        return roles.value.find((role) => role.id === roleId);
    };
    const getPermissionById = (permissionId) => {
        return permissions.value.find((permission) => permission.id === permissionId);
    };
    return {
        // State
        roles,
        permissions,
        loading,
        error,
        // Computed
        activeRoles,
        systemRoles,
        customRoles,
        // Actions
        fetchRoles,
        fetchPermissions,
        createRole,
        updateRole,
        deleteRole,
        assignPermissions,
        removePermissions,
        getRoleById,
        getPermissionById,
    };
});
