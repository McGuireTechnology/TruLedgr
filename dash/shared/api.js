import axios from 'axios';
const baseURL = import.meta.env.VITE_API_BASE_URL || '/api';
export const apiClient = axios.create({
    baseURL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
});
// Auth token management
let authToken = null;
export const setAuthToken = (token) => {
    authToken = token;
    if (token) {
        localStorage.setItem('auth_token', token);
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
    else {
        localStorage.removeItem('auth_token');
        delete apiClient.defaults.headers.common['Authorization'];
    }
};
export const getAuthToken = () => {
    if (!authToken) {
        authToken = localStorage.getItem('auth_token');
        if (authToken) {
            apiClient.defaults.headers.common['Authorization'] = `Bearer ${authToken}`;
        }
    }
    return authToken;
};
// Initialize token from localStorage on app start
getAuthToken();
// Request interceptor to ensure token is always included
apiClient.interceptors.request.use((config) => {
    const token = getAuthToken();
    if (token && !config.headers.Authorization) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});
// Response interceptor to handle auth errors
apiClient.interceptors.response.use((response) => response, (error) => {
    if (error.response?.status === 401) {
        setAuthToken(null);
        // Redirect to login - can be customized per domain
        if (typeof window !== 'undefined') {
            window.location.href = '/login';
        }
    }
    return Promise.reject(error);
});
export default apiClient;
