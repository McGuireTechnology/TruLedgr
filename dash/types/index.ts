export interface User {
  id: string
  username: string
  email: string
  first_name?: string
  last_name?: string
  bio?: string
  profile_picture_url?: string
  is_active: boolean
  is_verified: boolean
  email_verified: boolean
  last_login?: string
  created_at?: string
  updated_at?: string
  role_id?: string
  is_oauth_user: boolean
  oauth_provider?: string
}

export interface UserCreate {
  username: string
  email: string
  password: string
  first_name?: string
  last_name?: string
  bio?: string
  role_id?: string
}

export interface UserUpdate {
  username?: string
  email?: string
  first_name?: string
  last_name?: string
  bio?: string
  password?: string
  role_id?: string
  is_active?: boolean
  is_verified?: boolean
}

export interface LoginCredentials {
  username: string
  password: string
}

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
  updated_at?: string
}

export interface Item {
  id: number
  name: string
  description?: string
  is_active: boolean
}

export interface ItemCreate {
  name: string
  description?: string
}

export interface ItemUpdate {
  name?: string
  description?: string
  is_active?: boolean
}

export interface PaginatedResponse<T> {
  users: T[]  // Changed from "items" to match backend response
  total: number
  skip: number  // Changed from "page" to match backend
  limit: number  // Changed from "size" to match backend
  has_more: boolean  // Added to match backend
}

export interface ApiError {
  detail: string
  status_code: number
}

export interface UserStats {
  total_users: number
  active_users: number
  inactive_users: number
  verified_users: number
  unverified_users: number
  oauth_users: number
  regular_users: number
  deleted_users: number
  activation_rate: number
  verification_rate: number
  oauth_adoption_rate: number
}

export interface DashboardStats {
  users: UserStats
  recent_logins: User[]
  recent_registrations: User[]
  system_health: {
    status: 'healthy' | 'warning' | 'error'
    cpu_usage: number
    memory_usage: number
    disk_usage: number
  }
}

// Groups Types
export interface Group {
  id: string
  name: string
  slug: string
  description?: string
  is_public: boolean
  is_open: boolean
  group_type: string
  tags?: string
  max_members?: number
  member_count: number
  owner_id: string
  owner?: User
  created_at: string
  updated_at: string
  is_deleted: boolean
  metadata?: Record<string, any>
}

export interface GroupCreate {
  name: string
  description?: string
  is_public?: boolean
  is_open?: boolean
  group_type?: string
  tags?: string
  max_members?: number
  metadata?: Record<string, any>
}

export interface GroupUpdate {
  name?: string
  description?: string
  is_public?: boolean
  is_open?: boolean
  group_type?: string
  tags?: string
  max_members?: number
  metadata?: Record<string, any>
}

export interface UserInGroup {
  user_id: string
  group_id: string
  role_in_group: string
  joined_at: string
  is_active: boolean
  metadata?: Record<string, any>
  user?: User
}

export interface GroupWithMembers extends Group {
  members?: UserInGroup[]
}

export interface GroupMembershipRequest {
  user_ids: string[]
  role_in_group?: string
}

export interface GroupMembershipUpdate {
  role_in_group?: string
  is_active?: boolean
  metadata?: Record<string, any>
}

export interface GroupListResponse {
  items: Group[]
  total: number
  page: number
  size: number
  total_pages: number
}
