/**
 * Groups domain module
 *
 * This module provides type-safe interfaces and utilities for group management
 * operations including CRUD operations, membership management, and validation.
 */
// Group type constants
export const GROUP_TYPES = {
    GENERAL: 'general',
    DEPARTMENT: 'department',
    PROJECT: 'project',
    TEAM: 'team',
    COMMUNITY: 'community',
    SYSTEM: 'system'
};
// Group role constants
export const GROUP_ROLES = {
    OWNER: 'owner',
    ADMIN: 'admin',
    MODERATOR: 'moderator',
    MEMBER: 'member',
    VIEWER: 'viewer'
};
// Group sorting options
export const GROUP_SORT_OPTIONS = {
    NAME: 'name',
    CREATED_AT: 'created_at',
    UPDATED_AT: 'updated_at',
    MEMBER_COUNT: 'member_count',
    GROUP_TYPE: 'group_type'
};
// Group validation functions
export function validateGroupName(name) {
    return name.length >= 3 && name.length <= 100 && /^[a-zA-Z0-9\s\-_]+$/.test(name);
}
export function validateGroupSlug(slug) {
    return /^[a-z0-9\-_]+$/.test(slug) && slug.length >= 3 && slug.length <= 50;
}
export function validateGroupDescription(description) {
    return description.length <= 500;
}
export function validateMaxMembers(maxMembers) {
    return maxMembers > 0 && maxMembers <= 10000;
}
// Group utility functions
export function generateSlugFromName(name) {
    return name
        .toLowerCase()
        .replace(/[^\w\s-]/g, '') // Remove special characters
        .replace(/\s+/g, '-') // Replace spaces with hyphens
        .replace(/-+/g, '-') // Replace multiple hyphens with single
        .trim()
        .slice(0, 50); // Limit length
}
export function formatGroupType(groupType) {
    return groupType.charAt(0).toUpperCase() + groupType.slice(1).toLowerCase();
}
export function formatGroupRole(role) {
    switch (role) {
        case GROUP_ROLES.OWNER:
            return 'Owner';
        case GROUP_ROLES.ADMIN:
            return 'Administrator';
        case GROUP_ROLES.MODERATOR:
            return 'Moderator';
        case GROUP_ROLES.MEMBER:
            return 'Member';
        case GROUP_ROLES.VIEWER:
            return 'Viewer';
        default:
            return role.charAt(0).toUpperCase() + role.slice(1).toLowerCase();
    }
}
export function getRolePermissions(role) {
    switch (role) {
        case GROUP_ROLES.OWNER:
            return {
                canEditGroup: true,
                canDeleteGroup: true,
                canAddMembers: true,
                canRemoveMembers: true,
                canManageRoles: true,
                canViewMembers: true
            };
        case GROUP_ROLES.ADMIN:
            return {
                canEditGroup: true,
                canDeleteGroup: false,
                canAddMembers: true,
                canRemoveMembers: true,
                canManageRoles: true,
                canViewMembers: true
            };
        case GROUP_ROLES.MODERATOR:
            return {
                canEditGroup: false,
                canDeleteGroup: false,
                canAddMembers: true,
                canRemoveMembers: true,
                canManageRoles: false,
                canViewMembers: true
            };
        case GROUP_ROLES.MEMBER:
            return {
                canEditGroup: false,
                canDeleteGroup: false,
                canAddMembers: false,
                canRemoveMembers: false,
                canManageRoles: false,
                canViewMembers: true
            };
        case GROUP_ROLES.VIEWER:
            return {
                canEditGroup: false,
                canDeleteGroup: false,
                canAddMembers: false,
                canRemoveMembers: false,
                canManageRoles: false,
                canViewMembers: false
            };
        default:
            return {
                canEditGroup: false,
                canDeleteGroup: false,
                canAddMembers: false,
                canRemoveMembers: false,
                canManageRoles: false,
                canViewMembers: false
            };
    }
}
// Group creation helpers
export function createGroupPayload(name, description, options) {
    return {
        name: name.trim(),
        description: description?.trim(),
        is_public: options?.is_public ?? true,
        is_open: options?.is_open ?? false,
        group_type: options?.group_type ?? GROUP_TYPES.GENERAL,
        tags: options?.tags?.trim(),
        max_members: options?.max_members,
        metadata: options?.metadata
    };
}
export function createMembershipPayload(userIds, role = GROUP_ROLES.MEMBER) {
    return {
        user_ids: userIds,
        role_in_group: role
    };
}
// Group filtering helpers
export function filterGroupsByType(groups, groupType) {
    return groups.filter(group => group.group_type === groupType);
}
export function filterPublicGroups(groups) {
    return groups.filter(group => group.is_public);
}
export function filterUserOwnedGroups(groups, userId) {
    return groups.filter(group => group.owner_id === userId);
}
export function filterUserMemberGroups(groups, userId) {
    return groups.filter(group => group.members?.some(member => member.user_id === userId));
}
// Group search helpers
export function searchGroups(groups, query) {
    const lowercaseQuery = query.toLowerCase();
    return groups.filter(group => group.name.toLowerCase().includes(lowercaseQuery) ||
        group.description?.toLowerCase().includes(lowercaseQuery) ||
        group.tags?.toLowerCase().includes(lowercaseQuery));
}
// Group membership helpers
export function getUserRoleInGroup(group, userId) {
    if (group.owner_id === userId) {
        return GROUP_ROLES.OWNER;
    }
    const membership = group.members?.find(member => member.user_id === userId);
    return membership?.role_in_group ?? null;
}
export function isUserMemberOfGroup(group, userId) {
    return group.owner_id === userId ||
        (group.members?.some(member => member.user_id === userId && member.is_active) ?? false);
}
export function canUserJoinGroup(group, userId) {
    // Check if group is open for joining
    if (!group.is_open) {
        return false;
    }
    // Check member limit
    if (group.max_members && group.member_count >= group.max_members) {
        return false;
    }
    return true;
}
// Group display helpers
export function getGroupIcon(groupType) {
    switch (groupType) {
        case GROUP_TYPES.DEPARTMENT:
            return 'building-office';
        case GROUP_TYPES.PROJECT:
            return 'folder';
        case GROUP_TYPES.TEAM:
            return 'user-group';
        case GROUP_TYPES.COMMUNITY:
            return 'users';
        case GROUP_TYPES.SYSTEM:
            return 'cog';
        default:
            return 'users';
    }
}
export function getGroupBadgeColor(groupType) {
    switch (groupType) {
        case GROUP_TYPES.DEPARTMENT:
            return 'blue';
        case GROUP_TYPES.PROJECT:
            return 'green';
        case GROUP_TYPES.TEAM:
            return 'purple';
        case GROUP_TYPES.COMMUNITY:
            return 'orange';
        case GROUP_TYPES.SYSTEM:
            return 'gray';
        default:
            return 'indigo';
    }
}
export function getRoleBadgeColor(role) {
    switch (role) {
        case GROUP_ROLES.OWNER:
            return 'red';
        case GROUP_ROLES.ADMIN:
            return 'orange';
        case GROUP_ROLES.MODERATOR:
            return 'yellow';
        case GROUP_ROLES.MEMBER:
            return 'blue';
        case GROUP_ROLES.VIEWER:
            return 'gray';
        default:
            return 'gray';
    }
}
