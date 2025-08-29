import { apiClient } from '@/shared/api';
export const authorizationApi = {
    // Role management
    getRoles: async () => {
        const response = await apiClient.get('/roles');
        return response.data;
    },
    createRole: async (roleData) => {
        const response = await apiClient.post('/roles', roleData);
        return response.data;
    },
    updateRole: async (roleId, roleData) => {
        const response = await apiClient.put(`/roles/${roleId}`, roleData);
        return response.data;
    },
    deleteRole: async (roleId) => {
        await apiClient.delete(`/roles/${roleId}`);
    },
    // Permission management
    getPermissions: async () => {
        const response = await apiClient.get('/permissions');
        return response.data;
    },
    // Role-Permission management
    assignPermissionToRole: async (roleId, permissionId) => {
        await apiClient.post(`/roles/${roleId}/permissions/${permissionId}`);
    },
    removePermissionFromRole: async (roleId, permissionId) => {
        await apiClient.delete(`/roles/${roleId}/permissions/${permissionId}`);
    },
    // User-Role management
    assignRoleToUser: async (userId, roleId) => {
        await apiClient.post(`/users/${userId}/roles/${roleId}`);
    },
    removeRoleFromUser: async (userId, roleId) => {
        await apiClient.delete(`/users/${userId}/roles/${roleId}`);
    },
    // Permission checking
    getUserPermissions: async (userId) => {
        const response = await apiClient.get(`/users/${userId}/permissions`);
        return response.data;
    },
    checkPermission: async (check) => {
        const response = await apiClient.post('/permissions/check', check);
        return response.data.allowed;
    },
};
