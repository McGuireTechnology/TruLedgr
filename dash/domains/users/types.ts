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
  is_deleted?: boolean
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

export interface UserSearchParams {
  skip?: number
  limit?: number
  include_deleted?: boolean
  is_active?: boolean
  is_verified?: boolean
  role_id?: string
  search?: string
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

export interface UsersPaginatedResponse {
  users: User[]
  total: number
  skip: number
  limit: number
  has_more: boolean
}
