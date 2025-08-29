<template>
  <section id="pricing" class="pricing">
    <div class="container">
      <div class="section-header">
        <h2>Future Pricing Plans</h2>
        <p>Planned pricing structure for when TruLedgr launches. Subject to change.</p>
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
            <li v-for="feature in plan.features" :key="feature.text" :class="{ disabled: !feature.enabled }">
              <i :class="feature.enabled ? 'fas fa-check' : 'fas fa-times'" aria-hidden="true"></i>
              <span class="feature-text" :aria-disabled="!feature.enabled">{{ feature.text }}</span>
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
  features: { text: string; enabled?: boolean }[]
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
  price: 1,
    features: [
      { text: "1 financial account", enabled: true },
      { text: "Automated imports via Plaid", enabled: false },
      { text: "Manual transaction imports", enabled: true },
      { text: "Basic reporting", enabled: true },
      { text: "Community support", enabled: true },
    ],
    link: "#notify",
    buttonText: "Get Notified",
    buttonClass: "btn btn-outline"
  },
    {
      id: 2,
      name: "Basic",
    price: 5,
      features: [
        { text: "Up to 3 financial accounts", enabled: true },
        { text: "Automated imports via Plaid", enabled: true },
        { text: "Manual transaction imports", enabled: true },
        { text: "Daily transaction sync", enabled: true },
        { text: "Standard reporting", enabled: true },
        { text: "Email support", enabled: true },
      ],
      link: "#notify",
      buttonText: "Get Notified",
      buttonClass: "btn btn-primary"
    },
    {
      id: 3,
      name: "Pro",
    price: 10,
      features: [
        { text: "Up to 10 financial accounts", enabled: true },
        { text: "Automated imports via Plaid", enabled: true },
        { text: "Manual transaction imports", enabled: true },
        { text: "Near real-time sync", enabled: true },
        { text: "Advanced reporting & exports", enabled: true },
        { text: "Priority support", enabled: true },
      ],
      link: "#notify",
      buttonText: "Get Notified",
      buttonClass: "btn btn-primary",
      featured: true,
      badge: "Most Popular"
    },
    {
      id: 4,
      name: "Pro Plus",
    price: 15,
      features: [
        { text: "Up to 20 financial accounts", enabled: true },
        { text: "Automated imports via Plaid", enabled: true },
        { text: "Manual transaction imports", enabled: true },
        { text: "Priority sync & dedicated support", enabled: true },
        { text: "Advanced team features (coming soon)", enabled: true },
        { text: "Custom exports", enabled: true },
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

<style scoped>
.pricing-features li.disabled .feature-text {
  text-decoration: line-through;
  opacity: 0.65;
}
.pricing-features li.disabled i {
  color: var(--text-muted);
}
</style>
