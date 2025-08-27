<template>
  <div class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="$emit('close')"></div>

      <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
        <form @submit.prevent="handleSubmit">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">
                  Edit User
                </h3>
                
                <div class="space-y-4">
                  <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div>
                      <label for="username" class="block text-sm font-medium text-gray-700">Username</label>
                      <input
                        id="username"
                        v-model="form.username"
                        type="text"
                        class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                      />
                    </div>
                    <div>
                      <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
                      <input
                        id="email"
                        v-model="form.email"
                        type="email"
                        class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                      />
                    </div>
                  </div>
                  
                  <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div>
                      <label for="first_name" class="block text-sm font-medium text-gray-700">First Name</label>
                      <input
                        id="first_name"
                        v-model="form.first_name"
                        type="text"
                        class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                      />
                    </div>
                    <div>
                      <label for="last_name" class="block text-sm font-medium text-gray-700">Last Name</label>
                      <input
                        id="last_name"
                        v-model="form.last_name"
                        type="text"
                        class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                      />
                    </div>
                  </div>
                  
                  <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div class="flex items-center">
                      <input
                        id="is_active"
                        v-model="form.is_active"
                        type="checkbox"
                        class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      />
                      <label for="is_active" class="ml-2 block text-sm text-gray-900">
                        Active
                      </label>
                    </div>
                    <div class="flex items-center">
                      <input
                        id="is_verified"
                        v-model="form.is_verified"
                        type="checkbox"
                        class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      />
                      <label for="is_verified" class="ml-2 block text-sm text-gray-900">
                        Verified
                      </label>
                    </div>
                  </div>
                </div>

                <div v-if="error" class="mt-4 rounded-md bg-red-50 p-4">
                  <p class="text-sm text-red-800">{{ error }}</p>
                </div>
              </div>
            </div>
          </div>
          
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button
              type="submit"
              :disabled="loading"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-primary-600 text-base font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50"
            >
              {{ loading ? 'Updating...' : 'Update User' }}
            </button>
            <button
              type="button"
              @click="$emit('close')"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiClient } from '@/services/api'
import type { User, UserUpdate } from '@/types'

interface Props {
  user: User
}

const props = defineProps<Props>()
const emit = defineEmits(['close', 'updated'])

const loading = ref(false)
const error = ref('')

const form = ref<UserUpdate>({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  is_active: true,
  is_verified: false
})

const handleSubmit = async () => {
  loading.value = true
  error.value = ''
  
  try {
    await apiClient.put(`/users/${props.user.id}`, form.value)
    emit('updated')
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to update user'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // Pre-populate form with user data
  form.value = {
    username: props.user.username,
    email: props.user.email,
    first_name: props.user.first_name || '',
    last_name: props.user.last_name || '',
    is_active: props.user.is_active,
    is_verified: props.user.is_verified
  }
})
</script>
