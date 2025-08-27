import { apiClient } from './api'
import type { User, UserCreate, UserUpdate, UserStats, PaginatedResponse } from '@/types'

// User public profile interface for public endpoints
export interface UserPublic {
  id: string
  username: string
  first_name?: string
  last_name?: string
  profile_picture_url?: string
  bio?: string
}

// User search/filter parameters
export interface UserSearchParams {
  skip?: number
  limit?: number
  include_deleted?: boolean
  is_active?: boolean
  is_verified?: boolean
  role_id?: string
  search?: string
}

// Password change interface
export interface PasswordChangeData {
  current_password: string
  new_password: string
}

export const usersApi = {
  // Get paginated list of users with filtering
  getUsers: async (params: UserSearchParams = {}): Promise<PaginatedResponse<User>> => {
    const searchParams = new URLSearchParams()
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, value.toString())
      }
    })
    
    const response = await apiClient.get<PaginatedResponse<User>>(`/users?${searchParams.toString()}`)
    return response.data
  },

  // Search users by query string
  searchUsers: async (query: string, limit = 50, includeDeleted = false): Promise<UserPublic[]> => {
    const params = new URLSearchParams({
      q: query,
      limit: limit.toString(),
      include_deleted: includeDeleted.toString(),
    })
    
    const response = await apiClient.get<UserPublic[]>(`/users/search?${params.toString()}`)
    return response.data
  },

  // Get user statistics
  getUserStats: async (): Promise<UserStats> => {
    const response = await apiClient.get<UserStats>('/users/stats')
    return response.data
  },

  // Get single user by ID
  getUser: async (userId: string, includeDeleted = false): Promise<User> => {
    const params = includeDeleted ? '?include_deleted=true' : ''
    const response = await apiClient.get<User>(`/users/${userId}${params}`)
    return response.data
  },

  // Get user's public profile
  getUserPublicProfile: async (userId: string): Promise<UserPublic> => {
    const response = await apiClient.get<UserPublic>(`/users/${userId}/public`)
    return response.data
  },

  // Create new user
  createUser: async (userData: UserCreate): Promise<User> => {
    const response = await apiClient.post<User>('/users', userData)
    return response.data
  },

  // Update user
  updateUser: async (userId: string, userData: UserUpdate): Promise<User> => {
    const response = await apiClient.put<User>(`/users/${userId}`, userData)
    return response.data
  },

  // Delete user (soft delete by default)
  deleteUser: async (userId: string, hardDelete = false): Promise<{ message: string }> => {
    const params = hardDelete ? '?hard_delete=true' : ''
    const response = await apiClient.delete<{ message: string }>(`/users/${userId}${params}`)
    return response.data
  },

  // Restore soft-deleted user
  restoreUser: async (userId: string): Promise<User> => {
    const response = await apiClient.post<User>(`/users/${userId}/restore`)
    return response.data
  },

  // Activate user account
  activateUser: async (userId: string): Promise<User> => {
    const response = await apiClient.post<User>(`/users/${userId}/activate`)
    return response.data
  },

  // Deactivate user account
  deactivateUser: async (userId: string): Promise<User> => {
    const response = await apiClient.post<User>(`/users/${userId}/deactivate`)
    return response.data
  },

  // Verify user email
  verifyUserEmail: async (userId: string): Promise<User> => {
    const response = await apiClient.post<User>(`/users/${userId}/verify-email`)
    return response.data
  },

  // Current user profile management
  getCurrentUserProfile: async (): Promise<User> => {
    const response = await apiClient.get<User>('/users/me')
    return response.data
  },

  // Update current user profile
  updateCurrentUserProfile: async (userData: UserUpdate): Promise<User> => {
    const response = await apiClient.put<User>('/users/me', userData)
    return response.data
  },

  // Change current user password
  changeCurrentUserPassword: async (passwordData: PasswordChangeData): Promise<{ message: string }> => {
    const response = await apiClient.post<{ message: string }>('/users/me/change-password', passwordData)
    return response.data
  },
}
