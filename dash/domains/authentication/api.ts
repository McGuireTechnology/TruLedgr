import { apiClient } from '@/shared/api'

export interface LoginCredentials {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: {
    id: string
    username: string
    email: string
  }
  session_id: string
  totp_enabled: boolean
}

export interface AuthUser {
  id: string
  username: string
  email: string
  first_name?: string
  last_name?: string
  is_active: boolean
  is_verified: boolean
  email_verified: boolean
  last_login?: string
  created_at?: string
  role_id?: string
}

export const authApi = {
  // Login with username/email and password
  login: async (credentials: LoginCredentials): Promise<LoginResponse> => {
    const formData = new FormData()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)
    
    const response = await apiClient.post<LoginResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  },

  // Logout (revoke session)
  logout: async (allSessions = false): Promise<void> => {
    await apiClient.post('/auth/logout', { all_sessions: allSessions })
  },

  // Get current user info
  me: async (): Promise<AuthUser> => {
    const response = await apiClient.get<AuthUser>('/auth/me')
    return response.data
  },

  // Refresh session/token
  refresh: async (): Promise<LoginResponse> => {
    const response = await apiClient.post<LoginResponse>('/auth/refresh')
    return response.data
  },

  // Register new user (if registration is enabled)
  register: async (userData: {
    username: string
    email: string
    password: string
    first_name?: string
    last_name?: string
  }): Promise<{ message: string; user_id: string }> => {
    const response = await apiClient.post('/auth/register', userData)
    return response.data
  },
}
