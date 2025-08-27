import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/services/api'

export interface Role {
  id: string
  name: string
  description?: string
  is_system: boolean
  is_active: boolean
  created_at: string
  updated_at: string
  permissions: Permission[]
  user_count?: number
}

export interface Permission {
  id: string
  name: string
  description?: string
  resource: string
  action: string
  is_system: boolean
  created_at: string
  updated_at: string
}

export interface RoleCreate {
  name: string
  description?: string
  permission_ids?: string[]
}

export interface RoleUpdate {
  name?: string
  description?: string
  is_active?: boolean
  permission_ids?: string[]
}

export const useRolesStore = defineStore('roles', () => {
  const roles = ref<Role[]>([])
  const permissions = ref<Permission[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const activeRoles = computed(() => roles.value.filter((role) => role.is_active))
  const systemRoles = computed(() => roles.value.filter((role) => role.is_system))
  const customRoles = computed(() => roles.value.filter((role) => !role.is_system))

  // Actions
  const fetchRoles = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.get('/authorization/roles')
      roles.value = response.data
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch roles'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchPermissions = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.get('/authorization/permissions')
      permissions.value = response.data
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch permissions'
      throw err
    } finally {
      loading.value = false
    }
  }

  const createRole = async (roleData: RoleCreate): Promise<Role> => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.post('/authorization/roles', roleData)
      const newRole = response.data
      roles.value.push(newRole)
      return newRole
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to create role'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateRole = async (roleId: string, roleData: RoleUpdate): Promise<Role> => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.put(`/authorization/roles/${roleId}`, roleData)
      const updatedRole = response.data
      const index = roles.value.findIndex((role) => role.id === roleId)
      if (index !== -1) {
        roles.value[index] = updatedRole
      }
      return updatedRole
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to update role'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteRole = async (roleId: string): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      await apiClient.delete(`/authorization/roles/${roleId}`)
      roles.value = roles.value.filter((role) => role.id !== roleId)
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to delete role'
      throw err
    } finally {
      loading.value = false
    }
  }

  const assignPermissions = async (roleId: string, permissionIds: string[]): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      await apiClient.post(`/authorization/roles/${roleId}/permissions`, {
        permission_ids: permissionIds,
      })
      await fetchRoles() // Refresh to get updated permissions
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to assign permissions'
      throw err
    } finally {
      loading.value = false
    }
  }

  const removePermissions = async (roleId: string, permissionIds: string[]): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      await apiClient.delete(`/authorization/roles/${roleId}/permissions`, {
        data: { permission_ids: permissionIds },
      })
      await fetchRoles() // Refresh to get updated permissions
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to remove permissions'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getRoleById = (roleId: string): Role | undefined => {
    return roles.value.find((role) => role.id === roleId)
  }

  const getPermissionById = (permissionId: string): Permission | undefined => {
    return permissions.value.find((permission) => permission.id === permissionId)
  }

  return {
    // State
    roles,
    permissions,
    loading,
    error,
    
    // Computed
    activeRoles,
    systemRoles,
    customRoles,
    
    // Actions
    fetchRoles,
    fetchPermissions,
    createRole,
    updateRole,
    deleteRole,
    assignPermissions,
    removePermissions,
    getRoleById,
    getPermissionById,
  }
})
