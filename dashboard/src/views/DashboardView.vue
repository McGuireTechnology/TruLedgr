<script setup lang="ts">
import { ref } from 'vue'

const message = ref('Welcome to TruLedgr Dashboard')
</script>

<template>
  <div class="dashboard-container">
    <header class="dashboard-header">
      <div class="header-content">
        <h1>🎩 TruLedgr</h1>
        <nav class="header-nav">
          <router-link to="/login" class="nav-link">Log Out</router-link>
        </nav>
      </div>
    </header>

    <main class="dashboard-main">
      <div class="dashboard-content">
        <h2>{{ message }}</h2>
        <p class="subtitle">Your personal finance dashboard</p>
        
        <div class="dashboard-grid">
          <div class="dashboard-card">
            <h3>Accounts</h3>
            <p>Manage your financial accounts</p>
          </div>
          
          <div class="dashboard-card">
            <h3>Transactions</h3>
            <p>Track your spending and income</p>
          </div>
          
          <div class="dashboard-card">
            <h3>Reports</h3>
            <p>View monthly financial reports</p>
          </div>
          
          <div class="dashboard-card">
            <h3>Settings</h3>
            <p>Configure your preferences</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.dashboard-header {
  background-color: #1a73e8;
  color: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

@media (prefers-color-scheme: dark) {
  .dashboard-header {
    background-color: #1557b0;
  }
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h1 {
  font-size: 1.5rem;
  margin: 0;
}

.header-nav {
  display: flex;
  gap: 1rem;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.dashboard-main {
  flex: 1;
  padding: 2rem;
  background-color: #f5f5f5;
}

@media (prefers-color-scheme: dark) {
  .dashboard-main {
    background-color: #121212;
  }
}

.dashboard-content {
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-content h2 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #666;
  margin-bottom: 2rem;
}

@media (prefers-color-scheme: dark) {
  .subtitle {
    color: #999;
  }
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}

.dashboard-card {
  background-color: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.dashboard-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

@media (prefers-color-scheme: dark) {
  .dashboard-card {
    background-color: #2a2a2a;
  }
}

.dashboard-card h3 {
  font-size: 1.25rem;
  margin-bottom: 0.5rem;
}

.dashboard-card p {
  color: #666;
  font-size: 0.9rem;
}

@media (prefers-color-scheme: dark) {
  .dashboard-card p {
    color: #999;
  }
}
</style>
