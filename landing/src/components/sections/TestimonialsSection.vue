<template>
  <section class="testimonials">
    <div class="container">
      <div class="section-header">
        <h2>Trusted by Thousands</h2>
        <p>See what our customers have to say about TruLedgr</p>
      </div>
      <div class="testimonials-grid">
        <div v-for="testimonial in testimonials" :key="testimonial.id" class="testimonial-card">
          <div class="testimonial-content">{{ testimonial.content }}</div>
          <div class="testimonial-author">
            <div class="author-avatar">
              <i class="fas fa-user"></i>
            </div>
            <div class="author-info">
              <div class="author-name">{{ testimonial.author.name }}</div>
              <div class="author-title">{{ testimonial.author.title }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
interface Testimonial {
  id: number
  content: string
  author: {
    name: string
    title: string
  }
}

const testimonials: Testimonial[] = [
  {
    id: 1,
    content: "TruLedgr transformed our financial workflow. The mobile app is incredible and the API integration was seamless.",
    author: {
      name: "Sarah Chen",
      title: "CFO, TechStart Inc."
    }
  },
  {
    id: 2,
    content: "The best financial management platform we've used. Fast, secure, and the support team is outstanding.",
    author: {
      name: "Michael Rodriguez",
      title: "Founder, GrowthCo"
    }
  },
  {
    id: 3,
    content: "TruLedgr's analytics helped us identify cost savings worth $50k in the first quarter alone.",
    author: {
      name: "Emily Johnson",
      title: "Finance Director, Scale LLC"
    }
  }
]
</script>

<style scoped>
/* Testimonials section styles are in main.css */
</style>
