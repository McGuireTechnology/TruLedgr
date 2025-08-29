import { apiClient } from '@/shared/api';
export const authApi = {
    // Login with username/email and password
    login: async (credentials) => {
        const formData = new FormData();
        formData.append('username', credentials.username);
        formData.append('password', credentials.password);
        const response = await apiClient.post('/auth/login', formData, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        });
        return response.data;
    },
    // Logout (revoke session)
    logout: async (allSessions = false) => {
        await apiClient.post('/auth/logout', { all_sessions: allSessions });
    },
    // Get current user info
    me: async () => {
        const response = await apiClient.get('/auth/me');
        return response.data;
    },
    // Refresh session/token
    refresh: async () => {
        const response = await apiClient.post('/auth/refresh');
        return response.data;
    },
    // Register new user (if registration is enabled)
    register: async (userData) => {
        const response = await apiClient.post('/auth/register', userData);
        return response.data;
    },
};
