<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
      <div class="mt-3">
        <!-- Header -->
        <div class="flex items-center justify-between pb-4 border-b">
          <h3 class="text-lg font-medium text-gray-900">
            {{ user ? 'Edit User' : 'Create New User' }}
          </h3>
          <button
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600"
          >
            <XMarkIcon class="h-6 w-6" />
          </button>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleSubmit" class="mt-6 space-y-6">
          <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <!-- Username -->
            <div>
              <label for="username" class="block text-sm font-medium text-gray-700">
                Username *
              </label>
              <input
                id="username"
                v-model="form.username"
                type="text"
                required
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                :class="{ 'border-red-300': errors.username }"
              />
              <p v-if="errors.username" class="mt-1 text-sm text-red-600">{{ errors.username }}</p>
            </div>

            <!-- Email -->
            <div>
              <label for="email" class="block text-sm font-medium text-gray-700">
                Email *
              </label>
              <input
                id="email"
                v-model="form.email"
                type="email"
                required
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                :class="{ 'border-red-300': errors.email }"
              />
              <p v-if="errors.email" class="mt-1 text-sm text-red-600">{{ errors.email }}</p>
            </div>

            <!-- First Name -->
            <div>
              <label for="first_name" class="block text-sm font-medium text-gray-700">
                First Name
              </label>
              <input
                id="first_name"
                v-model="form.first_name"
                type="text"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              />
            </div>

            <!-- Last Name -->
            <div>
              <label for="last_name" class="block text-sm font-medium text-gray-700">
                Last Name
              </label>
              <input
                id="last_name"
                v-model="form.last_name"
                type="text"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              />
            </div>

            <!-- Password (only for new users) -->
            <div v-if="!user" class="sm:col-span-2">
              <label for="password" class="block text-sm font-medium text-gray-700">
                Password *
              </label>
              <input
                id="password"
                v-model="form.password"
                type="password"
                required
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                :class="{ 'border-red-300': errors.password }"
              />
              <p v-if="errors.password" class="mt-1 text-sm text-red-600">{{ errors.password }}</p>
            </div>

            <!-- Bio -->
            <div class="sm:col-span-2">
              <label for="bio" class="block text-sm font-medium text-gray-700">
                Bio
              </label>
              <textarea
                id="bio"
                v-model="form.bio"
                rows="3"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                placeholder="Tell us about this user..."
              ></textarea>
            </div>

            <!-- Status Controls (only for editing) -->
            <div v-if="user" class="sm:col-span-2">
              <div class="space-y-4">
                <div class="flex items-center">
                  <input
                    id="is_active"
                    v-model="form.is_active"
                    type="checkbox"
                    class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <label for="is_active" class="ml-2 block text-sm text-gray-900">
                    Account is active
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
                    Email is verified
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- Submit buttons -->
          <div class="flex justify-end space-x-3 pt-6 border-t">
            <button
              type="button"
              @click="$emit('close')"
              class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="loading"
              class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
            >
              <span v-if="loading" class="inline-flex items-center">
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ user ? 'Updating...' : 'Creating...' }}
              </span>
              <span v-else>
                {{ user ? 'Update User' : 'Create User' }}
              </span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import type { User, UserCreate, UserUpdate } from '@/types'

interface Props {
  user?: User | null
}

interface Emits {
  (e: 'close'): void
  (e: 'save', data: UserCreate | UserUpdate): void
}

const props = withDefaults(defineProps<Props>(), {
  user: null
})

const emit = defineEmits<Emits>()

const loading = ref(false)
const errors = ref<Record<string, string>>({})

const form = reactive<UserCreate & UserUpdate>({
  username: '',
  email: '',
  password: '',
  first_name: '',
  last_name: '',
  bio: '',
  is_active: true,
  is_verified: false,
})

// Initialize form with user data if editing
watch(() => props.user, (user) => {
  if (user) {
    form.username = user.username || ''
    form.email = user.email || ''
    form.first_name = user.first_name || ''
    form.last_name = user.last_name || ''
    form.bio = user.bio || ''
    form.is_active = user.is_active
    form.is_verified = user.is_verified
    // Don't set password for existing users
    form.password = ''
  } else {
    // Reset form for new user
    form.username = ''
    form.email = ''
    form.password = ''
    form.first_name = ''
    form.last_name = ''
    form.bio = ''
    form.is_active = true
    form.is_verified = false
  }
  errors.value = {}
}, { immediate: true })

const validateForm = () => {
  errors.value = {}

  if (!form.username.trim()) {
    errors.value.username = 'Username is required'
  }

  if (!form.email.trim()) {
    errors.value.email = 'Email is required'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errors.value.email = 'Please enter a valid email address'
  }

  if (!props.user && !form.password) {
    errors.value.password = 'Password is required for new users'
  } else if (!props.user && form.password.length < 8) {
    errors.value.password = 'Password must be at least 8 characters long'
  }

  return Object.keys(errors.value).length === 0
}

const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }

  loading.value = true

  try {
    const data: UserCreate | UserUpdate = {
      username: form.username,
      email: form.email,
      first_name: form.first_name || undefined,
      last_name: form.last_name || undefined,
      bio: form.bio || undefined,
    }

    if (props.user) {
      // Editing existing user
      const updateData: UserUpdate = {
        ...data,
        is_active: form.is_active,
        is_verified: form.is_verified,
      }
      emit('save', updateData)
    } else {
      // Creating new user
      const createData: UserCreate = {
        ...data,
        password: form.password,
      }
      emit('save', createData)
    }
  } catch (error) {
    console.error('Form submission error:', error)
  } finally {
    loading.value = false
  }
}
</script>
