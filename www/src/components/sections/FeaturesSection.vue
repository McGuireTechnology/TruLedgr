<template>
  <section id="features" class="features">
    <div class="container">
      <div class="section-header">
        <h2>Why Choose TruLedgr?</h2>
        <p>Everything you need to manage your finances, all in one platform</p>
      </div>
      <div class="features-grid">
        <div v-for="feature in features" :key="feature.id" class="feature-card">
          <div class="feature-icon">
            <i :class="feature.icon"></i>
          </div>
          <h3>{{ feature.title }}</h3>
          <p>{{ feature.description }}</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
interface Feature {
  id: number
  title: string
  description: string
  icon: string
}

const features: Feature[] = [
  {
    id: 1,
    title: "Lightning Fast",
    description: "Built with FastAPI for maximum performance. Sub-second response times guaranteed.",
    icon: "fas fa-tachometer-alt"
  },
  {
    id: 2,
    title: "Bank-Level Security",
    description: "JWT authentication, encrypted data, and biometric support for ultimate security.",
    icon: "fas fa-shield-alt"
  },
  {
    id: 3,
    title: "Mobile First",
    description: "Native iOS and Android apps with offline capabilities and real-time sync.",
    icon: "fas fa-mobile-alt"
  },
  {
    id: 4,
    title: "Cloud Native",
    description: "Deployed on Digital Ocean with auto-scaling and 99.9% uptime guarantee.",
    icon: "fas fa-cloud"
  },
  {
    id: 5,
    title: "Advanced Analytics",
    description: "Real-time insights, custom reports, and predictive analytics powered by AI.",
    icon: "fas fa-chart-bar"
  },
  {
    id: 6,
    title: "Developer API",
    description: "RESTful API with comprehensive documentation for seamless integrations.",
    icon: "fas fa-code"
  }
]
</script>

<style scoped>
/* Features section styles are in main.css */
</style>
