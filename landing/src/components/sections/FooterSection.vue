<template>
  <footer id="contact" class="footer">
    <div class="container">
      <div class="footer-content">
        <div class="footer-section">
          <div class="footer-brand">
            <div class="footer-logo">
              <i class="fas fa-chart-line"></i>
            </div>
            <span class="footer-title">TruLedgr</span>
          </div>
          <p class="footer-description">
            Modern financial management platform built for the cloud-native era.
          </p>
          <div class="footer-social">
            <a href="https://github.com/McGuireTechnology" aria-label="GitHub">
              <i class="fab fa-github"></i>
            </a>
            <a href="#" aria-label="Twitter">
              <i class="fab fa-twitter"></i>
            </a>
            <a href="#" aria-label="LinkedIn">
              <i class="fab fa-linkedin"></i>
            </a>
          </div>
        </div>
        
        <div v-for="section in footerSections" :key="section.title" class="footer-section">
          <h4>{{ section.title }}</h4>
          <a v-for="link in section.links" :key="link.text" :href="link.url">{{ link.text }}</a>
        </div>
      </div>
      
      <div class="footer-bottom">
        <p>&copy; 2025 McGuire Technology. All rights reserved.</p>
        <div class="footer-links">
          <a href="#privacy">Privacy</a>
          <a href="#terms">Terms</a>
          <a href="#cookies">Cookies</a>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
interface FooterLink {
  text: string
  url: string
}

interface FooterSection {
  title: string
  links: FooterLink[]
}

const footerSections: FooterSection[] = [
  {
    title: "Product",
    links: [
      { text: "Features", url: "#features" },
      { text: "Pricing", url: "#pricing" },
      { text: "API", url: "https://api.truledgr.app" },
      { text: "Documentation", url: "https://docs.truledgr.app" }
    ]
  },
  {
    title: "Platforms",
    links: [
      { text: "Web Dashboard", url: "https://dash.truledgr.app" },
      { text: "iOS App", url: "#" },
      { text: "Android App", url: "#" },
      { text: "Developer API", url: "https://api.truledgr.app" }
    ]
  },
  {
    title: "Company",
    links: [
      { text: "About", url: "#about" },
      { text: "Careers", url: "#careers" },
      { text: "Blog", url: "#blog" },
      { text: "Contact", url: "mailto:support@truledgr.app" }
    ]
  },
  {
    title: "Resources",
    links: [
      { text: "Documentation", url: "https://docs.truledgr.app" },
      { text: "Support", url: "#support" },
      { text: "Privacy Policy", url: "#privacy" },
      { text: "Terms of Service", url: "#terms" }
    ]
  }
]
</script>

<style scoped>
/* Footer section styles are in main.css */
</style>
