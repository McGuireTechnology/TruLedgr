import { apiClient } from './api'
import type { Item, ItemCreate, ItemUpdate } from '@/types'

export const itemsApi = {
  // Get all items
  getItems: async (): Promise<Item[]> => {
    const response = await apiClient.get<Item[]>('/items/')
    return response.data
  },

  // Get a single item by ID
  getItem: async (id: number): Promise<Item> => {
    const response = await apiClient.get<Item>(`/items/${id}`)
    return response.data
  },

  // Create a new item
  createItem: async (item: ItemCreate): Promise<Item> => {
    const response = await apiClient.post<Item>('/items/', item)
    return response.data
  },

  // Update an existing item
  updateItem: async (id: number, item: ItemUpdate): Promise<Item> => {
    const response = await apiClient.patch<Item>(`/items/${id}`, item)
    return response.data
  },

  // Delete an item
  deleteItem: async (id: number): Promise<void> => {
    await apiClient.delete(`/items/${id}`)
  },
}

export { type Item, type ItemCreate, type ItemUpdate }
