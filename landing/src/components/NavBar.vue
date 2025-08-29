<template>
  <nav class="navbar" :class="{ scrolled: isScrolled }">
    <div class="nav-container">
      <div class="nav-brand">
        <div class="nav-logo">
          <i class="fas fa-chart-line"></i>
        </div>
        <span class="nav-title">TruLedgr</span>
      </div>
      <div class="nav-menu" :class="{ active: isMenuOpen }" id="nav-menu">
        <a href="#features" class="nav-link" @click="closeMenu">Features</a>
        <a href="#platforms" class="nav-link" @click="closeMenu">Platforms</a>
        <a href="#pricing" class="nav-link" @click="closeMenu">Pricing</a>
        <a href="#contact" class="nav-link" @click="closeMenu">Contact</a>
        <a href="mailto:earlyaccess@truledgr.app" class="nav-link nav-cta">Early Access</a>
      </div>
      <div class="nav-toggle" :class="{ active: isMenuOpen }" @click="toggleMenu">
        <span class="bar"></span>
        <span class="bar"></span>
        <span class="bar"></span>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const isScrolled = ref(false)
const isMenuOpen = ref(false)

const handleScroll = () => {
  isScrolled.value = window.scrollY > 50
}

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}

const closeMenu = () => {
  isMenuOpen.value = false
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
/* Navigation styles are in main.css */
</style>
