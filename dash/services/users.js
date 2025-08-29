import { apiClient } from './api';
export const usersApi = {
    // Get paginated list of users with filtering
    getUsers: async (params = {}) => {
        const searchParams = new URLSearchParams();
        Object.entries(params).forEach(([key, value]) => {
            if (value !== undefined && value !== null) {
                searchParams.append(key, value.toString());
            }
        });
        const response = await apiClient.get(`/users?${searchParams.toString()}`);
        return response.data;
    },
    // Search users by query string
    searchUsers: async (query, limit = 50, includeDeleted = false) => {
        const params = new URLSearchParams({
            q: query,
            limit: limit.toString(),
            include_deleted: includeDeleted.toString(),
        });
        const response = await apiClient.get(`/users/search?${params.toString()}`);
        return response.data;
    },
    // Get user statistics
    getUserStats: async () => {
        const response = await apiClient.get('/users/stats');
        return response.data;
    },
    // Get single user by ID
    getUser: async (userId, includeDeleted = false) => {
        const params = includeDeleted ? '?include_deleted=true' : '';
        const response = await apiClient.get(`/users/${userId}${params}`);
        return response.data;
    },
    // Get user's public profile
    getUserPublicProfile: async (userId) => {
        const response = await apiClient.get(`/users/${userId}/public`);
        return response.data;
    },
    // Create new user
    createUser: async (userData) => {
        const response = await apiClient.post('/users', userData);
        return response.data;
    },
    // Update user
    updateUser: async (userId, userData) => {
        const response = await apiClient.put(`/users/${userId}`, userData);
        return response.data;
    },
    // Delete user (soft delete by default)
    deleteUser: async (userId, hardDelete = false) => {
        const params = hardDelete ? '?hard_delete=true' : '';
        const response = await apiClient.delete(`/users/${userId}${params}`);
        return response.data;
    },
    // Restore soft-deleted user
    restoreUser: async (userId) => {
        const response = await apiClient.post(`/users/${userId}/restore`);
        return response.data;
    },
    // Activate user account
    activateUser: async (userId) => {
        const response = await apiClient.post(`/users/${userId}/activate`);
        return response.data;
    },
    // Deactivate user account
    deactivateUser: async (userId) => {
        const response = await apiClient.post(`/users/${userId}/deactivate`);
        return response.data;
    },
    // Verify user email
    verifyUserEmail: async (userId) => {
        const response = await apiClient.post(`/users/${userId}/verify-email`);
        return response.data;
    },
    // Current user profile management
    getCurrentUserProfile: async () => {
        const response = await apiClient.get('/users/me');
        return response.data;
    },
    // Update current user profile
    updateCurrentUserProfile: async (userData) => {
        const response = await apiClient.put('/users/me', userData);
        return response.data;
    },
    // Change current user password
    changeCurrentUserPassword: async (passwordData) => {
        const response = await apiClient.post('/users/me/change-password', passwordData);
        return response.data;
    },
};
