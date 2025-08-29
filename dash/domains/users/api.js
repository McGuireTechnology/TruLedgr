import { apiClient } from '@/shared/api';
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
    // Create new user
    createUser: async (userData) => {
        const response = await apiClient.post('/users', userData);
        return response.data;
    },
    // Update existing user
    updateUser: async (userId, userData) => {
        const response = await apiClient.put(`/users/${userId}`, userData);
        return response.data;
    },
    // Delete user (soft delete)
    deleteUser: async (userId, permanent = false) => {
        const params = permanent ? '?permanent=true' : '';
        await apiClient.delete(`/users/${userId}${params}`);
    },
    // Activate/deactivate user
    setUserActive: async (userId, isActive) => {
        const response = await apiClient.patch(`/users/${userId}/active`, { is_active: isActive });
        return response.data;
    },
    // Verify user email
    verifyUser: async (userId) => {
        const response = await apiClient.post(`/users/${userId}/verify`);
        return response.data;
    },
    // Search users
    searchUsers: async (query, limit = 50) => {
        const params = new URLSearchParams({
            q: query,
            limit: limit.toString(),
        });
        const response = await apiClient.get(`/users/search?${params.toString()}`);
        return response.data;
    },
    // Change user password (admin)
    changeUserPassword: async (userId, newPassword) => {
        await apiClient.post(`/users/${userId}/password`, { new_password: newPassword });
    },
};
