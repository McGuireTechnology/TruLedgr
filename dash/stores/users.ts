import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { usersApi, type User, type UserCreate, type UserUpdate, type UserSearchParams, type UserStats } from '@/services/users'

export const useUsersStore = defineStore('users', () => {
  const users = ref<User[]>([])
  const currentUser = ref<User | null>(null)
  const userStats = ref<UserStats | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const searchQuery = ref('')
  const currentPage = ref(1)
  const pageSize = ref(10)
  const totalUsers = ref(0)
  const filters = ref<UserSearchParams>({
    is_active: undefined,
    is_verified: undefined,
    role_id: undefined,
    include_deleted: false,
  })

  // Computed properties
  const activeUsers = computed(() => users.value.filter(user => user.is_active && !user.is_deleted))
  const inactiveUsers = computed(() => users.value.filter(user => !user.is_active || user.is_deleted))
  const verifiedUsers = computed(() => users.value.filter(user => user.is_verified))
  const unverifiedUsers = computed(() => users.value.filter(user => !user.is_verified))
  const totalPages = computed(() => Math.ceil(totalUsers.value / pageSize.value))

  // Fetch users with pagination and filtering
  const fetchUsers = async (force = false) => {
    if (loading.value || (!force && users.value.length > 0)) {
      return users.value
    }

    loading.value = true
    error.value = null

    try {
      const params: UserSearchParams = {
        skip: (currentPage.value - 1) * pageSize.value,
        limit: pageSize.value,
        search: searchQuery.value || undefined,
        ...filters.value,
      }

      const response = await usersApi.getUsers(params)
      users.value = response.users  // Changed from response.items to response.users
      totalUsers.value = response.total
      return response.users  // Changed from response.items to response.users
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch users'
      error.value = errorMessage
      throw err
    } finally {
      loading.value = false
    }
  }

  // Fetch user statistics
  const fetchUserStats = async () => {
    try {
      const stats = await usersApi.getUserStats()
      userStats.value = stats
      return stats
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch user statistics'
      error.value = errorMessage
      throw err
    }
  }

  // Get single user
  const fetchUser = async (userId: string, includeDeleted = false) => {
    loading.value = true
    error.value = null

    try {
      const user = await usersApi.getUser(userId, includeDeleted)
      
      // Update user in the list if it exists
      const index = users.value.findIndex(u => u.id === userId)
      if (index !== -1) {
        users.value[index] = user
      }
      
      return user
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch user'
      error.value = errorMessage
      throw err
    } finally {
      loading.value = false
    }
  }

  // Create new user
  const createUser = async (userData: UserCreate) => {
    loading.value = true
    error.value = null

    try {
      const newUser = await usersApi.createUser(userData)
      users.value.unshift(newUser)
      totalUsers.value += 1
      return newUser
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create user'
      error.value = errorMessage
      throw err
    } finally {
      loading.value = false
    }
  }

  // Update user
  const updateUser = async (userId: string, userData: UserUpdate) => {
    loading.value = true
    error.value = null

    try {
      const updatedUser = await usersApi.updateUser(userId, userData)
      
      const index = users.value.findIndex(user => user.id === userId)
      if (index !== -1) {
        users.value[index] = updatedUser
      }
      
      return updatedUser
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update user'
      error.value = errorMessage
      throw err
    } finally {
      loading.value = false
    }
  }

  // Delete user
  const deleteUser = async (userId: string, hardDelete = false) => {
    loading.value = true
    error.value = null

    try {
      await usersApi.deleteUser(userId, hardDelete)
      
      if (hardDelete) {
        // Remove from list
        users.value = users.value.filter(user => user.id !== userId)
        totalUsers.value -= 1
      } else {
        // Mark as deleted
        const index = users.value.findIndex(user => user.id === userId)
        if (index !== -1) {
          users.value[index] = { ...users.value[index], is_deleted: true, is_active: false }
        }
      }
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete user'
      error.value = errorMessage
      throw err
    } finally {
      loading.value = false
    }
  }

  // Restore user
  const restoreUser = async (userId: string) => {
    loading.value = true
    error.value = null

    try {
      const restoredUser = await usersApi.restoreUser(userId)
      
      const index = users.value.findIndex(user => user.id === userId)
      if (index !== -1) {
        users.value[index] = restoredUser
      }
      
      return restoredUser
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to restore user'
      error.value = errorMessage
      throw err
    } finally {
      loading.value = false
    }
  }

  // Activate user
  const activateUser = async (userId: string) => {
    loading.value = true
    error.value = null

    try {
      const activatedUser = await usersApi.activateUser(userId)
      
      const index = users.value.findIndex(user => user.id === userId)
      if (index !== -1) {
        users.value[index] = activatedUser
      }
      
      return activatedUser
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to activate user'
      error.value = errorMessage
      throw err
    } finally {
      loading.value = false
    }
  }

  // Deactivate user
  const deactivateUser = async (userId: string) => {
    loading.value = true
    error.value = null

    try {
      const deactivatedUser = await usersApi.deactivateUser(userId)
      
      const index = users.value.findIndex(user => user.id === userId)
      if (index !== -1) {
        users.value[index] = deactivatedUser
      }
      
      return deactivatedUser
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to deactivate user'
      error.value = errorMessage
      throw err
    } finally {
      loading.value = false
    }
  }

  // Verify user email
  const verifyUserEmail = async (userId: string) => {
    loading.value = true
    error.value = null

    try {
      const verifiedUser = await usersApi.verifyUserEmail(userId)
      
      const index = users.value.findIndex(user => user.id === userId)
      if (index !== -1) {
        users.value[index] = verifiedUser
      }
      
      return verifiedUser
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to verify user email'
      error.value = errorMessage
      throw err
    } finally {
      loading.value = false
    }
  }

  // Search users
  const searchUsers = async (query: string) => {
    searchQuery.value = query
    currentPage.value = 1
    await fetchUsers(true)
  }

  // Set filters
  const setFilters = async (newFilters: Partial<UserSearchParams>) => {
    filters.value = { ...filters.value, ...newFilters }
    currentPage.value = 1
    await fetchUsers(true)
  }

  // Set page
  const setPage = async (page: number) => {
    currentPage.value = page
    await fetchUsers(true)
  }

  // Set page size
  const setPageSize = async (size: number) => {
    pageSize.value = size
    currentPage.value = 1
    await fetchUsers(true)
  }

  // Clear error
  const clearError = () => {
    error.value = null
  }

  // Reset store
  const reset = () => {
    users.value = []
    currentUser.value = null
    userStats.value = null
    loading.value = false
    error.value = null
    searchQuery.value = ''
    currentPage.value = 1
    totalUsers.value = 0
    filters.value = {
      is_active: undefined,
      is_verified: undefined,
      role_id: undefined,
      include_deleted: false,
    }
  }

  return {
    // State
    users,
    currentUser,
    userStats,
    loading,
    error,
    searchQuery,
    currentPage,
    pageSize,
    totalUsers,
    filters,
    
    // Computed
    activeUsers,
    inactiveUsers,
    verifiedUsers,
    unverifiedUsers,
    totalPages,
    
    // Actions
    fetchUsers,
    fetchUserStats,
    fetchUser,
    createUser,
    updateUser,
    deleteUser,
    restoreUser,
    activateUser,
    deactivateUser,
    verifyUserEmail,
    searchUsers,
    setFilters,
    setPage,
    setPageSize,
    clearError,
    reset,
  }
})
