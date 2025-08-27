<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="sm:flex sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Items Management</h1>
        <p class="mt-2 text-sm text-gray-700">
          Manage your application items and their properties.
        </p>
      </div>
      <div class="mt-4 sm:mt-0 flex space-x-3">
        <button
          @click="loadItems(true)"
          type="button"
          class="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          :disabled="loading"
        >
          <ArrowPathIcon class="-ml-1 mr-2 h-4 w-4" :class="{ 'animate-spin': loading }" aria-hidden="true" />
          Refresh
        </button>
        <button
          @click="showCreateModal = true"
          type="button"
          class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          <PlusIcon class="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
          New Item
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <CubeIcon class="h-6 w-6 text-gray-400" aria-hidden="true" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Total Items</dt>
                <dd class="text-lg font-medium text-gray-900">{{ items.length }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <CheckCircleIcon class="h-6 w-6 text-green-400" aria-hidden="true" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Active Items</dt>
                <dd class="text-lg font-medium text-gray-900">{{ activeItems.length }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <XCircleIcon class="h-6 w-6 text-red-400" aria-hidden="true" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Inactive Items</dt>
                <dd class="text-lg font-medium text-gray-900">{{ inactiveItems.length }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white shadow rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <div class="sm:flex sm:items-center sm:justify-between">
          <div class="flex space-x-4">
            <div>
              <label for="status-filter" class="block text-sm font-medium text-gray-700">Status</label>
              <select
                id="status-filter"
                v-model="statusFilter"
                class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
              >
                <option value="all">All Items</option>
                <option value="active">Active Only</option>
                <option value="inactive">Inactive Only</option>
              </select>
            </div>
            <div>
              <label for="search" class="block text-sm font-medium text-gray-700">Search</label>
              <input
                id="search"
                v-model="searchQuery"
                type="text"
                placeholder="Search items..."
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Items Table -->
    <div class="bg-white shadow overflow-hidden sm:rounded-md">
      <div v-if="loading" class="p-6 text-center">
        <div class="inline-flex items-center">
          <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Loading items...
        </div>
      </div>

      <ul v-else-if="filteredItems.length > 0" role="list" class="divide-y divide-gray-200">
        <li v-for="item in filteredItems" :key="item.id" class="px-6 py-4">
          <div class="flex items-center justify-between">
            <div class="flex-1 min-w-0">
              <div class="flex items-center space-x-3">
                <div 
                  :class="[
                    'flex-shrink-0 w-2.5 h-2.5 rounded-full',
                    item.is_active ? 'bg-green-400' : 'bg-red-400'
                  ]"
                ></div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-gray-900 truncate">
                    {{ item.name }}
                  </p>
                  <p v-if="item.description" class="text-sm text-gray-500 truncate">
                    {{ item.description }}
                  </p>
                </div>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <span 
                :class="[
                  'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                  item.is_active 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                ]"
              >
                {{ item.is_active ? 'Active' : 'Inactive' }}
              </span>
              <div class="flex space-x-1">
                <button
                  @click="editItem(item)"
                  class="p-1 text-gray-400 hover:text-gray-600"
                  title="Edit item"
                >
                  <PencilIcon class="h-4 w-4" />
                </button>
                <button
                  @click="toggleStatus(item)"
                  class="p-1 text-gray-400 hover:text-gray-600"
                  :title="item.is_active ? 'Deactivate item' : 'Activate item'"
                >
                  <component :is="item.is_active ? EyeSlashIcon : EyeIcon" class="h-4 w-4" />
                </button>
                <button
                  @click="confirmDelete(item)"
                  class="p-1 text-gray-400 hover:text-red-600"
                  title="Delete item"
                >
                  <TrashIcon class="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        </li>
      </ul>

      <div v-else class="px-6 py-12 text-center">
        <CubeIcon class="mx-auto h-12 w-12 text-gray-400" />
        <h3 class="mt-2 text-sm font-medium text-gray-900">No items found</h3>
        <p class="mt-1 text-sm text-gray-500">
          {{ searchQuery || statusFilter !== 'all' ? 'Try adjusting your filters.' : 'Get started by creating a new item.' }}
        </p>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <ItemModal 
      v-if="showCreateModal || editingItem"
      :item="editingItem"
      @close="closeModal"
      @save="handleSave"
    />

    <!-- Delete Confirmation Modal -->
    <ConfirmModal
      v-if="itemToDelete"
      title="Delete Item"
      :message="`Are you sure you want to delete '${itemToDelete.name}'? This action cannot be undone.`"
      confirm-text="Delete"
      confirm-class="bg-red-600 hover:bg-red-700 focus:ring-red-500"
      @confirm="handleDelete"
      @cancel="itemToDelete = null"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useItemsStore } from '@/stores/items'
import { useToast } from 'vue-toastification'
import type { Item, ItemCreate, ItemUpdate } from '@/services/items'
import {
  PlusIcon,
  CubeIcon,
  CheckCircleIcon,
  XCircleIcon,
  PencilIcon,
  TrashIcon,
  EyeIcon,
  EyeSlashIcon,
  ArrowPathIcon,
} from '@heroicons/vue/24/outline'
import ItemModal from './ItemModal.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'

const itemsStore = useItemsStore()
const toast = useToast()

// Reactive data
const showCreateModal = ref(false)
const editingItem = ref<Item | null>(null)
const itemToDelete = ref<Item | null>(null)
const statusFilter = ref('all')
const searchQuery = ref('')

// Computed
const items = computed(() => itemsStore.items)
const loading = computed(() => itemsStore.loading)
const activeItems = computed(() => itemsStore.activeItems)
const inactiveItems = computed(() => itemsStore.inactiveItems)
const filteredItems = computed(() => {
  let filtered = items.value

  // Apply status filter
  if (statusFilter.value === 'active') {
    filtered = activeItems.value
  } else if (statusFilter.value === 'inactive') {
    filtered = inactiveItems.value
  }

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(
      (item) =>
        item.name.toLowerCase().includes(query) ||
        (item.description && item.description.toLowerCase().includes(query))
    )
  }

  return filtered
})

