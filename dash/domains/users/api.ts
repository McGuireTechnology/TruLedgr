import { apiClient } from '@/shared/api'
import type { 
  User, 
  UserCreate, 
  UserUpdate, 
  UserSearchParams, 
  UserStats, 
  UsersPaginatedResponse 
} from './types'

export const usersApi = {
  // Get paginated list of users with filtering
  getUsers: async (params: UserSearchParams = {}): Promise<UsersPaginatedResponse> => {
    const searchParams = new URLSearchParams()
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, value.toString())
      }
    })
    
    const response = await apiClient.get<UsersPaginatedResponse>(`/users?${searchParams.toString()}`)
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

  // Create new user
  createUser: async (userData: UserCreate): Promise<User> => {
    const response = await apiClient.post<User>('/users', userData)
    return response.data
  },

  // Update existing user
  updateUser: async (userId: string, userData: UserUpdate): Promise<User> => {
    const response = await apiClient.put<User>(`/users/${userId}`, userData)
    return response.data
  },

  // Delete user (soft delete)
  deleteUser: async (userId: string, permanent = false): Promise<void> => {
    const params = permanent ? '?permanent=true' : ''
    await apiClient.delete(`/users/${userId}${params}`)
  },

  // Activate/deactivate user
  setUserActive: async (userId: string, isActive: boolean): Promise<User> => {
    const response = await apiClient.patch<User>(`/users/${userId}/active`, { is_active: isActive })
    return response.data
  },

  // Verify user email
  verifyUser: async (userId: string): Promise<User> => {
    const response = await apiClient.post<User>(`/users/${userId}/verify`)
    return response.data
  },

  // Search users
  searchUsers: async (query: string, limit = 50): Promise<User[]> => {
    const params = new URLSearchParams({
      q: query,
      limit: limit.toString(),
    })
    
    const response = await apiClient.get<User[]>(`/users/search?${params.toString()}`)
    return response.data
  },

  // Change user password (admin)
  changeUserPassword: async (userId: string, newPassword: string): Promise<void> => {
    await apiClient.post(`/users/${userId}/password`, { new_password: newPassword })
  },
}
