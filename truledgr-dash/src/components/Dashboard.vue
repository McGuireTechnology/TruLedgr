<template>
  <section class="dashboard">
    <h2>Service status</h2>
    <p v-if="loading">Checking API health…</p>
    <p v-else-if="error" class="error">Error: {{ error }}</p>
    <p v-else class="healthy">API status: <strong>{{ status }}</strong></p>

    <hr />

    <h3>Quick actions</h3>
    <div class="actions">
      <button @click="refresh">Refresh status</button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const loading = ref(true)
const status = ref('unknown')
const error = ref('')

async function fetchHealth() {
  loading.value = true
  error.value = ''
  try {
    const res = await fetch('/api/health')
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
    const json = await res.json()
    status.value = json.status ?? 'ok'
  } catch (err: any) {
    error.value = err.message || String(err)
    status.value = 'unreachable'
  } finally {
    loading.value = false
  }
}

function refresh() {
  fetchHealth()
}

fetchHealth()
</script>

<style scoped>
.dashboard {
  border: 1px solid #e5e7eb;
  padding: 16px;
  border-radius: 8px;
}
.error { color: #b91c1c }
.healthy { color: #065f46 }
.actions { margin-top: 8px }
button { padding: 8px 12px; border-radius: 6px }
</style>
