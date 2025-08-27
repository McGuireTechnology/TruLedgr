import { apiClient } from '@/shared/api'
import type { Role, Permission, UserPermissions, PermissionCheck } from './types'

export const authorizationApi = {
  // Role management
  getRoles: async (): Promise<Role[]> => {
    const response = await apiClient.get<Role[]>('/roles')
    return response.data
  },

  createRole: async (roleData: { name: string; description?: string }): Promise<Role> => {
    const response = await apiClient.post<Role>('/roles', roleData)
    return response.data
  },

  updateRole: async (roleId: string, roleData: Partial<Role>): Promise<Role> => {
    const response = await apiClient.put<Role>(`/roles/${roleId}`, roleData)
    return response.data
  },

  deleteRole: async (roleId: string): Promise<void> => {
    await apiClient.delete(`/roles/${roleId}`)
  },

  // Permission management
  getPermissions: async (): Promise<Permission[]> => {
    const response = await apiClient.get<Permission[]>('/permissions')
    return response.data
  },

  // Role-Permission management
  assignPermissionToRole: async (roleId: string, permissionId: string): Promise<void> => {
    await apiClient.post(`/roles/${roleId}/permissions/${permissionId}`)
  },

  removePermissionFromRole: async (roleId: string, permissionId: string): Promise<void> => {
    await apiClient.delete(`/roles/${roleId}/permissions/${permissionId}`)
  },

  // User-Role management
  assignRoleToUser: async (userId: string, roleId: string): Promise<void> => {
    await apiClient.post(`/users/${userId}/roles/${roleId}`)
  },

  removeRoleFromUser: async (userId: string, roleId: string): Promise<void> => {
    await apiClient.delete(`/users/${userId}/roles/${roleId}`)
  },

  // Permission checking
  getUserPermissions: async (userId: string): Promise<UserPermissions> => {
    const response = await apiClient.get<UserPermissions>(`/users/${userId}/permissions`)
    return response.data
  },

  checkPermission: async (check: PermissionCheck): Promise<boolean> => {
    const response = await apiClient.post<{ allowed: boolean }>('/permissions/check', check)
    return response.data.allowed
  },
}
