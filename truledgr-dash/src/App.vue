<template>
  <div class="app">
    <header class="site-header">
      <h1>TruLedgr Dashboard</h1>
      <small>Example Vue + Vite starter</small>
    </header>

    <main>
      <Dashboard />
    </main>

    <footer>
      <small>TruLedgr — internal dashboard sample</small>
    </footer>
  </div>
</template>

<script setup lang="ts">
import Dashboard from './components/Dashboard.vue'
</script>

<style scoped>
.app {
  max-width: 900px;
  margin: 32px auto;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
  color: #111827;
}
.site-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}
main {
  margin-top: 20px;
}
</style>
