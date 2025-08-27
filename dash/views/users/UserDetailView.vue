<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="border-b border-gray-200 pb-6">
      <h1 class="text-2xl font-bold text-gray-900">User Details</h1>
      <p class="mt-1 text-sm text-gray-600">
        View and manage user information
      </p>
    </div>

    <!-- Coming Soon -->
    <div class="text-center py-12">
      <div class="max-w-md mx-auto">
        <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-primary-100">
          <UsersIcon class="h-6 w-6 text-primary-600" />
        </div>
        <h3 class="mt-4 text-lg font-medium text-gray-900">User Detail View</h3>
        <p class="mt-2 text-sm text-gray-500">
          This feature is coming soon. You'll be able to view detailed user information here.
        </p>
        <div class="mt-4">
          <router-link
            to="/users"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
          >
            Back to Users
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { UsersIcon } from '@heroicons/vue/24/outline'
</script>
