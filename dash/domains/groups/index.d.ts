/**
 * Groups domain module
 *
 * This module provides type-safe interfaces and utilities for group management
 * operations including CRUD operations, membership management, and validation.
 */
import type { Group, GroupCreate, GroupUpdate, GroupWithMembers, UserInGroup, GroupMembershipRequest, GroupMembershipUpdate } from '@/types';
export declare const GROUP_TYPES: {
    readonly GENERAL: "general";
    readonly DEPARTMENT: "department";
    readonly PROJECT: "project";
    readonly TEAM: "team";
    readonly COMMUNITY: "community";
    readonly SYSTEM: "system";
};
export type GroupType = typeof GROUP_TYPES[keyof typeof GROUP_TYPES];
export declare const GROUP_ROLES: {
    readonly OWNER: "owner";
    readonly ADMIN: "admin";
    readonly MODERATOR: "moderator";
    readonly MEMBER: "member";
    readonly VIEWER: "viewer";
};
export type GroupRole = typeof GROUP_ROLES[keyof typeof GROUP_ROLES];
export declare const GROUP_SORT_OPTIONS: {
    readonly NAME: "name";
    readonly CREATED_AT: "created_at";
    readonly UPDATED_AT: "updated_at";
    readonly MEMBER_COUNT: "member_count";
    readonly GROUP_TYPE: "group_type";
};
export type GroupSortOption = typeof GROUP_SORT_OPTIONS[keyof typeof GROUP_SORT_OPTIONS];
export declare function validateGroupName(name: string): boolean;
export declare function validateGroupSlug(slug: string): boolean;
export declare function validateGroupDescription(description: string): boolean;
export declare function validateMaxMembers(maxMembers: number): boolean;
export declare function generateSlugFromName(name: string): string;
export declare function formatGroupType(groupType: string): string;
export declare function formatGroupRole(role: string): string;
export declare function getRolePermissions(role: string): {
    canEditGroup: boolean;
    canDeleteGroup: boolean;
    canAddMembers: boolean;
    canRemoveMembers: boolean;
    canManageRoles: boolean;
    canViewMembers: boolean;
};
export declare function createGroupPayload(name: string, description?: string, options?: Partial<GroupCreate>): GroupCreate;
export declare function createMembershipPayload(userIds: string[], role?: GroupRole): GroupMembershipRequest;
export declare function filterGroupsByType(groups: Group[], groupType: string): Group[];
export declare function filterPublicGroups(groups: Group[]): Group[];
export declare function filterUserOwnedGroups(groups: Group[], userId: string): Group[];
export declare function filterUserMemberGroups(groups: GroupWithMembers[], userId: string): GroupWithMembers[];
export declare function searchGroups(groups: Group[], query: string): Group[];
export declare function getUserRoleInGroup(group: GroupWithMembers, userId: string): string | null;
export declare function isUserMemberOfGroup(group: GroupWithMembers, userId: string): boolean;
export declare function canUserJoinGroup(group: Group, userId: string): boolean;
export declare function getGroupIcon(groupType: string): string;
export declare function getGroupBadgeColor(groupType: string): string;
export declare function getRoleBadgeColor(role: string): string;
export type { Group, GroupCreate, GroupUpdate, GroupWithMembers, UserInGroup, GroupMembershipRequest, GroupMembershipUpdate };
