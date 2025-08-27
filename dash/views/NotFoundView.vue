<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div class="text-center">
        <h2 class="mt-6 text-9xl font-bold text-gray-900">404</h2>
        <p class="mt-2 text-lg font-medium text-gray-900">Page not found</p>
        <p class="mt-1 text-sm text-gray-600">
          Sorry, we couldn't find the page you're looking for.
        </p>
      </div>
      <div class="text-center">
        <router-link
          to="/"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          Go back home
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// No additional logic needed for 404 page
</script>
