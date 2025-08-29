import { type Item, type ItemCreate, type ItemUpdate } from '@/services/items';
export declare const useItemsStore: import("pinia").StoreDefinition<"items", Pick<{
    items: import("vue").Ref<{
        id: number;
        name: string;
        description?: string | undefined;
        is_active: boolean;
    }[], Item[] | {
        id: number;
        name: string;
        description?: string | undefined;
        is_active: boolean;
    }[]>;
    loading: import("vue").Ref<boolean, boolean>;
    error: import("vue").Ref<string | null, string | null>;
    activeItems: import("vue").ComputedRef<{
        id: number;
        name: string;
        description?: string | undefined;
        is_active: boolean;
    }[]>;
    inactiveItems: import("vue").ComputedRef<{
        id: number;
        name: string;
        description?: string | undefined;
        is_active: boolean;
    }[]>;
    fetchItems: (force?: boolean) => Promise<Item[]>;
    createItem: (itemData: ItemCreate) => Promise<Item>;
    updateItem: (id: number, itemData: ItemUpdate) => Promise<Item>;
    deleteItem: (id: number) => Promise<void>;
    toggleItemStatus: (id: number) => Promise<void>;
    clearError: () => void;
}, "loading" | "error" | "items">, Pick<{
    items: import("vue").Ref<{
        id: number;
        name: string;
        description?: string | undefined;
        is_active: boolean;
    }[], Item[] | {
        id: number;
        name: string;
        description?: string | undefined;
        is_active: boolean;
    }[]>;
    loading: import("vue").Ref<boolean, boolean>;
    error: import("vue").Ref<string | null, string | null>;
    activeItems: import("vue").ComputedRef<{
        id: number;
        name: string;
        description?: string | undefined;
        is_active: boolean;
    }[]>;
    inactiveItems: import("vue").ComputedRef<{
        id: number;
        name: string;
        description?: string | undefined;
        is_active: boolean;
    }[]>;
    fetchItems: (force?: boolean) => Promise<Item[]>;
    createItem: (itemData: ItemCreate) => Promise<Item>;
    updateItem: (id: number, itemData: ItemUpdate) => Promise<Item>;
    deleteItem: (id: number) => Promise<void>;
    toggleItemStatus: (id: number) => Promise<void>;
    clearError: () => void;
}, "activeItems" | "inactiveItems">, Pick<{
    items: import("vue").Ref<{
        id: number;
        name: string;
        description?: string | undefined;
        is_active: boolean;
    }[], Item[] | {
        id: number;
        name: string;
        description?: string | undefined;
        is_active: boolean;
    }[]>;
    loading: import("vue").Ref<boolean, boolean>;
    error: import("vue").Ref<string | null, string | null>;
    activeItems: import("vue").ComputedRef<{
        id: number;
        name: string;
        description?: string | undefined;
        is_active: boolean;
    }[]>;
    inactiveItems: import("vue").ComputedRef<{
        id: number;
        name: string;
        description?: string | undefined;
        is_active: boolean;
    }[]>;
    fetchItems: (force?: boolean) => Promise<Item[]>;
    createItem: (itemData: ItemCreate) => Promise<Item>;
    updateItem: (id: number, itemData: ItemUpdate) => Promise<Item>;
    deleteItem: (id: number) => Promise<void>;
    toggleItemStatus: (id: number) => Promise<void>;
    clearError: () => void;
}, "clearError" | "fetchItems" | "createItem" | "updateItem" | "deleteItem" | "toggleItemStatus">>;
