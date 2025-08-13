<template>
  <section id="platforms" class="platforms">
    <div class="container">
      <div class="section-header">
        <h2>Multi-Platform Excellence</h2>
        <p>Access your financial data anywhere, anytime, on any device</p>
      </div>
      <div class="platforms-grid">
        <div v-for="platform in platforms" :key="platform.id" class="platform-card">
          <div class="platform-icon">
            <i :class="platform.icon"></i>
          </div>
          <h3>{{ platform.title }}</h3>
          <p>{{ platform.description }}</p>
          <a :href="platform.link" class="platform-link">
            {{ platform.linkText }} <i class="fas fa-arrow-right"></i>
          </a>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
interface Platform {
  id: number
  title: string
  description: string
  icon: string
  link: string
  linkText: string
}

const platforms: Platform[] = [
  {
    id: 1,
    title: "Web Dashboard",
    description: "Powerful Vue.js dashboard with real-time updates and advanced features",
    icon: "fas fa-desktop",
    link: "https://dash.truledgr.app",
    linkText: "Visit Dashboard"
  },
  {
    id: 2,
    title: "iOS App",
    description: "Native Swift app with Touch ID, Face ID, and offline-first architecture",
    icon: "fab fa-apple",
    link: "#",
    linkText: "App Store"
  },
  {
    id: 3,
    title: "Android App",
    description: "Material Design app with fingerprint auth and seamless sync",
    icon: "fab fa-android",
    link: "#",
    linkText: "Google Play"
  },
  {
    id: 4,
    title: "Developer API",
    description: "RESTful API with OpenAPI documentation and SDKs",
    icon: "fas fa-code",
    link: "https://api.truledgr.app",
    linkText: "API Docs"
  }
]
</script>

<style scoped>
/* Platforms section styles are in main.css */
</style>
