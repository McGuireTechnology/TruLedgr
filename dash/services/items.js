import { apiClient } from './api';
export const itemsApi = {
    // Get all items
    getItems: async () => {
        const response = await apiClient.get('/items/');
        return response.data;
    },
    // Get a single item by ID
    getItem: async (id) => {
        const response = await apiClient.get(`/items/${id}`);
        return response.data;
    },
    // Create a new item
    createItem: async (item) => {
        const response = await apiClient.post('/items/', item);
        return response.data;
    },
    // Update an existing item
    updateItem: async (id, item) => {
        const response = await apiClient.patch(`/items/${id}`, item);
        return response.data;
    },
    // Delete an item
    deleteItem: async (id) => {
        await apiClient.delete(`/items/${id}`);
    },
};
export {};
