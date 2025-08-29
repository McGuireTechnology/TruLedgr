import type { Role, Permission, UserPermissions, PermissionCheck } from './types';
export declare const authorizationApi: {
    getRoles: () => Promise<Role[]>;
    createRole: (roleData: {
        name: string;
        description?: string;
    }) => Promise<Role>;
    updateRole: (roleId: string, roleData: Partial<Role>) => Promise<Role>;
    deleteRole: (roleId: string) => Promise<void>;
    getPermissions: () => Promise<Permission[]>;
    assignPermissionToRole: (roleId: string, permissionId: string) => Promise<void>;
    removePermissionFromRole: (roleId: string, permissionId: string) => Promise<void>;
    assignRoleToUser: (userId: string, roleId: string) => Promise<void>;
    removeRoleFromUser: (userId: string, roleId: string) => Promise<void>;
    getUserPermissions: (userId: string) => Promise<UserPermissions>;
    checkPermission: (check: PermissionCheck) => Promise<boolean>;
};
