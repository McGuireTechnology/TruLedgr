import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { itemsApi } from '@/services/items';
export const useItemsStore = defineStore('items', () => {
    const items = ref([]);
    const loading = ref(false);
    const error = ref(null);
    const activeItems = computed(() => items.value.filter(item => item.is_active));
    const inactiveItems = computed(() => items.value.filter(item => !item.is_active));
    // Fetch all items
    const fetchItems = async (force = false) => {
        console.log('fetchItems called, force:', force, 'loading:', loading.value, 'items length:', items.value.length);
        // Don't fetch if already loading or if we already have items and it's not forced
        if (loading.value || (!force && items.value.length > 0)) {
            console.log('Skipping fetch - already loading or have items');
            return items.value;
        }
        loading.value = true;
        error.value = null;
        console.log('Starting API request for items...');
        try {
            const data = await itemsApi.getItems();
            console.log('API response received:', data);
            items.value = data;
            return data;
        }
        catch (err) {
            console.error('API request failed:', err);
            error.value = err.response?.data?.detail || 'Failed to fetch items';
            throw err;
        }
        finally {
            loading.value = false;
            console.log('fetchItems completed');
        }
    };
    // Create new item
    const createItem = async (itemData) => {
        loading.value = true;
        error.value = null;
        try {
            const newItem = await itemsApi.createItem(itemData);
            items.value.push(newItem);
            return newItem;
        }
        catch (err) {
            error.value = err.response?.data?.detail || 'Failed to create item';
            throw err;
        }
        finally {
            loading.value = false;
        }
    };
    // Update item
    const updateItem = async (id, itemData) => {
        loading.value = true;
        error.value = null;
        try {
            const updatedItem = await itemsApi.updateItem(id, itemData);
            const index = items.value.findIndex(item => item.id === id);
            if (index !== -1) {
                items.value[index] = updatedItem;
            }
            return updatedItem;
        }
        catch (err) {
            error.value = err.response?.data?.detail || 'Failed to update item';
            throw err;
        }
        finally {
            loading.value = false;
        }
    };
    // Delete item
    const deleteItem = async (id) => {
        loading.value = true;
        error.value = null;
        try {
            await itemsApi.deleteItem(id);
            items.value = items.value.filter(item => item.id !== id);
        }
        catch (err) {
            error.value = err.response?.data?.detail || 'Failed to delete item';
            throw err;
        }
        finally {
            loading.value = false;
        }
    };
    // Toggle item status
    const toggleItemStatus = async (id) => {
        const item = items.value.find(item => item.id === id);
        if (item) {
            await updateItem(id, { is_active: !item.is_active });
        }
    };
    // Clear error
    const clearError = () => {
        error.value = null;
    };
    return {
        items,
        loading,
        error,
        activeItems,
        inactiveItems,
        fetchItems,
        createItem,
        updateItem,
        deleteItem,
        toggleItemStatus,
        clearError,
    };
});
