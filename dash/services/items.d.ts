import type { Item, ItemCreate, ItemUpdate } from '@/types';
export declare const itemsApi: {
    getItems: () => Promise<Item[]>;
    getItem: (id: number) => Promise<Item>;
    createItem: (item: ItemCreate) => Promise<Item>;
    updateItem: (id: number, item: ItemUpdate) => Promise<Item>;
    deleteItem: (id: number) => Promise<void>;
};
export { type Item, type ItemCreate, type ItemUpdate };
