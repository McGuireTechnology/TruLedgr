import type { User, UserCreate, UserUpdate, UserSearchParams, UserStats, UsersPaginatedResponse } from './types';
export declare const usersApi: {
    getUsers: (params?: UserSearchParams) => Promise<UsersPaginatedResponse>;
    getUserStats: () => Promise<UserStats>;
    getUser: (userId: string, includeDeleted?: boolean) => Promise<User>;
    createUser: (userData: UserCreate) => Promise<User>;
    updateUser: (userId: string, userData: UserUpdate) => Promise<User>;
    deleteUser: (userId: string, permanent?: boolean) => Promise<void>;
    setUserActive: (userId: string, isActive: boolean) => Promise<User>;
    verifyUser: (userId: string) => Promise<User>;
    searchUsers: (query: string, limit?: number) => Promise<User[]>;
    changeUserPassword: (userId: string, newPassword: string) => Promise<void>;
};
