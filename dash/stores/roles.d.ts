export interface Role {
    id: string;
    name: string;
    description?: string;
    is_system: boolean;
    is_active: boolean;
    created_at: string;
    updated_at: string;
    permissions: Permission[];
    user_count?: number;
}
export interface Permission {
    id: string;
    name: string;
    description?: string;
    resource: string;
    action: string;
    is_system: boolean;
    created_at: string;
    updated_at: string;
}
export interface RoleCreate {
    name: string;
    description?: string;
    permission_ids?: string[];
}
export interface RoleUpdate {
    name?: string;
    description?: string;
    is_active?: boolean;
    permission_ids?: string[];
}
export declare const useRolesStore: import("pinia").StoreDefinition<"roles", Pick<{
    roles: import("vue").Ref<{
        id: string;
        name: string;
        description?: string | undefined;
        is_system: boolean;
        is_active: boolean;
        created_at: string;
        updated_at: string;
        permissions: {
            id: string;
            name: string;
            description?: string | undefined;
            resource: string;
            action: string;
            is_system: boolean;
            created_at: string;
            updated_at: string;
        }[];
        user_count?: number | undefined;
    }[], Role[] | {
        id: string;
        name: string;
        description?: string | undefined;
        is_system: boolean;
        is_active: boolean;
        created_at: string;
        updated_at: string;
        permissions: {
            id: string;
            name: string;
            description?: string | undefined;
            resource: string;
            action: string;
            is_system: boolean;
            created_at: string;
            updated_at: string;
        }[];
        user_count?: number | undefined;
    }[]>;
    permissions: import("vue").Ref<{
        id: string;
        name: string;
        description?: string | undefined;
        resource: string;
        action: string;
        is_system: boolean;
        created_at: string;
        updated_at: string;
    }[], Permission[] | {
        id: string;
        name: string;
        description?: string | undefined;
        resource: string;
        action: string;
        is_system: boolean;
        created_at: string;
        updated_at: string;
    }[]>;
    loading: import("vue").Ref<boolean, boolean>;
    error: import("vue").Ref<string | null, string | null>;
    activeRoles: import("vue").ComputedRef<{
        id: string;
        name: string;
        description?: string | undefined;
        is_system: boolean;
        is_active: boolean;
        created_at: string;
        updated_at: string;
        permissions: {
            id: string;
            name: string;
            description?: string | undefined;
            resource: string;
            action: string;
            is_system: boolean;
            created_at: string;
            updated_at: string;
        }[];
        user_count?: number | undefined;
    }[]>;
    systemRoles: import("vue").ComputedRef<{
        id: string;
        name: string;
        description?: string | undefined;
        is_system: boolean;
        is_active: boolean;
        created_at: string;
        updated_at: string;
        permissions: {
            id: string;
            name: string;
            description?: string | undefined;
            resource: string;
            action: string;
            is_system: boolean;
            created_at: string;
            updated_at: string;
        }[];
        user_count?: number | undefined;
    }[]>;
    customRoles: import("vue").ComputedRef<{
        id: string;
        name: string;
        description?: string | undefined;
        is_system: boolean;
        is_active: boolean;
        created_at: string;
        updated_at: string;
        permissions: {
            id: string;
            name: string;
            description?: string | undefined;
            resource: string;
            action: string;
            is_system: boolean;
            created_at: string;
            updated_at: string;
        }[];
        user_count?: number | undefined;
    }[]>;
    fetchRoles: () => Promise<void>;
    fetchPermissions: () => Promise<void>;
    createRole: (roleData: RoleCreate) => Promise<Role>;
    updateRole: (roleId: string, roleData: RoleUpdate) => Promise<Role>;
    deleteRole: (roleId: string) => Promise<void>;
    assignPermissions: (roleId: string, permissionIds: string[]) => Promise<void>;
    removePermissions: (roleId: string, permissionIds: string[]) => Promise<void>;
    getRoleById: (roleId: string) => Role | undefined;
    getPermissionById: (permissionId: string) => Permission | undefined;
}, "loading" | "error" | "roles" | "permissions">, Pick<{
    roles: import("vue").Ref<{
        id: string;
        name: string;
        description?: string | undefined;
        is_system: boolean;
        is_active: boolean;
        created_at: string;
        updated_at: string;
        permissions: {
            id: string;
            name: string;
            description?: string | undefined;
            resource: string;
            action: string;
            is_system: boolean;
            created_at: string;
            updated_at: string;
        }[];
        user_count?: number | undefined;
    }[], Role[] | {
        id: string;
        name: string;
        description?: string | undefined;
        is_system: boolean;
        is_active: boolean;
        created_at: string;
        updated_at: string;
        permissions: {
            id: string;
            name: string;
            description?: string | undefined;
            resource: string;
            action: string;
            is_system: boolean;
            created_at: string;
            updated_at: string;
        }[];
        user_count?: number | undefined;
    }[]>;
    permissions: import("vue").Ref<{
        id: string;
        name: string;
        description?: string | undefined;
        resource: string;
        action: string;
        is_system: boolean;
        created_at: string;
        updated_at: string;
    }[], Permission[] | {
        id: string;
        name: string;
        description?: string | undefined;
        resource: string;
        action: string;
        is_system: boolean;
        created_at: string;
        updated_at: string;
    }[]>;
    loading: import("vue").Ref<boolean, boolean>;
    error: import("vue").Ref<string | null, string | null>;
    activeRoles: import("vue").ComputedRef<{
        id: string;
        name: string;
        description?: string | undefined;
        is_system: boolean;
        is_active: boolean;
        created_at: string;
        updated_at: string;
        permissions: {
            id: string;
            name: string;
            description?: string | undefined;
            resource: string;
            action: string;
            is_system: boolean;
            created_at: string;
            updated_at: string;
        }[];
        user_count?: number | undefined;
    }[]>;
    systemRoles: import("vue").ComputedRef<{
        id: string;
        name: string;
        description?: string | undefined;
        is_system: boolean;
        is_active: boolean;
        created_at: string;
        updated_at: string;
        permissions: {
            id: string;
            name: string;
            description?: string | undefined;
            resource: string;
            action: string;
            is_system: boolean;
            created_at: string;
            updated_at: string;
        }[];
        user_count?: number | undefined;
    }[]>;
    customRoles: import("vue").ComputedRef<{
        id: string;
        name: string;
        description?: string | undefined;
        is_system: boolean;
        is_active: boolean;
        created_at: string;
        updated_at: string;
        permissions: {
            id: string;
            name: string;
            description?: string | undefined;
            resource: string;
            action: string;
            is_system: boolean;
            created_at: string;
            updated_at: string;
        }[];
        user_count?: number | undefined;
    }[]>;
    fetchRoles: () => Promise<void>;
    fetchPermissions: () => Promise<void>;
    createRole: (roleData: RoleCreate) => Promise<Role>;
    updateRole: (roleId: string, roleData: RoleUpdate) => Promise<Role>;
    deleteRole: (roleId: string) => Promise<void>;
    assignPermissions: (roleId: string, permissionIds: string[]) => Promise<void>;
    removePermissions: (roleId: string, permissionIds: string[]) => Promise<void>;
    getRoleById: (roleId: string) => Role | undefined;
    getPermissionById: (permissionId: string) => Permission | undefined;
}, "activeRoles" | "systemRoles" | "customRoles">, Pick<{
    roles: import("vue").Ref<{
        id: string;
        name: string;
        description?: string | undefined;
        is_system: boolean;
        is_active: boolean;
        created_at: string;
        updated_at: string;
        permissions: {
            id: string;
            name: string;
            description?: string | undefined;
            resource: string;
            action: string;
            is_system: boolean;
            created_at: string;
            updated_at: string;
        }[];
        user_count?: number | undefined;
    }[], Role[] | {
        id: string;
        name: string;
        description?: string | undefined;
        is_system: boolean;
        is_active: boolean;
        created_at: string;
        updated_at: string;
        permissions: {
            id: string;
            name: string;
            description?: string | undefined;
            resource: string;
            action: string;
            is_system: boolean;
            created_at: string;
            updated_at: string;
        }[];
        user_count?: number | undefined;
    }[]>;
    permissions: import("vue").Ref<{
        id: string;
        name: string;
        description?: string | undefined;
        resource: string;
        action: string;
        is_system: boolean;
        created_at: string;
        updated_at: string;
    }[], Permission[] | {
        id: string;
        name: string;
        description?: string | undefined;
        resource: string;
        action: string;
        is_system: boolean;
        created_at: string;
        updated_at: string;
    }[]>;
    loading: import("vue").Ref<boolean, boolean>;
    error: import("vue").Ref<string | null, string | null>;
    activeRoles: import("vue").ComputedRef<{
        id: string;
        name: string;
        description?: string | undefined;
        is_system: boolean;
        is_active: boolean;
        created_at: string;
        updated_at: string;
        permissions: {
            id: string;
            name: string;
            description?: string | undefined;
            resource: string;
            action: string;
            is_system: boolean;
            created_at: string;
            updated_at: string;
        }[];
        user_count?: number | undefined;
    }[]>;
    systemRoles: import("vue").ComputedRef<{
        id: string;
        name: string;
        description?: string | undefined;
        is_system: boolean;
        is_active: boolean;
        created_at: string;
        updated_at: string;
        permissions: {
            id: string;
            name: string;
            description?: string | undefined;
            resource: string;
            action: string;
            is_system: boolean;
            created_at: string;
            updated_at: string;
        }[];
        user_count?: number | undefined;
    }[]>;
    customRoles: import("vue").ComputedRef<{
        id: string;
        name: string;
        description?: string | undefined;
        is_system: boolean;
        is_active: boolean;
        created_at: string;
        updated_at: string;
        permissions: {
            id: string;
            name: string;
            description?: string | undefined;
            resource: string;
            action: string;
            is_system: boolean;
            created_at: string;
            updated_at: string;
        }[];
        user_count?: number | undefined;
    }[]>;
    fetchRoles: () => Promise<void>;
    fetchPermissions: () => Promise<void>;
    createRole: (roleData: RoleCreate) => Promise<Role>;
    updateRole: (roleId: string, roleData: RoleUpdate) => Promise<Role>;
    deleteRole: (roleId: string) => Promise<void>;
    assignPermissions: (roleId: string, permissionIds: string[]) => Promise<void>;
    removePermissions: (roleId: string, permissionIds: string[]) => Promise<void>;
    getRoleById: (roleId: string) => Role | undefined;
    getPermissionById: (permissionId: string) => Permission | undefined;
}, "fetchRoles" | "fetchPermissions" | "createRole" | "updateRole" | "deleteRole" | "assignPermissions" | "removePermissions" | "getRoleById" | "getPermissionById">>;
