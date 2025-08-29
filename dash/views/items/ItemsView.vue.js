/// <reference types="../../../node_modules/.vue-global-types/vue_3.5_0.d.ts" />
import { ref, computed, onMounted } from 'vue';
import { useItemsStore } from '@/stores/items';
import { useToast } from 'vue-toastification';
import { PlusIcon, CubeIcon, CheckCircleIcon, XCircleIcon, PencilIcon, TrashIcon, EyeIcon, EyeSlashIcon, ArrowPathIcon, } from '@heroicons/vue/24/outline';
import ItemModal from './ItemModal.vue';
import ConfirmModal from '@/components/ConfirmModal.vue';
const itemsStore = useItemsStore();
const toast = useToast();
// Reactive data
const showCreateModal = ref(false);
const editingItem = ref(null);
const itemToDelete = ref(null);
const statusFilter = ref('all');
const searchQuery = ref('');
// Computed
const items = computed(() => itemsStore.items);
const loading = computed(() => itemsStore.loading);
const activeItems = computed(() => itemsStore.activeItems);
const inactiveItems = computed(() => itemsStore.inactiveItems);
const filteredItems = computed(() => {
    let filtered = items.value;
    // Apply status filter
    if (statusFilter.value === 'active') {
        filtered = activeItems.value;
    }
    else if (statusFilter.value === 'inactive') {
        filtered = inactiveItems.value;
    }
    // Apply search filter
    if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase();
        filtered = filtered.filter((item) => item.name.toLowerCase().includes(query) ||
            (item.description && item.description.toLowerCase().includes(query)));
    }
    return filtered;
});
// Methods
const editItem = (item) => {
    editingItem.value = { ...item };
};
const closeModal = () => {
    showCreateModal.value = false;
    editingItem.value = null;
};
const handleSave = async (itemData) => {
    try {
        if (editingItem.value) {
            // Update existing item
            await itemsStore.updateItem(editingItem.value.id, itemData);
            toast.success('Item updated successfully!');
        }
        else {
            // Create new item
            await itemsStore.createItem(itemData);
            toast.success('Item created successfully!');
        }
        closeModal();
    }
    catch (error) {
        toast.error('Failed to save item');
    }
};
const toggleStatus = async (item) => {
    try {
        await itemsStore.toggleItemStatus(item.id);
        toast.success(`Item ${item.is_active ? 'deactivated' : 'activated'} successfully!`);
    }
    catch (error) {
        toast.error('Failed to update item status');
    }
};
const confirmDelete = (item) => {
    itemToDelete.value = item;
};
const handleDelete = async () => {
    if (!itemToDelete.value)
        return;
    try {
        await itemsStore.deleteItem(itemToDelete.value.id);
        toast.success('Item deleted successfully!');
        itemToDelete.value = null;
    }
    catch (error) {
        toast.error('Failed to delete item');
    }
};
// Initialize
const loadItems = async (force = false) => {
    try {
        console.log('Loading items..., force:', force);
        await itemsStore.fetchItems(force);
        console.log('Items loaded successfully:', itemsStore.items.length);
    }
    catch (error) {
        console.error('Failed to load items:', error);
        toast.error('Failed to load items');
    }
};
onMounted(async () => {
    console.log('ItemsView mounted, loading items...');
    await loadItems(true); // Force load on mount
});
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_elements;
let __VLS_components;
let __VLS_directives;
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "space-y-6" },
});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "sm:flex sm:items-center sm:justify-between" },
});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({});
__VLS_asFunctionalElement(__VLS_elements.h1, __VLS_elements.h1)({
    ...{ class: "text-2xl font-bold text-gray-900" },
});
__VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)({
    ...{ class: "mt-2 text-sm text-gray-700" },
});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "mt-4 sm:mt-0 flex space-x-3" },
});
__VLS_asFunctionalElement(__VLS_elements.button, __VLS_elements.button)({
    ...{ onClick: (...[$event]) => {
            __VLS_ctx.loadItems(true);
            // @ts-ignore
            [loadItems,];
        } },
    type: "button",
    ...{ class: "inline-flex items-center px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500" },
    disabled: (__VLS_ctx.loading),
});
// @ts-ignore
[loading,];
const __VLS_0 = {}.ArrowPathIcon;
/** @type {[typeof __VLS_components.ArrowPathIcon, ]} */ ;
// @ts-ignore
ArrowPathIcon;
// @ts-ignore
const __VLS_1 = __VLS_asFunctionalComponent(__VLS_0, new __VLS_0({
    ...{ class: "-ml-1 mr-2 h-4 w-4" },
    ...{ class: ({ 'animate-spin': __VLS_ctx.loading }) },
    'aria-hidden': "true",
}));
const __VLS_2 = __VLS_1({
    ...{ class: "-ml-1 mr-2 h-4 w-4" },
    ...{ class: ({ 'animate-spin': __VLS_ctx.loading }) },
    'aria-hidden': "true",
}, ...__VLS_functionalComponentArgsRest(__VLS_1));
// @ts-ignore
[loading,];
__VLS_asFunctionalElement(__VLS_elements.button, __VLS_elements.button)({
    ...{ onClick: (...[$event]) => {
            __VLS_ctx.showCreateModal = true;
            // @ts-ignore
            [showCreateModal,];
        } },
    type: "button",
    ...{ class: "inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500" },
});
const __VLS_5 = {}.PlusIcon;
/** @type {[typeof __VLS_components.PlusIcon, ]} */ ;
// @ts-ignore
PlusIcon;
// @ts-ignore
const __VLS_6 = __VLS_asFunctionalComponent(__VLS_5, new __VLS_5({
    ...{ class: "-ml-1 mr-2 h-5 w-5" },
    'aria-hidden': "true",
}));
const __VLS_7 = __VLS_6({
    ...{ class: "-ml-1 mr-2 h-5 w-5" },
    'aria-hidden': "true",
}, ...__VLS_functionalComponentArgsRest(__VLS_6));
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3" },
});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "bg-white overflow-hidden shadow rounded-lg" },
});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "p-5" },
});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "flex items-center" },
});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "flex-shrink-0" },
});
const __VLS_10 = {}.CubeIcon;
/** @type {[typeof __VLS_components.CubeIcon, ]} */ ;
// @ts-ignore
CubeIcon;
// @ts-ignore
const __VLS_11 = __VLS_asFunctionalComponent(__VLS_10, new __VLS_10({
    ...{ class: "h-6 w-6 text-gray-400" },
    'aria-hidden': "true",
}));
const __VLS_12 = __VLS_11({
    ...{ class: "h-6 w-6 text-gray-400" },
    'aria-hidden': "true",
}, ...__VLS_functionalComponentArgsRest(__VLS_11));
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "ml-5 w-0 flex-1" },
});
__VLS_asFunctionalElement(__VLS_elements.dl, __VLS_elements.dl)({});
__VLS_asFunctionalElement(__VLS_elements.dt, __VLS_elements.dt)({
    ...{ class: "text-sm font-medium text-gray-500 truncate" },
});
__VLS_asFunctionalElement(__VLS_elements.dd, __VLS_elements.dd)({
    ...{ class: "text-lg font-medium text-gray-900" },
});
(__VLS_ctx.items.length);
// @ts-ignore
[items,];
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "bg-white overflow-hidden shadow rounded-lg" },
});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "p-5" },
});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "flex items-center" },
});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "flex-shrink-0" },
});
const __VLS_15 = {}.CheckCircleIcon;
/** @type {[typeof __VLS_components.CheckCircleIcon, ]} */ ;
// @ts-ignore
CheckCircleIcon;
// @ts-ignore
const __VLS_16 = __VLS_asFunctionalComponent(__VLS_15, new __VLS_15({
    ...{ class: "h-6 w-6 text-green-400" },
    'aria-hidden': "true",
}));
const __VLS_17 = __VLS_16({
    ...{ class: "h-6 w-6 text-green-400" },
    'aria-hidden': "true",
}, ...__VLS_functionalComponentArgsRest(__VLS_16));
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "ml-5 w-0 flex-1" },
});
__VLS_asFunctionalElement(__VLS_elements.dl, __VLS_elements.dl)({});
__VLS_asFunctionalElement(__VLS_elements.dt, __VLS_elements.dt)({
    ...{ class: "text-sm font-medium text-gray-500 truncate" },
});
__VLS_asFunctionalElement(__VLS_elements.dd, __VLS_elements.dd)({
    ...{ class: "text-lg font-medium text-gray-900" },
});
(__VLS_ctx.activeItems.length);
// @ts-ignore
[activeItems,];
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "bg-white overflow-hidden shadow rounded-lg" },
});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "p-5" },
});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "flex items-center" },
});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "flex-shrink-0" },
});
const __VLS_20 = {}.XCircleIcon;
/** @type {[typeof __VLS_components.XCircleIcon, ]} */ ;
// @ts-ignore
XCircleIcon;
// @ts-ignore
const __VLS_21 = __VLS_asFunctionalComponent(__VLS_20, new __VLS_20({
    ...{ class: "h-6 w-6 text-red-400" },
    'aria-hidden': "true",
}));
const __VLS_22 = __VLS_21({
    ...{ class: "h-6 w-6 text-red-400" },
    'aria-hidden': "true",
}, ...__VLS_functionalComponentArgsRest(__VLS_21));
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "ml-5 w-0 flex-1" },
});
__VLS_asFunctionalElement(__VLS_elements.dl, __VLS_elements.dl)({});
__VLS_asFunctionalElement(__VLS_elements.dt, __VLS_elements.dt)({
    ...{ class: "text-sm font-medium text-gray-500 truncate" },
});
__VLS_asFunctionalElement(__VLS_elements.dd, __VLS_elements.dd)({
    ...{ class: "text-lg font-medium text-gray-900" },
});
(__VLS_ctx.inactiveItems.length);
// @ts-ignore
[inactiveItems,];
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "bg-white shadow rounded-lg" },
});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "px-4 py-5 sm:p-6" },
});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "sm:flex sm:items-center sm:justify-between" },
});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "flex space-x-4" },
});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({});
__VLS_asFunctionalElement(__VLS_elements.label, __VLS_elements.label)({
    for: "status-filter",
    ...{ class: "block text-sm font-medium text-gray-700" },
});
__VLS_asFunctionalElement(__VLS_elements.select, __VLS_elements.select)({
    id: "status-filter",
    value: (__VLS_ctx.statusFilter),
    ...{ class: "mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md" },
});
// @ts-ignore
[statusFilter,];
__VLS_asFunctionalElement(__VLS_elements.option, __VLS_elements.option)({
    value: "all",
});
__VLS_asFunctionalElement(__VLS_elements.option, __VLS_elements.option)({
    value: "active",
});
__VLS_asFunctionalElement(__VLS_elements.option, __VLS_elements.option)({
    value: "inactive",
});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({});
__VLS_asFunctionalElement(__VLS_elements.label, __VLS_elements.label)({
    for: "search",
    ...{ class: "block text-sm font-medium text-gray-700" },
});
__VLS_asFunctionalElement(__VLS_elements.input)({
    id: "search",
    value: (__VLS_ctx.searchQuery),
    type: "text",
    placeholder: "Search items...",
    ...{ class: "mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm" },
});
// @ts-ignore
[searchQuery,];
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "bg-white shadow overflow-hidden sm:rounded-md" },
});
if (__VLS_ctx.loading) {
    // @ts-ignore
    [loading,];
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "p-6 text-center" },
    });
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "inline-flex items-center" },
    });
    __VLS_asFunctionalElement(__VLS_elements.svg, __VLS_elements.svg)({
        ...{ class: "animate-spin -ml-1 mr-3 h-5 w-5 text-gray-500" },
        xmlns: "http://www.w3.org/2000/svg",
        fill: "none",
        viewBox: "0 0 24 24",
    });
    __VLS_asFunctionalElement(__VLS_elements.circle, __VLS_elements.circle)({
        ...{ class: "opacity-25" },
        cx: "12",
        cy: "12",
        r: "10",
        stroke: "currentColor",
        'stroke-width': "4",
    });
    __VLS_asFunctionalElement(__VLS_elements.path, __VLS_elements.path)({
        ...{ class: "opacity-75" },
        fill: "currentColor",
        d: "M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z",
    });
}
else if (__VLS_ctx.filteredItems.length > 0) {
    // @ts-ignore
    [filteredItems,];
    __VLS_asFunctionalElement(__VLS_elements.ul, __VLS_elements.ul)({
        role: "list",
        ...{ class: "divide-y divide-gray-200" },
    });
    for (const [item] of __VLS_getVForSourceType((__VLS_ctx.filteredItems))) {
        // @ts-ignore
        [filteredItems,];
        __VLS_asFunctionalElement(__VLS_elements.li, __VLS_elements.li)({
            key: (item.id),
            ...{ class: "px-6 py-4" },
        });
        __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
            ...{ class: "flex items-center justify-between" },
        });
        __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
            ...{ class: "flex-1 min-w-0" },
        });
        __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
            ...{ class: "flex items-center space-x-3" },
        });
        __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
            ...{ class: ([
                    'flex-shrink-0 w-2.5 h-2.5 rounded-full',
                    item.is_active ? 'bg-green-400' : 'bg-red-400'
                ]) },
        });
        __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
            ...{ class: "flex-1 min-w-0" },
        });
        __VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)({
            ...{ class: "text-sm font-medium text-gray-900 truncate" },
        });
        (item.name);
        if (item.description) {
            __VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)({
                ...{ class: "text-sm text-gray-500 truncate" },
            });
            (item.description);
        }
        __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
            ...{ class: "flex items-center space-x-2" },
        });
        __VLS_asFunctionalElement(__VLS_elements.span, __VLS_elements.span)({
            ...{ class: ([
                    'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                    item.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                ]) },
        });
        (item.is_active ? 'Active' : 'Inactive');
        __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
            ...{ class: "flex space-x-1" },
        });
        __VLS_asFunctionalElement(__VLS_elements.button, __VLS_elements.button)({
            ...{ onClick: (...[$event]) => {
                    if (!!(__VLS_ctx.loading))
                        return;
                    if (!(__VLS_ctx.filteredItems.length > 0))
                        return;
                    __VLS_ctx.editItem(item);
                    // @ts-ignore
                    [editItem,];
                } },
            ...{ class: "p-1 text-gray-400 hover:text-gray-600" },
            title: "Edit item",
        });
        const __VLS_25 = {}.PencilIcon;
        /** @type {[typeof __VLS_components.PencilIcon, ]} */ ;
        // @ts-ignore
        PencilIcon;
        // @ts-ignore
        const __VLS_26 = __VLS_asFunctionalComponent(__VLS_25, new __VLS_25({
            ...{ class: "h-4 w-4" },
        }));
        const __VLS_27 = __VLS_26({
            ...{ class: "h-4 w-4" },
        }, ...__VLS_functionalComponentArgsRest(__VLS_26));
        __VLS_asFunctionalElement(__VLS_elements.button, __VLS_elements.button)({
            ...{ onClick: (...[$event]) => {
                    if (!!(__VLS_ctx.loading))
                        return;
                    if (!(__VLS_ctx.filteredItems.length > 0))
                        return;
                    __VLS_ctx.toggleStatus(item);
                    // @ts-ignore
                    [toggleStatus,];
                } },
            ...{ class: "p-1 text-gray-400 hover:text-gray-600" },
            title: (item.is_active ? 'Deactivate item' : 'Activate item'),
        });
        const __VLS_30 = ((item.is_active ? __VLS_ctx.EyeSlashIcon : __VLS_ctx.EyeIcon));
        // @ts-ignore
        const __VLS_31 = __VLS_asFunctionalComponent(__VLS_30, new __VLS_30({
            ...{ class: "h-4 w-4" },
        }));
        const __VLS_32 = __VLS_31({
            ...{ class: "h-4 w-4" },
        }, ...__VLS_functionalComponentArgsRest(__VLS_31));
        // @ts-ignore
        [EyeSlashIcon, EyeIcon,];
        __VLS_asFunctionalElement(__VLS_elements.button, __VLS_elements.button)({
            ...{ onClick: (...[$event]) => {
                    if (!!(__VLS_ctx.loading))
                        return;
                    if (!(__VLS_ctx.filteredItems.length > 0))
                        return;
                    __VLS_ctx.confirmDelete(item);
                    // @ts-ignore
                    [confirmDelete,];
                } },
            ...{ class: "p-1 text-gray-400 hover:text-red-600" },
            title: "Delete item",
        });
        const __VLS_35 = {}.TrashIcon;
        /** @type {[typeof __VLS_components.TrashIcon, ]} */ ;
        // @ts-ignore
        TrashIcon;
        // @ts-ignore
        const __VLS_36 = __VLS_asFunctionalComponent(__VLS_35, new __VLS_35({
            ...{ class: "h-4 w-4" },
        }));
        const __VLS_37 = __VLS_36({
            ...{ class: "h-4 w-4" },
        }, ...__VLS_functionalComponentArgsRest(__VLS_36));
    }
}
else {
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "px-6 py-12 text-center" },
    });
    const __VLS_40 = {}.CubeIcon;
    /** @type {[typeof __VLS_components.CubeIcon, ]} */ ;
    // @ts-ignore
    CubeIcon;
    // @ts-ignore
    const __VLS_41 = __VLS_asFunctionalComponent(__VLS_40, new __VLS_40({
        ...{ class: "mx-auto h-12 w-12 text-gray-400" },
    }));
    const __VLS_42 = __VLS_41({
        ...{ class: "mx-auto h-12 w-12 text-gray-400" },
    }, ...__VLS_functionalComponentArgsRest(__VLS_41));
    __VLS_asFunctionalElement(__VLS_elements.h3, __VLS_elements.h3)({
        ...{ class: "mt-2 text-sm font-medium text-gray-900" },
    });
    __VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)({
        ...{ class: "mt-1 text-sm text-gray-500" },
    });
    (__VLS_ctx.searchQuery || __VLS_ctx.statusFilter !== 'all' ? 'Try adjusting your filters.' : 'Get started by creating a new item.');
    // @ts-ignore
    [statusFilter, searchQuery,];
}
if (__VLS_ctx.showCreateModal || __VLS_ctx.editingItem) {
    // @ts-ignore
    [showCreateModal, editingItem,];
    /** @type {[typeof ItemModal, ]} */ ;
    // @ts-ignore
    const __VLS_45 = __VLS_asFunctionalComponent(ItemModal, new ItemModal({
        ...{ 'onClose': {} },
        ...{ 'onSave': {} },
        item: (__VLS_ctx.editingItem),
    }));
    const __VLS_46 = __VLS_45({
        ...{ 'onClose': {} },
        ...{ 'onSave': {} },
        item: (__VLS_ctx.editingItem),
    }, ...__VLS_functionalComponentArgsRest(__VLS_45));
    let __VLS_48;
    let __VLS_49;
    const __VLS_50 = ({ close: {} },
        { onClose: (__VLS_ctx.closeModal) });
    const __VLS_51 = ({ save: {} },
        { onSave: (__VLS_ctx.handleSave) });
    // @ts-ignore
    [editingItem, closeModal, handleSave,];
    var __VLS_47;
}
if (__VLS_ctx.itemToDelete) {
    // @ts-ignore
    [itemToDelete,];
    /** @type {[typeof ConfirmModal, ]} */ ;
    // @ts-ignore
    const __VLS_53 = __VLS_asFunctionalComponent(ConfirmModal, new ConfirmModal({
        ...{ 'onConfirm': {} },
        ...{ 'onCancel': {} },
        title: "Delete Item",
        message: (`Are you sure you want to delete '${__VLS_ctx.itemToDelete.name}'? This action cannot be undone.`),
        confirmText: "Delete",
        confirmClass: "bg-red-600 hover:bg-red-700 focus:ring-red-500",
    }));
    const __VLS_54 = __VLS_53({
        ...{ 'onConfirm': {} },
        ...{ 'onCancel': {} },
        title: "Delete Item",
        message: (`Are you sure you want to delete '${__VLS_ctx.itemToDelete.name}'? This action cannot be undone.`),
        confirmText: "Delete",
        confirmClass: "bg-red-600 hover:bg-red-700 focus:ring-red-500",
    }, ...__VLS_functionalComponentArgsRest(__VLS_53));
    let __VLS_56;
    let __VLS_57;
    const __VLS_58 = ({ confirm: {} },
        { onConfirm: (__VLS_ctx.handleDelete) });
    const __VLS_59 = ({ cancel: {} },
        { onCancel: (...[$event]) => {
                if (!(__VLS_ctx.itemToDelete))
                    return;
                __VLS_ctx.itemToDelete = null;
                // @ts-ignore
                [itemToDelete, itemToDelete, handleDelete,];
            } });
    var __VLS_55;
}
/** @type {__VLS_StyleScopedClasses['space-y-6']} */ ;
/** @type {__VLS_StyleScopedClasses['sm:flex']} */ ;
/** @type {__VLS_StyleScopedClasses['sm:items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['sm:justify-between']} */ ;
/** @type {__VLS_StyleScopedClasses['text-2xl']} */ ;
/** @type {__VLS_StyleScopedClasses['font-bold']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-900']} */ ;
/** @type {__VLS_StyleScopedClasses['mt-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-700']} */ ;
/** @type {__VLS_StyleScopedClasses['mt-4']} */ ;
/** @type {__VLS_StyleScopedClasses['sm:mt-0']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['space-x-3']} */ ;
/** @type {__VLS_StyleScopedClasses['inline-flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['px-3']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-gray-300']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-md']} */ ;
/** @type {__VLS_StyleScopedClasses['shadow-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-700']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-white']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:bg-gray-50']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:outline-none']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:ring-2']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:ring-offset-2']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:ring-primary-500']} */ ;
/** @type {__VLS_StyleScopedClasses['-ml-1']} */ ;
/** @type {__VLS_StyleScopedClasses['mr-2']} */ ;
/** @type {__VLS_StyleScopedClasses['h-4']} */ ;
/** @type {__VLS_StyleScopedClasses['w-4']} */ ;
/** @type {__VLS_StyleScopedClasses['animate-spin']} */ ;
/** @type {__VLS_StyleScopedClasses['inline-flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-transparent']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-md']} */ ;
/** @type {__VLS_StyleScopedClasses['shadow-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['text-white']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-primary-600']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:bg-primary-700']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:outline-none']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:ring-2']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:ring-offset-2']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:ring-primary-500']} */ ;
/** @type {__VLS_StyleScopedClasses['-ml-1']} */ ;
/** @type {__VLS_StyleScopedClasses['mr-2']} */ ;
/** @type {__VLS_StyleScopedClasses['h-5']} */ ;
/** @type {__VLS_StyleScopedClasses['w-5']} */ ;
/** @type {__VLS_StyleScopedClasses['grid']} */ ;
/** @type {__VLS_StyleScopedClasses['grid-cols-1']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-5']} */ ;
/** @type {__VLS_StyleScopedClasses['sm:grid-cols-2']} */ ;
/** @type {__VLS_StyleScopedClasses['lg:grid-cols-3']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-white']} */ ;
/** @type {__VLS_StyleScopedClasses['overflow-hidden']} */ ;
/** @type {__VLS_StyleScopedClasses['shadow']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['p-5']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['flex-shrink-0']} */ ;
/** @type {__VLS_StyleScopedClasses['h-6']} */ ;
/** @type {__VLS_StyleScopedClasses['w-6']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-400']} */ ;
/** @type {__VLS_StyleScopedClasses['ml-5']} */ ;
/** @type {__VLS_StyleScopedClasses['w-0']} */ ;
/** @type {__VLS_StyleScopedClasses['flex-1']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-500']} */ ;
/** @type {__VLS_StyleScopedClasses['truncate']} */ ;
/** @type {__VLS_StyleScopedClasses['text-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-900']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-white']} */ ;
/** @type {__VLS_StyleScopedClasses['overflow-hidden']} */ ;
/** @type {__VLS_StyleScopedClasses['shadow']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['p-5']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['flex-shrink-0']} */ ;
/** @type {__VLS_StyleScopedClasses['h-6']} */ ;
/** @type {__VLS_StyleScopedClasses['w-6']} */ ;
/** @type {__VLS_StyleScopedClasses['text-green-400']} */ ;
/** @type {__VLS_StyleScopedClasses['ml-5']} */ ;
/** @type {__VLS_StyleScopedClasses['w-0']} */ ;
/** @type {__VLS_StyleScopedClasses['flex-1']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-500']} */ ;
/** @type {__VLS_StyleScopedClasses['truncate']} */ ;
/** @type {__VLS_StyleScopedClasses['text-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-900']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-white']} */ ;
/** @type {__VLS_StyleScopedClasses['overflow-hidden']} */ ;
/** @type {__VLS_StyleScopedClasses['shadow']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['p-5']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['flex-shrink-0']} */ ;
/** @type {__VLS_StyleScopedClasses['h-6']} */ ;
/** @type {__VLS_StyleScopedClasses['w-6']} */ ;
/** @type {__VLS_StyleScopedClasses['text-red-400']} */ ;
/** @type {__VLS_StyleScopedClasses['ml-5']} */ ;
/** @type {__VLS_StyleScopedClasses['w-0']} */ ;
/** @type {__VLS_StyleScopedClasses['flex-1']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-500']} */ ;
/** @type {__VLS_StyleScopedClasses['truncate']} */ ;
/** @type {__VLS_StyleScopedClasses['text-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-900']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-white']} */ ;
/** @type {__VLS_StyleScopedClasses['shadow']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-5']} */ ;
/** @type {__VLS_StyleScopedClasses['sm:p-6']} */ ;
/** @type {__VLS_StyleScopedClasses['sm:flex']} */ ;
/** @type {__VLS_StyleScopedClasses['sm:items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['sm:justify-between']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['space-x-4']} */ ;
/** @type {__VLS_StyleScopedClasses['block']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-700']} */ ;
/** @type {__VLS_StyleScopedClasses['mt-1']} */ ;
/** @type {__VLS_StyleScopedClasses['block']} */ ;
/** @type {__VLS_StyleScopedClasses['w-full']} */ ;
/** @type {__VLS_StyleScopedClasses['pl-3']} */ ;
/** @type {__VLS_StyleScopedClasses['pr-10']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-base']} */ ;
/** @type {__VLS_StyleScopedClasses['border-gray-300']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:outline-none']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:ring-primary-500']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:border-primary-500']} */ ;
/** @type {__VLS_StyleScopedClasses['sm:text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-md']} */ ;
/** @type {__VLS_StyleScopedClasses['block']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-700']} */ ;
/** @type {__VLS_StyleScopedClasses['mt-1']} */ ;
/** @type {__VLS_StyleScopedClasses['block']} */ ;
/** @type {__VLS_StyleScopedClasses['w-full']} */ ;
/** @type {__VLS_StyleScopedClasses['border-gray-300']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-md']} */ ;
/** @type {__VLS_StyleScopedClasses['shadow-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:ring-primary-500']} */ ;
/** @type {__VLS_StyleScopedClasses['focus:border-primary-500']} */ ;
/** @type {__VLS_StyleScopedClasses['sm:text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-white']} */ ;
/** @type {__VLS_StyleScopedClasses['shadow']} */ ;
/** @type {__VLS_StyleScopedClasses['overflow-hidden']} */ ;
/** @type {__VLS_StyleScopedClasses['sm:rounded-md']} */ ;
/** @type {__VLS_StyleScopedClasses['p-6']} */ ;
/** @type {__VLS_StyleScopedClasses['text-center']} */ ;
/** @type {__VLS_StyleScopedClasses['inline-flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['animate-spin']} */ ;
/** @type {__VLS_StyleScopedClasses['-ml-1']} */ ;
/** @type {__VLS_StyleScopedClasses['mr-3']} */ ;
/** @type {__VLS_StyleScopedClasses['h-5']} */ ;
/** @type {__VLS_StyleScopedClasses['w-5']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-500']} */ ;
/** @type {__VLS_StyleScopedClasses['opacity-25']} */ ;
/** @type {__VLS_StyleScopedClasses['opacity-75']} */ ;
/** @type {__VLS_StyleScopedClasses['divide-y']} */ ;
/** @type {__VLS_StyleScopedClasses['divide-gray-200']} */ ;
/** @type {__VLS_StyleScopedClasses['px-6']} */ ;
/** @type {__VLS_StyleScopedClasses['py-4']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-between']} */ ;
/** @type {__VLS_StyleScopedClasses['flex-1']} */ ;
/** @type {__VLS_StyleScopedClasses['min-w-0']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['space-x-3']} */ ;
/** @type {__VLS_StyleScopedClasses['flex-shrink-0']} */ ;
/** @type {__VLS_StyleScopedClasses['w-2.5']} */ ;
/** @type {__VLS_StyleScopedClasses['h-2.5']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-full']} */ ;
/** @type {__VLS_StyleScopedClasses['flex-1']} */ ;
/** @type {__VLS_StyleScopedClasses['min-w-0']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-900']} */ ;
/** @type {__VLS_StyleScopedClasses['truncate']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-500']} */ ;
/** @type {__VLS_StyleScopedClasses['truncate']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['space-x-2']} */ ;
/** @type {__VLS_StyleScopedClasses['inline-flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2.5']} */ ;
/** @type {__VLS_StyleScopedClasses['py-0.5']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-full']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['space-x-1']} */ ;
/** @type {__VLS_StyleScopedClasses['p-1']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-400']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:text-gray-600']} */ ;
/** @type {__VLS_StyleScopedClasses['h-4']} */ ;
/** @type {__VLS_StyleScopedClasses['w-4']} */ ;
/** @type {__VLS_StyleScopedClasses['p-1']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-400']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:text-gray-600']} */ ;
/** @type {__VLS_StyleScopedClasses['h-4']} */ ;
/** @type {__VLS_StyleScopedClasses['w-4']} */ ;
/** @type {__VLS_StyleScopedClasses['p-1']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-400']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:text-red-600']} */ ;
/** @type {__VLS_StyleScopedClasses['h-4']} */ ;
/** @type {__VLS_StyleScopedClasses['w-4']} */ ;
/** @type {__VLS_StyleScopedClasses['px-6']} */ ;
/** @type {__VLS_StyleScopedClasses['py-12']} */ ;
/** @type {__VLS_StyleScopedClasses['text-center']} */ ;
/** @type {__VLS_StyleScopedClasses['mx-auto']} */ ;
/** @type {__VLS_StyleScopedClasses['h-12']} */ ;
/** @type {__VLS_StyleScopedClasses['w-12']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-400']} */ ;
/** @type {__VLS_StyleScopedClasses['mt-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-900']} */ ;
/** @type {__VLS_StyleScopedClasses['mt-1']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-500']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup: () => ({
        PlusIcon: PlusIcon,
        CubeIcon: CubeIcon,
        CheckCircleIcon: CheckCircleIcon,
        XCircleIcon: XCircleIcon,
        PencilIcon: PencilIcon,
        TrashIcon: TrashIcon,
        EyeIcon: EyeIcon,
        EyeSlashIcon: EyeSlashIcon,
        ArrowPathIcon: ArrowPathIcon,
        ItemModal: ItemModal,
        ConfirmModal: ConfirmModal,
        showCreateModal: showCreateModal,
        editingItem: editingItem,
        itemToDelete: itemToDelete,
        statusFilter: statusFilter,
        searchQuery: searchQuery,
        items: items,
        loading: loading,
        activeItems: activeItems,
        inactiveItems: inactiveItems,
        filteredItems: filteredItems,
        editItem: editItem,
        closeModal: closeModal,
        handleSave: handleSave,
        toggleStatus: toggleStatus,
        confirmDelete: confirmDelete,
        handleDelete: handleDelete,
        loadItems: loadItems,
    }),
});
export default (await import('vue')).defineComponent({});
; /* PartiallyEnd: #4569/main.vue */