// Methods
const editItem = (item: Item) => {
  editingItem.value = { ...item }
}

const closeModal = () => {
  showCreateModal.value = false
  editingItem.value = null
}

const handleSave = async (itemData: ItemCreate | ItemUpdate) => {
  try {
    if (editingItem.value) {
      // Update existing item
      await itemsStore.updateItem(editingItem.value.id, itemData as ItemUpdate)
      toast.success('Item updated successfully!')
    } else {
      // Create new item
      await itemsStore.createItem(itemData as ItemCreate)
      toast.success('Item created successfully!')
    }
    closeModal()
  } catch (error) {
    toast.error('Failed to save item')
  }
}

const toggleStatus = async (item: Item) => {
  try {
    await itemsStore.toggleItemStatus(item.id)
    toast.success(`Item ${item.is_active ? 'deactivated' : 'activated'} successfully!`)
  } catch (error) {
    toast.error('Failed to update item status')
  }
}

const confirmDelete = (item: Item) => {
  itemToDelete.value = item
}

const handleDelete = async () => {
  if (!itemToDelete.value) return
  
  try {
    await itemsStore.deleteItem(itemToDelete.value.id)
    toast.success('Item deleted successfully!')
    itemToDelete.value = null
  } catch (error) {
    toast.error('Failed to delete item')
  }
}

// Initialize
const loadItems = async (force = false) => {
  try {
    console.log('Loading items..., force:', force)
    await itemsStore.fetchItems(force)
    console.log('Items loaded successfully:', itemsStore.items.length)
  } catch (error) {
    console.error('Failed to load items:', error)
    toast.error('Failed to load items')
  }
}

onMounted(async () => {
  console.log('ItemsView mounted, loading items...')
  await loadItems(true) // Force load on mount
})
</script>
