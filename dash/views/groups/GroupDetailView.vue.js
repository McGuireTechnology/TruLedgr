import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useGroupsStore } from '@/stores/groups';
import { formatGroupType, formatGroupRole, getGroupBadgeColor, getRoleBadgeColor, getUserRoleInGroup, isUserMemberOfGroup, canUserJoinGroup, getRolePermissions, GROUP_ROLES } from '@/domains/groups';
import GroupSettings from '@/components/groups/GroupSettings.vue';
import AddMembersModal from '@/components/modals/AddMembersModal.vue';
import EditMemberModal from '@/components/modals/EditMemberModal.vue';
import ConfirmModal from '@/components/ConfirmModal.vue';
const route = useRoute();
const router = useRouter();
const groupsStore = useGroupsStore();
// Reactive state
const activeTab = ref('members');
const showAddMembers = ref(false);
const showEditMember = ref(false);
const showRemoveMember = ref(false);
const selectedMember = ref(null);
// Computed properties
const group = computed(() => groupsStore.currentGroup);
const currentUserId = computed(() => getCurrentUserId());
const userRole = computed(() => {
    if (!group.value || !currentUserId.value)
        return null;
    return getUserRoleInGroup(group.value, currentUserId.value);
});
const rolePermissions = computed(() => {
    if (!userRole.value)
        return getRolePermissions('');
    return getRolePermissions(userRole.value);
});
const canEditGroup = computed(() => rolePermissions.value.canEditGroup);
const canAddMembers = computed(() => rolePermissions.value.canAddMembers);
const canManageMembers = computed(() => rolePermissions.value.canManageRoles || rolePermissions.value.canRemoveMembers);
const canViewSettings = computed(() => canEditGroup.value);
const canJoinGroup = computed(() => {
    if (!group.value || !currentUserId.value)
        return false;
    if (isUserMemberOfGroup(group.value, currentUserId.value))
        return false;
    return canUserJoinGroup(group.value, currentUserId.value);
});
const canLeaveGroup = computed(() => {
    if (!group.value || !currentUserId.value)
        return false;
    if (group.value.owner_id === currentUserId.value)
        return false; // Owner cannot leave
    return isUserMemberOfGroup(group.value, currentUserId.value);
});
// Methods
async function loadGroup() {
    const groupId = route.params.id;
    await groupsStore.fetchGroup(groupId, true);
}
function getCurrentUserId() {
    // TODO: Get from auth store
    return null;
}
function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString();
}
function editGroup() {
    router.push(`/groups/${group.value?.id}/edit`);
}
async function joinGroup() {
    if (!group.value || !currentUserId.value)
        return;
    // TODO: Implement join group functionality
    console.log('Joining group:', group.value.id);
}
async function leaveGroup() {
    if (!group.value || !currentUserId.value)
        return;
    const success = await groupsStore.removeUserFromGroup(group.value.id, currentUserId.value);
    if (success) {
        router.push('/groups');
    }
}
function editMember(member) {
    selectedMember.value = member;
    showEditMember.value = true;
}
function removeMember(member) {
    selectedMember.value = member;
    showRemoveMember.value = true;
}
async function confirmRemoveMember() {
    if (!group.value || !selectedMember.value)
        return;
    const success = await groupsStore.removeUserFromGroup(group.value.id, selectedMember.value.user_id);
    if (success) {
        showRemoveMember.value = false;
        selectedMember.value = null;
        await loadGroup(); // Reload to get updated member list
    }
}
function handleGroupUpdated(updatedGroup) {
    // Update the current group in store
    groupsStore.currentGroup = { ...groupsStore.currentGroup, ...updatedGroup };
}
function handleMembersAdded() {
    showAddMembers.value = false;
    loadGroup(); // Reload to get updated member list
}
function handleMemberUpdated() {
    showEditMember.value = false;
    selectedMember.value = null;
    loadGroup(); // Reload to get updated member list
}
// Lifecycle
onMounted(() => {
    loadGroup();
});
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_elements;
let __VLS_components;
let __VLS_directives;
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "space-y-6" },
});
if (__VLS_ctx.groupsStore.isLoading) {
    // @ts-ignore
    [groupsStore,];
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "text-center py-8" },
    });
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" },
    });
    __VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)({
        ...{ class: "mt-2 text-sm text-gray-500" },
    });
}
else if (__VLS_ctx.groupsStore.error) {
    // @ts-ignore
    [groupsStore,];
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "bg-red-50 border border-red-200 rounded-md p-4" },
    });
    __VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)({
        ...{ class: "text-red-800" },
    });
    (__VLS_ctx.groupsStore.error);
    // @ts-ignore
    [groupsStore,];
    __VLS_asFunctionalElement(__VLS_elements.button, __VLS_elements.button)({
        ...{ onClick: (__VLS_ctx.loadGroup) },
        ...{ class: "mt-2 text-red-600 hover:text-red-800 text-sm underline" },
    });
    // @ts-ignore
    [loadGroup,];
}
else if (__VLS_ctx.group) {
    // @ts-ignore
    [group,];
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "space-y-6" },
    });
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "bg-white shadow rounded-lg" },
    });
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "px-6 py-4 border-b border-gray-200" },
    });
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "flex items-center justify-between" },
    });
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "flex items-center space-x-4" },
    });
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "w-12 h-12 rounded-full flex items-center justify-center" },
        ...{ class: (`bg-${__VLS_ctx.getGroupBadgeColor(__VLS_ctx.group.group_type)}-100`) },
    });
    // @ts-ignore
    [group, getGroupBadgeColor,];
    __VLS_asFunctionalElement(__VLS_elements.svg, __VLS_elements.svg)({
        ...{ class: "w-6 h-6" },
        ...{ class: (`text-${__VLS_ctx.getGroupBadgeColor(__VLS_ctx.group.group_type)}-600`) },
        fill: "currentColor",
        viewBox: "0 0 20 20",
    });
    // @ts-ignore
    [group, getGroupBadgeColor,];
    __VLS_asFunctionalElement(__VLS_elements.path)({
        d: "M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z",
    });
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({});
    __VLS_asFunctionalElement(__VLS_elements.h1, __VLS_elements.h1)({
        ...{ class: "text-2xl font-bold text-gray-900" },
    });
    (__VLS_ctx.group.name);
    // @ts-ignore
    [group,];
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "flex items-center space-x-2 mt-1" },
    });
    __VLS_asFunctionalElement(__VLS_elements.span, __VLS_elements.span)({
        ...{ class: "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" },
        ...{ class: (`bg-${__VLS_ctx.getGroupBadgeColor(__VLS_ctx.group.group_type)}-100 text-${__VLS_ctx.getGroupBadgeColor(__VLS_ctx.group.group_type)}-800`) },
    });
    // @ts-ignore
    [group, group, getGroupBadgeColor, getGroupBadgeColor,];
    (__VLS_ctx.formatGroupType(__VLS_ctx.group.group_type));
    // @ts-ignore
    [group, formatGroupType,];
    __VLS_asFunctionalElement(__VLS_elements.span, __VLS_elements.span)({
        ...{ class: "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" },
        ...{ class: (__VLS_ctx.group.is_public ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800') },
    });
    // @ts-ignore
    [group,];
    (__VLS_ctx.group.is_public ? 'Public' : 'Private');
    // @ts-ignore
    [group,];
    if (__VLS_ctx.group.is_open) {
        // @ts-ignore
        [group,];
        __VLS_asFunctionalElement(__VLS_elements.span, __VLS_elements.span)({
            ...{ class: "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800" },
        });
    }
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "flex space-x-2" },
    });
    if (__VLS_ctx.canJoinGroup) {
        // @ts-ignore
        [canJoinGroup,];
        __VLS_asFunctionalElement(__VLS_elements.button, __VLS_elements.button)({
            ...{ onClick: (__VLS_ctx.joinGroup) },
            ...{ class: "bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium" },
        });
        // @ts-ignore
        [joinGroup,];
    }
    if (__VLS_ctx.canLeaveGroup) {
        // @ts-ignore
        [canLeaveGroup,];
        __VLS_asFunctionalElement(__VLS_elements.button, __VLS_elements.button)({
            ...{ onClick: (__VLS_ctx.leaveGroup) },
            ...{ class: "bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium" },
        });
        // @ts-ignore
        [leaveGroup,];
    }
    if (__VLS_ctx.canEditGroup) {
        // @ts-ignore
        [canEditGroup,];
        __VLS_asFunctionalElement(__VLS_elements.button, __VLS_elements.button)({
            ...{ onClick: (__VLS_ctx.editGroup) },
            ...{ class: "bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm font-medium" },
        });
        // @ts-ignore
        [editGroup,];
    }
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "px-6 py-4 space-y-4" },
    });
    if (__VLS_ctx.group.description) {
        // @ts-ignore
        [group,];
        __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({});
        __VLS_asFunctionalElement(__VLS_elements.h3, __VLS_elements.h3)({
            ...{ class: "text-sm font-medium text-gray-900 mb-2" },
        });
        __VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)({
            ...{ class: "text-gray-700" },
        });
        (__VLS_ctx.group.description);
        // @ts-ignore
        [group,];
    }
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "grid grid-cols-1 md:grid-cols-3 gap-4 text-sm" },
    });
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({});
    __VLS_asFunctionalElement(__VLS_elements.span, __VLS_elements.span)({
        ...{ class: "font-medium text-gray-500" },
    });
    __VLS_asFunctionalElement(__VLS_elements.span, __VLS_elements.span)({
        ...{ class: "ml-2 text-gray-900" },
    });
    (__VLS_ctx.formatDate(__VLS_ctx.group.created_at));
    // @ts-ignore
    [group, formatDate,];
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({});
    __VLS_asFunctionalElement(__VLS_elements.span, __VLS_elements.span)({
        ...{ class: "font-medium text-gray-500" },
    });
    __VLS_asFunctionalElement(__VLS_elements.span, __VLS_elements.span)({
        ...{ class: "ml-2 text-gray-900" },
    });
    (__VLS_ctx.group.member_count);
    // @ts-ignore
    [group,];
    if (__VLS_ctx.group.max_members) {
        // @ts-ignore
        [group,];
        __VLS_asFunctionalElement(__VLS_elements.span, __VLS_elements.span)({});
        (__VLS_ctx.group.max_members);
        // @ts-ignore
        [group,];
    }
    if (__VLS_ctx.group.owner) {
        // @ts-ignore
        [group,];
        __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({});
        __VLS_asFunctionalElement(__VLS_elements.span, __VLS_elements.span)({
            ...{ class: "font-medium text-gray-500" },
        });
        __VLS_asFunctionalElement(__VLS_elements.span, __VLS_elements.span)({
            ...{ class: "ml-2 text-gray-900" },
        });
        (__VLS_ctx.group.owner.username);
        // @ts-ignore
        [group,];
    }
    if (__VLS_ctx.group.tags) {
        // @ts-ignore
        [group,];
        __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
            ...{ class: "flex flex-wrap gap-2" },
        });
        for (const [tag] of __VLS_getVForSourceType((__VLS_ctx.group.tags.split(',')))) {
            // @ts-ignore
            [group,];
            __VLS_asFunctionalElement(__VLS_elements.span, __VLS_elements.span)({
                key: (tag.trim()),
                ...{ class: "inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800" },
            });
            (tag.trim());
        }
    }
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "bg-white shadow rounded-lg" },
    });
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "border-b border-gray-200" },
    });
    __VLS_asFunctionalElement(__VLS_elements.nav, __VLS_elements.nav)({
        ...{ class: "-mb-px flex space-x-8 px-6" },
    });
    __VLS_asFunctionalElement(__VLS_elements.button, __VLS_elements.button)({
        ...{ onClick: (...[$event]) => {
                if (!!(__VLS_ctx.groupsStore.isLoading))
                    return;
                if (!!(__VLS_ctx.groupsStore.error))
                    return;
                if (!(__VLS_ctx.group))
                    return;
                __VLS_ctx.activeTab = 'members';
                // @ts-ignore
                [activeTab,];
            } },
        ...{ class: ([
                'py-4 px-1 border-b-2 font-medium text-sm',
                __VLS_ctx.activeTab === 'members'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]) },
    });
    // @ts-ignore
    [activeTab,];
    (__VLS_ctx.group.member_count);
    // @ts-ignore
    [group,];
    if (__VLS_ctx.canViewSettings) {
        // @ts-ignore
        [canViewSettings,];
        __VLS_asFunctionalElement(__VLS_elements.button, __VLS_elements.button)({
            ...{ onClick: (...[$event]) => {
                    if (!!(__VLS_ctx.groupsStore.isLoading))
                        return;
                    if (!!(__VLS_ctx.groupsStore.error))
                        return;
                    if (!(__VLS_ctx.group))
                        return;
                    if (!(__VLS_ctx.canViewSettings))
                        return;
                    __VLS_ctx.activeTab = 'settings';
                    // @ts-ignore
                    [activeTab,];
                } },
            ...{ class: ([
                    'py-4 px-1 border-b-2 font-medium text-sm',
                    __VLS_ctx.activeTab === 'settings'
                        ? 'border-indigo-500 text-indigo-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                ]) },
        });
        // @ts-ignore
        [activeTab,];
    }
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "p-6" },
    });
    if (__VLS_ctx.activeTab === 'members') {
        // @ts-ignore
        [activeTab,];
        __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
            ...{ class: "space-y-4" },
        });
        if (__VLS_ctx.canAddMembers) {
            // @ts-ignore
            [canAddMembers,];
            __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
                ...{ class: "flex justify-end" },
            });
            __VLS_asFunctionalElement(__VLS_elements.button, __VLS_elements.button)({
                ...{ onClick: (...[$event]) => {
                        if (!!(__VLS_ctx.groupsStore.isLoading))
                            return;
                        if (!!(__VLS_ctx.groupsStore.error))
                            return;
                        if (!(__VLS_ctx.group))
                            return;
                        if (!(__VLS_ctx.activeTab === 'members'))
                            return;
                        if (!(__VLS_ctx.canAddMembers))
                            return;
                        __VLS_ctx.showAddMembers = true;
                        // @ts-ignore
                        [showAddMembers,];
                    } },
                ...{ class: "bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium" },
            });
        }
        if (__VLS_ctx.group.members && __VLS_ctx.group.members.length > 0) {
            // @ts-ignore
            [group, group,];
            __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
                ...{ class: "space-y-2" },
            });
            for (const [member] of __VLS_getVForSourceType((__VLS_ctx.group.members))) {
                // @ts-ignore
                [group,];
                __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
                    key: (member.user_id),
                    ...{ class: "flex items-center justify-between p-4 border border-gray-200 rounded-lg" },
                });
                __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
                    ...{ class: "flex items-center space-x-3" },
                });
                __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
                    ...{ class: "w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center" },
                });
                __VLS_asFunctionalElement(__VLS_elements.span, __VLS_elements.span)({
                    ...{ class: "text-sm font-medium text-gray-700" },
                });
                (member.user?.username?.charAt(0).toUpperCase() || '?');
                __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({});
                __VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)({
                    ...{ class: "font-medium text-gray-900" },
                });
                (member.user?.username || 'Unknown');
                __VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)({
                    ...{ class: "text-sm text-gray-500" },
                });
                (member.user?.email || '');
                __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
                    ...{ class: "flex items-center space-x-2" },
                });
                __VLS_asFunctionalElement(__VLS_elements.span, __VLS_elements.span)({
                    ...{ class: "inline-flex items-center px-2 py-1 rounded-full text-xs font-medium" },
                    ...{ class: (`bg-${__VLS_ctx.getRoleBadgeColor(member.role_in_group)}-100 text-${__VLS_ctx.getRoleBadgeColor(member.role_in_group)}-800`) },
                });
                // @ts-ignore
                [getRoleBadgeColor, getRoleBadgeColor,];
                (__VLS_ctx.formatGroupRole(member.role_in_group));
                // @ts-ignore
                [formatGroupRole,];
                if (__VLS_ctx.canManageMembers) {
                    // @ts-ignore
                    [canManageMembers,];
                    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
                        ...{ class: "flex space-x-1" },
                    });
                    __VLS_asFunctionalElement(__VLS_elements.button, __VLS_elements.button)({
                        ...{ onClick: (...[$event]) => {
                                if (!!(__VLS_ctx.groupsStore.isLoading))
                                    return;
                                if (!!(__VLS_ctx.groupsStore.error))
                                    return;
                                if (!(__VLS_ctx.group))
                                    return;
                                if (!(__VLS_ctx.activeTab === 'members'))
                                    return;
                                if (!(__VLS_ctx.group.members && __VLS_ctx.group.members.length > 0))
                                    return;
                                if (!(__VLS_ctx.canManageMembers))
                                    return;
                                __VLS_ctx.editMember(member);
                                // @ts-ignore
                                [editMember,];
                            } },
                        ...{ class: "text-indigo-600 hover:text-indigo-900 text-sm" },
                    });
                    if (member.user_id !== __VLS_ctx.group.owner_id) {
                        // @ts-ignore
                        [group,];
                        __VLS_asFunctionalElement(__VLS_elements.button, __VLS_elements.button)({
                            ...{ onClick: (...[$event]) => {
                                    if (!!(__VLS_ctx.groupsStore.isLoading))
                                        return;
                                    if (!!(__VLS_ctx.groupsStore.error))
                                        return;
                                    if (!(__VLS_ctx.group))
                                        return;
                                    if (!(__VLS_ctx.activeTab === 'members'))
                                        return;
                                    if (!(__VLS_ctx.group.members && __VLS_ctx.group.members.length > 0))
                                        return;
                                    if (!(__VLS_ctx.canManageMembers))
                                        return;
                                    if (!(member.user_id !== __VLS_ctx.group.owner_id))
                                        return;
                                    __VLS_ctx.removeMember(member);
                                    // @ts-ignore
                                    [removeMember,];
                                } },
                            ...{ class: "text-red-600 hover:text-red-900 text-sm" },
                        });
                    }
                }
            }
        }
        else {
            __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
                ...{ class: "text-center py-8 text-gray-500" },
            });
            __VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)({});
        }
    }
    if (__VLS_ctx.activeTab === 'settings' && __VLS_ctx.canViewSettings) {
        // @ts-ignore
        [activeTab, canViewSettings,];
        __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({});
        /** @type {[typeof GroupSettings, ]} */ ;
        // @ts-ignore
        const __VLS_0 = __VLS_asFunctionalComponent(GroupSettings, new GroupSettings({
            ...{ 'onUpdated': {} },
            group: (__VLS_ctx.group),
        }));
        const __VLS_1 = __VLS_0({
            ...{ 'onUpdated': {} },
            group: (__VLS_ctx.group),
        }, ...__VLS_functionalComponentArgsRest(__VLS_0));
        let __VLS_3;
        let __VLS_4;
        const __VLS_5 = ({ updated: {} },
            { onUpdated: (__VLS_ctx.handleGroupUpdated) });
        // @ts-ignore
        [group, handleGroupUpdated,];
        var __VLS_2;
    }
}
if (__VLS_ctx.showAddMembers) {
    // @ts-ignore
    [showAddMembers,];
    /** @type {[typeof AddMembersModal, ]} */ ;
    // @ts-ignore
    const __VLS_7 = __VLS_asFunctionalComponent(AddMembersModal, new AddMembersModal({
        ...{ 'onClose': {} },
        ...{ 'onAdded': {} },
        group: (__VLS_ctx.group),
    }));
    const __VLS_8 = __VLS_7({
        ...{ 'onClose': {} },
        ...{ 'onAdded': {} },
        group: (__VLS_ctx.group),
    }, ...__VLS_functionalComponentArgsRest(__VLS_7));
    let __VLS_10;
    let __VLS_11;
    const __VLS_12 = ({ close: {} },
        { onClose: (...[$event]) => {
                if (!(__VLS_ctx.showAddMembers))
                    return;
                __VLS_ctx.showAddMembers = false;
                // @ts-ignore
                [group, showAddMembers,];
            } });
    const __VLS_13 = ({ added: {} },
        { onAdded: (__VLS_ctx.handleMembersAdded) });
    // @ts-ignore
    [handleMembersAdded,];
    var __VLS_9;
}
if (__VLS_ctx.showEditMember && __VLS_ctx.selectedMember) {
    // @ts-ignore
    [showEditMember, selectedMember,];
    /** @type {[typeof EditMemberModal, ]} */ ;
    // @ts-ignore
    const __VLS_15 = __VLS_asFunctionalComponent(EditMemberModal, new EditMemberModal({
        ...{ 'onClose': {} },
        ...{ 'onUpdated': {} },
        group: (__VLS_ctx.group),
        member: (__VLS_ctx.selectedMember),
    }));
    const __VLS_16 = __VLS_15({
        ...{ 'onClose': {} },
        ...{ 'onUpdated': {} },
        group: (__VLS_ctx.group),
        member: (__VLS_ctx.selectedMember),
    }, ...__VLS_functionalComponentArgsRest(__VLS_15));
    let __VLS_18;
    let __VLS_19;
    const __VLS_20 = ({ close: {} },
        { onClose: (...[$event]) => {
                if (!(__VLS_ctx.showEditMember && __VLS_ctx.selectedMember))
                    return;
                __VLS_ctx.showEditMember = false;
                // @ts-ignore
                [group, showEditMember, selectedMember,];
            } });
    const __VLS_21 = ({ updated: {} },
        { onUpdated: (__VLS_ctx.handleMemberUpdated) });
    // @ts-ignore
    [handleMemberUpdated,];
    var __VLS_17;
}
if (__VLS_ctx.showRemoveMember && __VLS_ctx.selectedMember) {
    // @ts-ignore
    [selectedMember, showRemoveMember,];
    /** @type {[typeof ConfirmModal, ]} */ ;
    // @ts-ignore
    const __VLS_23 = __VLS_asFunctionalComponent(ConfirmModal, new ConfirmModal({
        ...{ 'onConfirm': {} },
        ...{ 'onCancel': {} },
        title: "Remove Member",
        message: (`Are you sure you want to remove ${__VLS_ctx.selectedMember.user?.username} from this group?`),
        confirmText: "Remove",
    }));
    const __VLS_24 = __VLS_23({
        ...{ 'onConfirm': {} },
        ...{ 'onCancel': {} },
        title: "Remove Member",
        message: (`Are you sure you want to remove ${__VLS_ctx.selectedMember.user?.username} from this group?`),
        confirmText: "Remove",
    }, ...__VLS_functionalComponentArgsRest(__VLS_23));
    let __VLS_26;
    let __VLS_27;
    const __VLS_28 = ({ confirm: {} },
        { onConfirm: (__VLS_ctx.confirmRemoveMember) });
    const __VLS_29 = ({ cancel: {} },
        { onCancel: (...[$event]) => {
                if (!(__VLS_ctx.showRemoveMember && __VLS_ctx.selectedMember))
                    return;
                __VLS_ctx.showRemoveMember = false;
                // @ts-ignore
                [selectedMember, showRemoveMember, confirmRemoveMember,];
            } });
    var __VLS_25;
}
/** @type {__VLS_StyleScopedClasses['space-y-6']} */ ;
/** @type {__VLS_StyleScopedClasses['text-center']} */ ;
/** @type {__VLS_StyleScopedClasses['py-8']} */ ;
/** @type {__VLS_StyleScopedClasses['inline-block']} */ ;
/** @type {__VLS_StyleScopedClasses['animate-spin']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-full']} */ ;
/** @type {__VLS_StyleScopedClasses['h-8']} */ ;
/** @type {__VLS_StyleScopedClasses['w-8']} */ ;
/** @type {__VLS_StyleScopedClasses['border-b-2']} */ ;
/** @type {__VLS_StyleScopedClasses['border-indigo-600']} */ ;
/** @type {__VLS_StyleScopedClasses['mt-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-500']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-red-50']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-red-200']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-md']} */ ;
/** @type {__VLS_StyleScopedClasses['p-4']} */ ;
/** @type {__VLS_StyleScopedClasses['text-red-800']} */ ;
/** @type {__VLS_StyleScopedClasses['mt-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-red-600']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:text-red-800']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['underline']} */ ;
/** @type {__VLS_StyleScopedClasses['space-y-6']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-white']} */ ;
/** @type {__VLS_StyleScopedClasses['shadow']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['px-6']} */ ;
/** @type {__VLS_StyleScopedClasses['py-4']} */ ;
/** @type {__VLS_StyleScopedClasses['border-b']} */ ;
/** @type {__VLS_StyleScopedClasses['border-gray-200']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-between']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['space-x-4']} */ ;
/** @type {__VLS_StyleScopedClasses['w-12']} */ ;
/** @type {__VLS_StyleScopedClasses['h-12']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-full']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-center']} */ ;
/** @type {__VLS_StyleScopedClasses['w-6']} */ ;
/** @type {__VLS_StyleScopedClasses['h-6']} */ ;
/** @type {__VLS_StyleScopedClasses['text-2xl']} */ ;
/** @type {__VLS_StyleScopedClasses['font-bold']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-900']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['space-x-2']} */ ;
/** @type {__VLS_StyleScopedClasses['mt-1']} */ ;
/** @type {__VLS_StyleScopedClasses['inline-flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2.5']} */ ;
/** @type {__VLS_StyleScopedClasses['py-0.5']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-full']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['inline-flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2.5']} */ ;
/** @type {__VLS_StyleScopedClasses['py-0.5']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-full']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['inline-flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2.5']} */ ;
/** @type {__VLS_StyleScopedClasses['py-0.5']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-full']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-blue-100']} */ ;
/** @type {__VLS_StyleScopedClasses['text-blue-800']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['space-x-2']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-indigo-600']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:bg-indigo-700']} */ ;
/** @type {__VLS_StyleScopedClasses['text-white']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-md']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-red-600']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:bg-red-700']} */ ;
/** @type {__VLS_StyleScopedClasses['text-white']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-md']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-gray-600']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:bg-gray-700']} */ ;
/** @type {__VLS_StyleScopedClasses['text-white']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-md']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['px-6']} */ ;
/** @type {__VLS_StyleScopedClasses['py-4']} */ ;
/** @type {__VLS_StyleScopedClasses['space-y-4']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-900']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-700']} */ ;
/** @type {__VLS_StyleScopedClasses['grid']} */ ;
/** @type {__VLS_StyleScopedClasses['grid-cols-1']} */ ;
/** @type {__VLS_StyleScopedClasses['md:grid-cols-3']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-4']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-500']} */ ;
/** @type {__VLS_StyleScopedClasses['ml-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-900']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-500']} */ ;
/** @type {__VLS_StyleScopedClasses['ml-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-900']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-500']} */ ;
/** @type {__VLS_StyleScopedClasses['ml-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-900']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['flex-wrap']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-2']} */ ;
/** @type {__VLS_StyleScopedClasses['inline-flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-1']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-full']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-gray-100']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-800']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-white']} */ ;
/** @type {__VLS_StyleScopedClasses['shadow']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['border-b']} */ ;
/** @type {__VLS_StyleScopedClasses['border-gray-200']} */ ;
/** @type {__VLS_StyleScopedClasses['-mb-px']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['space-x-8']} */ ;
/** @type {__VLS_StyleScopedClasses['px-6']} */ ;
/** @type {__VLS_StyleScopedClasses['py-4']} */ ;
/** @type {__VLS_StyleScopedClasses['px-1']} */ ;
/** @type {__VLS_StyleScopedClasses['border-b-2']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['py-4']} */ ;
/** @type {__VLS_StyleScopedClasses['px-1']} */ ;
/** @type {__VLS_StyleScopedClasses['border-b-2']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['p-6']} */ ;
/** @type {__VLS_StyleScopedClasses['space-y-4']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-end']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-indigo-600']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:bg-indigo-700']} */ ;
/** @type {__VLS_StyleScopedClasses['text-white']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-md']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['space-y-2']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-between']} */ ;
/** @type {__VLS_StyleScopedClasses['p-4']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-gray-200']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['space-x-3']} */ ;
/** @type {__VLS_StyleScopedClasses['w-8']} */ ;
/** @type {__VLS_StyleScopedClasses['h-8']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-gray-300']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-full']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-center']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-700']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-900']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-500']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['space-x-2']} */ ;
/** @type {__VLS_StyleScopedClasses['inline-flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-1']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-full']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['space-x-1']} */ ;
/** @type {__VLS_StyleScopedClasses['text-indigo-600']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:text-indigo-900']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-red-600']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:text-red-900']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-center']} */ ;
/** @type {__VLS_StyleScopedClasses['py-8']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-500']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup: () => ({
        formatGroupType: formatGroupType,
        formatGroupRole: formatGroupRole,
        getGroupBadgeColor: getGroupBadgeColor,
        getRoleBadgeColor: getRoleBadgeColor,
        GroupSettings: GroupSettings,
        AddMembersModal: AddMembersModal,
        EditMemberModal: EditMemberModal,
        ConfirmModal: ConfirmModal,
        groupsStore: groupsStore,
        activeTab: activeTab,
        showAddMembers: showAddMembers,
        showEditMember: showEditMember,
        showRemoveMember: showRemoveMember,
        selectedMember: selectedMember,
        group: group,
        canEditGroup: canEditGroup,
        canAddMembers: canAddMembers,
        canManageMembers: canManageMembers,
        canViewSettings: canViewSettings,
        canJoinGroup: canJoinGroup,
        canLeaveGroup: canLeaveGroup,
        loadGroup: loadGroup,
        formatDate: formatDate,
        editGroup: editGroup,
        joinGroup: joinGroup,
        leaveGroup: leaveGroup,
        editMember: editMember,
        removeMember: removeMember,
        confirmRemoveMember: confirmRemoveMember,
        handleGroupUpdated: handleGroupUpdated,
        handleMembersAdded: handleMembersAdded,
        handleMemberUpdated: handleMemberUpdated,
    }),
});
export default (await import('vue')).defineComponent({});
; /* PartiallyEnd: #4569/main.vue */
