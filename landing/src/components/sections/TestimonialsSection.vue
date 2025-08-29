<template>
  <section class="testimonials">
    <div class="container">
      <div class="section-header">
        <h2>Development Updates</h2>
        <p>Follow our progress as we build TruLedgr</p>
      </div>
      <div class="testimonials-grid">
        <div v-for="update in updates" :key="update.id" class="testimonial-card">
          <div class="testimonial-content">{{ update.content }}</div>
          <div class="testimonial-author">
            <div class="author-avatar">
              <i class="fas fa-code"></i>
            </div>
            <div class="author-info">
              <div class="author-name">{{ update.milestone }}</div>
              <div class="author-title">{{ update.status }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
interface Update {
  id: number
  content: string
  milestone: string
  status: string
}

const updates: Update[] = [
  {
    id: 1,
    content: "Core backend architecture completed with FastAPI. Authentication system and database models finalized.",
    milestone: "Backend Foundation",
    status: "Completed Q4 2024"
  },
  {
    id: 2,
    content: "Vue.js dashboard framework established. Component library and routing structure implemented.",
    milestone: "Frontend Framework",
    status: "Completed Q4 2024"
  },
  {
    id: 3,
    content: "Mobile app development in progress. iOS and Android native apps with offline-first architecture.",
    milestone: "Mobile Applications",
    status: "In Development"
  }
]
</script>

<style scoped>
/* Testimonials section styles are in main.css */
</style>
