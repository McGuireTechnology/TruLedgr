<template>
  <section id="pricing" class="pricing">
    <div class="container">
      <div class="section-header">
        <h2>Simple, Transparent Pricing</h2>
        <p>Choose the plan that fits your needs. Always fair, always transparent.</p>
      </div>
      <div class="pricing-grid">
        <div v-for="plan in pricingPlans" :key="plan.id" 
             class="pricing-card" 
             :class="{ featured: plan.featured }">
          <div v-if="plan.badge" class="pricing-badge">{{ plan.badge }}</div>
          <div class="pricing-header">
            <h3>{{ plan.name }}</h3>
            <div class="price">
              <span class="currency">$</span>
              <span class="amount">{{ plan.price }}</span>
              <span class="period">/month</span>
            </div>
          </div>
          <ul class="pricing-features">
            <li v-for="feature in plan.features" :key="feature">
              <i class="fas fa-check"></i>{{ feature }}
            </li>
          </ul>
          <a :href="plan.link" :class="plan.buttonClass">{{ plan.buttonText }}</a>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
interface PricingPlan {
  id: number
  name: string
  price: number
  features: string[]
  link: string
  buttonText: string
  buttonClass: string
  featured?: boolean
  badge?: string
}

const pricingPlans: PricingPlan[] = [
  {
    id: 1,
    name: "Starter",
    price: 0,
    features: [
      "Up to 100 transactions",
      "Basic reporting",
      "Mobile apps",
      "Email support"
    ],
    link: "https://dash.truledgr.app/signup?plan=starter",
    buttonText: "Get Started",
    buttonClass: "btn btn-outline"
  },
  {
    id: 2,
    name: "Professional",
    price: 29,
    features: [
      "Unlimited transactions",
      "Advanced analytics",
      "API access",
      "Priority support",
      "Custom integrations"
    ],
    link: "https://dash.truledgr.app/signup?plan=pro",
    buttonText: "Start Free Trial",
    buttonClass: "btn btn-primary",
    featured: true,
    badge: "Most Popular"
  },
  {
    id: 3,
    name: "Enterprise",
    price: 99,
    features: [
      "Everything in Pro",
      "White-label options",
      "Dedicated support",
      "Custom development",
      "SLA guarantee"
    ],
    link: "mailto:sales@truledgr.app",
    buttonText: "Contact Sales",
    buttonClass: "btn btn-outline"
  }
]
</script>

<style scoped>
/* Pricing section styles are in main.css */
</style>
