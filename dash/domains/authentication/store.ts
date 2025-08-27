import { defineStore } from 'pinia'
import { ref, computed, readonly } from 'vue'
import { authApi, type LoginCredentials, type AuthUser } from './api'
import { setAuthToken, getAuthToken } from '@/shared/api'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<AuthUser | null>(null)
  const token = ref<string | null>(getAuthToken())
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userDisplayName = computed(() => {
    if (!user.value) return ''
    if (user.value.first_name && user.value.last_name) {
      return `${user.value.first_name} ${user.value.last_name}`
    }
    return user.value.username
  })

  // Actions
  const login = async (credentials: LoginCredentials) => {
    loading.value = true
    error.value = null

    try {
      const response = await authApi.login(credentials)
      
      // Store token and user
      token.value = response.access_token
      user.value = response.user as AuthUser
      
      // Update API client
      setAuthToken(response.access_token)
      
      return response
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Login failed'
      error.value = errorMessage
      throw new Error(errorMessage)
    } finally {
      loading.value = false
    }
  }

  const logout = async (allSessions = false) => {
    loading.value = true
    error.value = null

    try {
      if (token.value) {
        await authApi.logout(allSessions)
      }
    } catch (err) {
      console.warn('Logout API call failed:', err)
    } finally {
      // Clear local state regardless of API success
      user.value = null
      token.value = null
      setAuthToken(null)
      loading.value = false
    }
  }

  const fetchUser = async () => {
    if (!token.value) return null

    loading.value = true
    error.value = null

    try {
      const userData = await authApi.me()
      user.value = userData
      return userData
    } catch (err: unknown) {
      const errorMessage = err instanceof Error 
        ? err.message
        : (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Failed to fetch user'
      error.value = errorMessage
      
      // If user fetch fails with 401, token is invalid
      if ((err as { response?: { status?: number } })?.response?.status === 401) {
        await logout()
      }
      
      throw new Error(errorMessage)
    } finally {
      loading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  const initialize = async () => {
    if (token.value) {
      try {
        await fetchUser()
      } catch (err) {
        console.warn('Failed to initialize user:', err)
      }
    }
  }

  // Return store interface
  return {
    // State
    user: readonly(user),
    token: readonly(token),
    loading: readonly(loading),
    error: readonly(error),
    
    // Computed
    isAuthenticated,
    userDisplayName,
    
    // Actions
    login,
    logout,
    fetchUser,
    clearError,
    initialize,
  }
})
