import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/services/api'
import { isTokenExpired } from '@/utils/jwt'
import type { User, LoginCredentials, UserCreate } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('auth_token'))
  const user = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const initialized = ref(false) // Track if auth has been initialized

  const isAuthenticated = computed(() => !!token.value && !!user.value)

  const login = async (credentials: LoginCredentials) => {
    loading.value = true
    error.value = null
    
    try {
      // Create URL-encoded form data for OAuth2PasswordRequestForm
      const formData = new URLSearchParams()
      formData.append('username', credentials.username)
      formData.append('password', credentials.password)
      
      const response = await apiClient.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      })
      
      token.value = response.data.access_token
      localStorage.setItem('auth_token', token.value!)
      
      // Set the token for future requests
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
      
      // Fetch user profile
      await fetchProfile()
      
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Login failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('auth_token')
    delete apiClient.defaults.headers.common['Authorization']
  }

  const fetchProfile = async () => {
    if (!token.value) return
    
    try {
      const response = await apiClient.get('/auth/me')
      user.value = response.data
    } catch (err) {
      console.error('Failed to fetch profile:', err)
      logout()
    }
  }

  const checkAuth = async () => {
    if (token.value) {
      // Check if token is expired
      if (isTokenExpired(token.value)) {
        console.log('Token is expired, logging out')
        logout()
        initialized.value = true
        return
      }

      apiClient.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
      try {
        await fetchProfile()
      } catch (error) {
        console.error('Auth check failed:', error)
        // If token is invalid, clear it
        logout()
      }
    }
    initialized.value = true
  }

  const register = async (userData: UserCreate) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.post('/auth/register', userData)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Registration failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateProfile = async (userData: Partial<User>) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.put('/auth/me', userData)
      user.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Profile update failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  const changePassword = async (currentPassword: string, newPassword: string) => {
    loading.value = true
    error.value = null
    
    try {
      await apiClient.post('/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword
      })
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Password change failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    token,
    user,
    loading,
    error,
    initialized,
    isAuthenticated,
    login,
    logout,
    fetchProfile,
    checkAuth,
    register,
    updateProfile,
    changePassword,
  }
})
