export interface Role {
  id: string
  name: string
  description?: string
  permissions: Permission[]
  created_at?: string
  updated_at?: string
}

export interface Permission {
  id: string
  name: string
  description?: string
  resource: string
  action: string
  created_at?: string
}

export interface RoleAssignment {
  user_id: string
  role_id: string
  assigned_at: string
  assigned_by: string
}

export interface PermissionCheck {
  resource: string
  action: string
  user_id?: string
}

export interface UserPermissions {
  user_id: string
  permissions: string[]
  roles: Role[]
}
