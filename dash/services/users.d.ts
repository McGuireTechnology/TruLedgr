import type { User, UserCreate, UserUpdate, UserStats, PaginatedResponse } from '@/types';
export interface UserPublic {
    id: string;
    username: string;
    first_name?: string;
    last_name?: string;
    profile_picture_url?: string;
    bio?: string;
}
export interface UserSearchParams {
    skip?: number;
    limit?: number;
    include_deleted?: boolean;
    is_active?: boolean;
    is_verified?: boolean;
    role_id?: string;
    search?: string;
}
export interface PasswordChangeData {
    current_password: string;
    new_password: string;
}
export declare const usersApi: {
    getUsers: (params?: UserSearchParams) => Promise<PaginatedResponse<User>>;
    searchUsers: (query: string, limit?: number, includeDeleted?: boolean) => Promise<UserPublic[]>;
    getUserStats: () => Promise<UserStats>;
    getUser: (userId: string, includeDeleted?: boolean) => Promise<User>;
    getUserPublicProfile: (userId: string) => Promise<UserPublic>;
    createUser: (userData: UserCreate) => Promise<User>;
    updateUser: (userId: string, userData: UserUpdate) => Promise<User>;
    deleteUser: (userId: string, hardDelete?: boolean) => Promise<{
        message: string;
    }>;
    restoreUser: (userId: string) => Promise<User>;
    activateUser: (userId: string) => Promise<User>;
    deactivateUser: (userId: string) => Promise<User>;
    verifyUserEmail: (userId: string) => Promise<User>;
    getCurrentUserProfile: () => Promise<User>;
    updateCurrentUserProfile: (userData: UserUpdate) => Promise<User>;
    changeCurrentUserPassword: (passwordData: PasswordChangeData) => Promise<{
        message: string;
    }>;
};
