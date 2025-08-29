import axios from 'axios';
import { useAuthStore } from '@/stores/auth';
const baseURL = import.meta.env.VITE_API_BASE_URL || '/api';
export const apiClient = axios.create({
    baseURL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
});
// Request interceptor to add auth token
apiClient.interceptors.request.use((config) => {
    const authStore = useAuthStore();
    if (authStore.token) {
        config.headers.Authorization = `Bearer ${authStore.token}`;
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});
// Response interceptor to handle errors
apiClient.interceptors.response.use((response) => response, (error) => {
    if (error.response?.status === 401) {
        const authStore = useAuthStore();
        authStore.logout();
        window.location.href = '/login';
    }
    return Promise.reject(error);
});
export default apiClient;
