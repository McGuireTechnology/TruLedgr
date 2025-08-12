import axios, {
  type AxiosInstance,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from 'axios'

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://api.truledgr.app'

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('auth_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: unknown) => {
    return Promise.reject(error)
  },
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: unknown) => {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

// API Types
export interface User {
  id: number
  email: string
  full_name?: string
  is_active: boolean
}

export interface UserCreate {
  email: string
  password: string
  full_name?: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface HealthCheck {
  status: string
  message: string
  version: string
}

export interface MobileConfig {
  api_version: string
  min_app_version: string
  force_update: boolean
  maintenance_mode: boolean
  features: {
    biometric_auth: boolean
    push_notifications: boolean
    offline_mode: boolean
  }
}

// API Functions
export const api = {
  // Health check
  async healthCheck(): Promise<HealthCheck> {
    const response = await apiClient.get<HealthCheck>('/health')
    return response.data
  },

  // Authentication
  async register(userData: UserCreate): Promise<User> {
    const response = await apiClient.post<User>('/auth/register', userData)
    return response.data
  },

  async login(credentials: { email: string; password: string }): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>('/auth/login', credentials)

    // Store token in localStorage
    if (response.data.access_token) {
      localStorage.setItem('auth_token', response.data.access_token)
    }

    return response.data
  },

  async logout(): Promise<void> {
    localStorage.removeItem('auth_token')
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/users/me')
    return response.data
  },

  // Mobile config (useful for feature flags)
  async getMobileConfig(): Promise<MobileConfig> {
    const response = await apiClient.get<MobileConfig>('/mobile/config')
    return response.data
  },
}

export default apiClient
