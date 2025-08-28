<script setup lang="ts">
import { RouterView } from 'vue-router'
import NavBar from '@/components/NavBar.vue'
</script>

<template>
  <div class="app">
    <NavBar />
    <RouterView />
  </div>
</template>

<style>
@import '@/assets/main.css';
</style>
